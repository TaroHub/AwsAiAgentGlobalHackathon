from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from strands_tools import swarm
import json
import re
import asyncio

app = BedrockAgentCoreApp()

def extract_json(message):
    """メッセージからJSON部分を抽出"""
    if isinstance(message, dict):
        if 'content' in message and isinstance(message['content'], list):
            text = message['content'][0].get('text', '')
        else:
            text = str(message)
    else:
        text = str(message)
    
    json_match = re.search(r'```json\s*({.*?})\s*```', text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(1))
    
    try:
        return json.loads(text)
    except:
        return None

async def invoke_async_streaming(payload):
    """マルチエージェント政策システム（ストリーミング対応）"""
    try:
        user_message = payload.get("prompt", "")
        
        if not user_message:
            yield {"type": "error", "data": "プロンプトが必要です"}
            return
        
        yield {"type": "status", "data": "[ステップ1] SVエージェントがエージェント定義を生成中..."}
        
        sv_agent = Agent(
            model="us.anthropic.claude-sonnet-4-20250514-v1:0",
            callback_handler=None,
            system_prompt="""市民意見を分析し、政策検討に必要なエージェントを設計してください。

あなたの役割:
1. 市民意見の内容を分析
2. 必要な政策立案エージェントの数と専門分野を決定（目安: 2-4名）
3. 必要な市民評価エージェントの数と立場を決定（目安: 3-7名）
4. 各エージェントの詳細なsystem_promptを作成

出力形式:
```json
{
  "policy_agents": [
    {"name": "エージェント名", "expertise": "専門分野", "system_prompt": "詳細なプロンプト"},
    ...
  ],
  "citizen_agents": [
    {"name": "名前", "age": 年齢, "profile": "プロフィール", "system_prompt": "評価用プロンプト"},
    ...
  ]
}
```

決定基準:
- 政策立案エージェント: 市民意見の内容に応じて必要な専門家を選定
- 市民評価エージェント: 政策の影響を受ける多様な立場を代表
- system_promptには具体的な指示、評価基準、出力形式を明記
"""
        )
        
        sv_response = ""
        async for event in sv_agent.stream_async(f"市民意見: {user_message}"):
            if "data" in event:
                chunk = event["data"]
                yield {"type": "stream", "step": "sv_agent", "data": chunk}
                sv_response += chunk
        
        agent_defs = extract_json(sv_response)
        
        if not agent_defs:
            yield {"type": "error", "data": "エージェント定義の生成に失敗しました"}
            return
        
        yield {"type": "agent_defs", "data": agent_defs}
        yield {"type": "status", "data": "[ステップ2] Swarmで政策立案エージェントを協調実行中..."}
        
        swarm_agent = Agent(
            model="us.anthropic.claude-sonnet-4-20250514-v1:0",
            tools=[swarm],
            callback_handler=None
        )
        
        swarm_prompt = f"""以下のエージェント定義に基づいてswarmを作成し、市民意見「{user_message}」に対する政策案をJSON形式で作成してください。

エージェント定義:
{json.dumps(agent_defs['policy_agents'], ensure_ascii=False, indent=2)}

出力形式:
```json
{{
  "policy_title": "政策名",
  "summary": "政策概要",
  "problem_analysis": "問題分析",
  "policy_options": [
    {{
      "option_name": "選択肢名",
      "description": "説明",
      "merits": ["メリット1"],
      "demerits": ["デメリット1"]
    }}
  ],
  "recommended_policy": "推奨政策",
  "implementation_plan": "実施計画",
  "expected_effects": "期待効果",
  "risks": "リスク"
}}
```
"""
        
        policy_response = ""
        async for event in swarm_agent.stream_async(swarm_prompt):
            if "data" in event:
                chunk = event["data"]
                yield {"type": "stream", "step": "swarm", "data": chunk}
                policy_response += chunk
        
        policy_json = extract_json(policy_response)
        if not policy_json:
            policy_json = {"raw_text": policy_response}
        
        yield {"type": "policy", "data": policy_json}
        yield {"type": "status", "data": "[ステップ3] 市民評価を実行中..."}
        
        policy_summary = f"""
政策名: {policy_json.get('policy_title', 'N/A')}
概要: {policy_json.get('summary', 'N/A')}
推奨政策: {policy_json.get('recommended_policy', 'N/A')}
"""
        
        citizen_evaluations = []
        
        for i, agent_def in enumerate(agent_defs["citizen_agents"]):
            yield {"type": "status", "data": f"市民{i+1}/{len(agent_defs['citizen_agents'])}: {agent_def['name']}"}
            
            citizen_agent = Agent(
                model="us.anthropic.claude-sonnet-4-20250514-v1:0",
                system_prompt=agent_def["system_prompt"],
                callback_handler=None
            )
            
            eval_prompt = f"""{policy_summary}

あなたの立場: {agent_def['profile']}

上記の政策案を評価し、以下のJSON形式で出力してください:

重要: overall_ratingは必ず1から5の整数で評価してください（1:非常に悪い、2:悪い、3:普通、4:良い、5:非常に良い）

{{
  "evaluator_name": "{agent_def['name']}",
  "overall_rating": 3,
  "evaluation_details": {{
    "criterion_1": {{"score": 3, "reason": "理由"}}
  }},
  "expectations": "期待",
  "concerns": "懸念",
  "recommendations": "提言"
}}
"""
            
            try:
                eval_response = ""
                async for event in citizen_agent.stream_async(eval_prompt):
                    if "data" in event:
                        chunk = event["data"]
                        yield {"type": "stream", "step": f"citizen_{i}", "data": chunk}
                        eval_response += chunk
                
                evaluation = extract_json(eval_response)
                if evaluation:
                    citizen_evaluations.append(evaluation)
                    yield {"type": "evaluation", "data": evaluation}
                else:
                    citizen_evaluations.append({
                        "evaluator_name": agent_def['name'],
                        "error": "JSON抽出失敗"
                    })
            except Exception as e:
                citizen_evaluations.append({
                    "evaluator_name": agent_def['name'],
                    "error": str(e)
                })
        
        result_json = {
            "status": "success",
            "user_message": user_message,
            "generated_agents": {
                "policy_agents": [
                    {"name": agent_def["name"], "expertise": agent_def["expertise"]}
                    for agent_def in agent_defs["policy_agents"]
                ],
                "citizen_agents": [
                    {"name": agent_def["name"], "age": agent_def["age"], "profile": agent_def["profile"]}
                    for agent_def in agent_defs["citizen_agents"]
                ]
            },
            "policy_proposal": policy_json,
            "citizen_evaluations": citizen_evaluations,
            "execution_status": {
                "completed": True,
                "policy_agents_count": len(agent_defs["policy_agents"]),
                "citizen_agents_count": len(agent_defs["citizen_agents"]),
                "method": {"policy_creation": "Swarm", "citizen_evaluation": "Workflow"}
            }
        }
        
        yield {"type": "complete", "data": result_json}
    
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        yield {"type": "error", "data": f"エラーが発生しました: {str(e)}"}
        print(f"\n\nエラー詳細:\n{error_msg}")

async def invoke_async(payload):
    """マルチエージェント政策システム（非同期 + Swarm + Workflow）"""
    result_json = {}
    async for chunk in invoke_async_streaming(payload):
        if chunk["type"] == "complete":
            result_json = chunk["data"]
        elif chunk["type"] == "error":
            return {"error": chunk["data"]}
    return result_json

@app.entrypoint
def invoke(payload):
    """AgentCore Runtime エントリーポイント"""
    return asyncio.run(invoke_async(payload))

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--stream":
        test_payload = {"prompt": "子育て支援の所得制限を撤廃して欲しい"}
        print("■■■ 政策検討システム開始（ストリーミング） ■■■")
        print(f"市民意見: {test_payload['prompt']}\n")
        
        async def test_streaming():
            async for chunk in invoke_async_streaming(test_payload):
                if chunk["type"] == "stream":
                    print(chunk["data"], end="", flush=True)
                elif chunk["type"] == "status":
                    print(f"\n\n{chunk['data']}\n")
                elif chunk["type"] == "complete":
                    print("\n\n" + "="*80)
                    print("■■■ 実行完了 ■■■")
                    print("="*80)
        
        try:
            asyncio.run(test_streaming())
        except Exception as e:
            print(f"\nエラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
    else:
        test_payload = {"prompt": "子育て支援の所得制限を撤廃して欲しい"}
        print("■■■ 政策検討システム開始 ■■■")
        print(f"市民意見: {test_payload['prompt']}")
        
        try:
            result = asyncio.run(invoke_async(test_payload))
            
            print("\n\n" + "="*80)
            print("■■■ 実行結果 ■■■")
            print("="*80)
            
            if "error" in result:
                print(f"エラー: {result['error']}")
            else:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            
            print("\n" + "="*80)
        except Exception as e:
            print(f"\nエラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
