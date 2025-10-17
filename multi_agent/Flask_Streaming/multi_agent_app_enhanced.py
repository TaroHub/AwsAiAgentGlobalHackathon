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
    """マルチエージェント政策システム（拡張版・ストリーミング対応）"""
    try:
        user_message = payload.get("prompt", "")
        
        if not user_message:
            yield {"type": "error", "data": "プロンプトが必要です"}
            return
        
        # ステップ0: 類似政策の調査
        yield {"type": "status", "data": "[ステップ0] 他自治体の類似政策を調査中..."}
        
        research_agent = Agent(
            model="us.anthropic.claude-sonnet-4-20250514-v1:0",
            callback_handler=None,
            system_prompt="""あなたは自治体政策の調査専門家です。
市民意見に関連する既存の政策事例を調査し、参考になる事例を提示してください。

調査優先順位:
1. 大阪市の事例を最優先
2. 大阪市に事例がなければ他の政令指定都市や大阪府内の市区町村
3. それでもなければ日本全国の自治体事例

出力形式:
```json
{
  "similar_policies": [
    {"municipality": "自治体名", "policy_name": "政策名", "summary": "概要", "results": "成果"}
  ],
  "has_references": true/false,
  "search_scope": "大阪市/他の市区町村/日本全体"
}
```"""
        )
        
        research_response = ""
        async for event in research_agent.stream_async(f"市民意見: {user_message}\n\nまず大阪市の類似政策事例を調査してください。大阪市に事例がなければ他の市区町村や日本全国の事例を3つ程度調査してください。"):
            if "data" in event:
                chunk = event["data"]
                yield {"type": "stream", "step": "research", "data": chunk}
                research_response += chunk
        
        research_result = extract_json(research_response) or {"similar_policies": [], "has_references": False}
        yield {"type": "research", "data": research_result}
        yield {"type": "stream", "step": "research_complete", "data": f"\n\n【調査完了】類似政策: {len(research_result.get('similar_policies', []))}件"}
        
        # ステップ1a: 人口動態調査
        yield {"type": "status", "data": "[ステップ1a] 対象地域の人口動態を調査中..."}
        
        demographics_agent = Agent(
            model="us.anthropic.claude-sonnet-4-20250514-v1:0",
            callback_handler=None,
            system_prompt="""あなたは人口統計の専門家です。
市民意見から対象地域を特定し、その地域の人口動態を調査してください。

調査優先順位:
1. 大阪市の人口動態を最優先
2. 市民意見で特定の地域が明示されている場合はその地域
3. 大阪市のデータが不明な場合は他の政令指定都市や日本全体の統計

日本語習熟度の判断基準（外国人住民の場合）:
- fluent (流暢): JLPT N1-N2相当。行政文書の読解、窓口での複雑な相談、就労に支障なし
- conversational (会話可能): JLPT N3-N4相当。日常会話は可能だが、専門用語や書類手続きに支援が必要
- basic (基礎レベル): JLPT N5相当またはそれ以下。挨拶・簡単な買い物程度。生活全般で支援が必要
- needs_support (支援必須): ほぼ日本語不可。通訳・翻訳が常時必要

出力形式:
```json
{
  "target_area": "対象地域名",
  "age_distribution": {
    "20代": 10,
    "30代": 15,
    "40代": 15,
    "50代": 20,
    "60代以上": 40
  },
  "gender_ratio": {"male": 48, "female": 52},
  "family_types": [
    {"type": "単身世帯", "percentage": 35},
    {"type": "夫婦のみ", "percentage": 20},
    {"type": "子育て世帯", "percentage": 25},
    {"type": "三世代同居", "percentage": 10},
    {"type": "高齢者のみ", "percentage": 10}
  ],
  "language_distribution": [
    {"language": "日本語", "percentage": 60, "notes": "備考"},
    {"language": "英語", "percentage": 15, "notes": "主にビジネス層"}
  ],
  "japanese_proficiency_levels": {
    "fluent": 30,
    "conversational": 40,
    "basic": 20,
    "needs_support": 10
  },
  "cultural_considerations": [
    {"group": "地域・文化圏", "key_points": ["宗教行事の配慮", "学校での文化摩擦"]},
    {"group": "技能実習生", "key_points": ["行政手続きの支援", "労働時間管理"]}
  ],
  "priority_services": [
    "行政手続きの多言語化（日本語・英語・中国語・ベトナム語）",
    "学校での多文化サポート教員の配置"
  ],
  "data_source": "データソース",
  "data_scope": "大阪市/他の市区町村/日本全体"
}
```"""
        )
        
        demographics_response = ""
        async for event in demographics_agent.stream_async(f"市民意見: {user_message}\n\nまず大阪市の人口動態を調査してください。大阪市のデータが不明な場合は他の市区町村や日本全体の統計を使用してください。"):
            if "data" in event:
                chunk = event["data"]
                yield {"type": "stream", "step": "demographics", "data": chunk}
                demographics_response += chunk
        
        demographics_data = extract_json(demographics_response)
        if not demographics_data:
            yield {"type": "error", "data": "人口動態データの取得に失敗しました"}
            return
        yield {"type": "demographics", "data": demographics_data}
        language_distribution = demographics_data.get('language_distribution', [])
        language_summary = ", ".join(
            f"{entry.get('language', '不明')}: {entry.get('percentage', '?')}%"
            for entry in language_distribution[:3]
        ) or "不明"
        japanese_proficiency = demographics_data.get('japanese_proficiency_levels', {})
        proficiency_summary = ", ".join(
            f"{level}: {percentage}%"
            for level, percentage in japanese_proficiency.items()
        ) or "不明"
        yield {"type": "stream", "step": "demographics_complete", "data": (
            f"\n\n【調査完了】対象地域: {demographics_data.get('target_area', '不明')}"
            f"\n年齢分布: {json.dumps(demographics_data.get('age_distribution', {}), ensure_ascii=False)}"
            f"\n性別比率: {json.dumps(demographics_data.get('gender_ratio', {}), ensure_ascii=False)}"
            f"\n主な言語: {language_summary}"
            f"\n日本語習熟度: {proficiency_summary}"
        )}
        
        # ステップ1b: SVエージェントがエージェント定義を生成（調査した人口動態に基づく）
        yield {"type": "status", "data": "[ステップ1b] エージェント定義を生成中（調査した人口動態に基づく、最低10名）..."}
        
        demographics_text = f"""
対象地域: {demographics_data.get('target_area', '不明')}
年齢分布: {json.dumps(demographics_data.get('age_distribution', {}), ensure_ascii=False)}
性別比率: {json.dumps(demographics_data.get('gender_ratio', {}), ensure_ascii=False)}
家族構成: {json.dumps(demographics_data.get('family_types', []), ensure_ascii=False)}
言語分布: {json.dumps(demographics_data.get('language_distribution', []), ensure_ascii=False)}
日本語習熟度: {json.dumps(demographics_data.get('japanese_proficiency_levels', {}), ensure_ascii=False)}
文化的配慮事項: {json.dumps(demographics_data.get('cultural_considerations', []), ensure_ascii=False)}
優先サービス: {json.dumps(demographics_data.get('priority_services', []), ensure_ascii=False)}
"""
        
        sv_agent = Agent(
            model="us.anthropic.claude-sonnet-4-20250514-v1:0",
            callback_handler=None,
            system_prompt="""市民意見を分析し、政策検討に必要なエージェントを設計してください。

あなたの役割:
1. 市民意見の内容を分析
2. 必要な政策立案エージェントの数と専門分野を決定（目安: 2-4名）
   - 大阪市の政策担当者の視点を含める
3. 市民評価エージェントを最低10名設定（提供された人口動態データに基づく）
   - 大阪市民の多様な視点を反映
4. 市民意見に直接関係ない層も含める（例：子育て政策なら独身高齢者も）

市民エージェント設定基準:
- 提供された人口動態データの年齢分布・性別比率・家族構成に従う
- 大阪市の地域特性（商業都市、多様性等）を考慮
- 政策の直接的影響を受けない層も含める

出力形式:
```json
{
  "policy_agents": [
    {"name": "エージェント名", "expertise": "専門分野", "system_prompt": "詳細なプロンプト"}
  ],
  "citizen_agents": [
    {"name": "名前", "age": 年齢, "gender": "性別", "family": "家族構成", "profile": "詳細プロフィール", "is_directly_affected": true/false, "system_prompt": "評価用プロンプト"}
  ],
  "reviewer_agent": {
    "name": "レビュアー名", "expertise": "専門分野", "system_prompt": "レビュー用プロンプト"
  }
}
```

注意: is_directly_affected は政策の直接的な恩恵を受けるかどうかを示します（true=恩恵を受ける、false=恩恵を受けない/関係ない層）"""
        )
        
        sv_response = ""
        async for event in sv_agent.stream_async(f"市民意見: {user_message}\n\n人口動態データ:\n{demographics_text}"):
            if "data" in event:
                chunk = event["data"]
                yield {"type": "stream", "step": "sv_agent", "data": chunk}
                sv_response += chunk
        
        agent_defs = extract_json(sv_response)
        
        if not agent_defs or len(agent_defs.get("citizen_agents", [])) < 10:
            yield {"type": "error", "data": "エージェント定義の生成に失敗しました（市民エージェントが10名未満）"}
            return
        
        # is_directly_affectedフィールドの確認と警告
        unaffected_count = sum(1 for a in agent_defs.get("citizen_agents", []) if a.get("is_directly_affected") == False)
        yield {"type": "status", "data": f"[ステップ1b] 生成完了: 市民エージェント{len(agent_defs.get('citizen_agents', []))}名（うち政策対象外{unaffected_count}名）"}
        
        yield {"type": "agent_defs", "data": agent_defs}
        
        # ステップ2: Swarmで政策立案（類似政策を参考に）
        yield {"type": "status", "data": "[ステップ2] 政策立案エージェントが協調実行中..."}
        
        reference_text = ""
        if research_result.get("has_references"):
            reference_text = f"\n\n参考事例:\n{json.dumps(research_result['similar_policies'], ensure_ascii=False, indent=2)}\n上記事例を参考にしてください。"
        
        swarm_agent = Agent(
            model="us.anthropic.claude-sonnet-4-20250514-v1:0",
            tools=[swarm],
            callback_handler=None
        )
        
        swarm_prompt = f"""以下のエージェント定義に基づいてswarmを作成し、市民意見「{user_message}」に対する政策案をJSON形式で作成してください。

エージェント定義:
{json.dumps(agent_defs['policy_agents'], ensure_ascii=False, indent=2)}
{reference_text}

出力形式:
```json
{{
  "policy_title": "政策名",
  "summary": "政策概要",
  "referenced_policies": ["参考にした自治体政策"],
  "problem_analysis": "問題分析",
  "recommended_policy": "推奨政策",
  "implementation_plan": "実施計画",
  "expected_effects": "期待効果",
  "is_temporary": true/false
}}
```"""
        
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
        
        # ステップ3: レビュアーによる法律・実現性チェック（最大3回再試行）
        yield {"type": "status", "data": "[ステップ3] レビュアーが法律・実現性をチェック中..."}
        
        reviewer_agent = Agent(
            model="us.anthropic.claude-sonnet-4-20250514-v1:0",
            system_prompt=agent_defs.get("reviewer_agent", {}).get("system_prompt", "法律と実現性の観点でレビューしてください"),
            callback_handler=None
        )
        
        review_result = None
        for attempt in range(1, 4):
            yield {"type": "status", "data": f"[ステップ3] レビュー試行 {attempt}/3"}
            
            review_prompt = f"""以下の政策案を法律と実現性の観点でレビューしてください。

政策案:
{json.dumps(policy_json, ensure_ascii=False, indent=2)}

出力形式:
```json
{{
  "legal_compliance": {{"score": 5, "issues": ["問題点"], "recommendations": ["推奨事項"]}},
  "feasibility": {{"score": 4, "issues": ["問題点"], "recommendations": ["推奨事項"]}},
  "overall_assessment": "総合評価",
  "approved": true/false,
  "improvement_suggestions": "改善提案（承認されない場合）"
}}
```"""
            
            review_response = ""
            async for event in reviewer_agent.stream_async(review_prompt):
                if "data" in event:
                    chunk = event["data"]
                    yield {"type": "stream", "step": f"reviewer_attempt_{attempt}", "data": chunk}
                    review_response += chunk
            
            review_result = extract_json(review_response) or {"approved": False}
            yield {"type": "review", "data": {**review_result, "attempt": attempt}}
            
            if review_result.get("approved", False):
                yield {"type": "status", "data": f"[ステップ3] レビュー承認（{attempt}回目）"}
                break
            
            if attempt < 3:
                yield {"type": "status", "data": f"[ステップ3] 承認されず、政策案を改善中..."}
                
                # 政策案を改善
                improvement_prompt = f"""以下の政策案がレビューで承認されませんでした。

元の政策案:
{json.dumps(policy_json, ensure_ascii=False, indent=2)}

レビュー結果:
{json.dumps(review_result, ensure_ascii=False, indent=2)}

改善提案に基づいて政策案を修正してください。出力形式は元の政策案と同じJSON形式です。"""
                
                policy_response = ""
                async for event in swarm_agent.stream_async(improvement_prompt):
                    if "data" in event:
                        chunk = event["data"]
                        yield {"type": "stream", "step": f"improvement_{attempt}", "data": chunk}
                        policy_response += chunk
                
                improved_policy = extract_json(policy_response)
                if improved_policy:
                    policy_json = improved_policy
                    yield {"type": "policy", "data": {**policy_json, "improved": True, "attempt": attempt}}
            else:
                yield {"type": "status", "data": "[ステップ3] 3回目も承認されませんでしたが、処理を続行します"}
        
        yield {"type": "review_final", "data": review_result}
        
        # ステップ4: 市民評価（濃い評価）
        yield {"type": "status", "data": "[ステップ4] 市民エージェントが評価中..."}
        
        policy_summary = f"""
政策名: {policy_json.get('policy_title', 'N/A')}
概要: {policy_json.get('summary', 'N/A')}
推奨政策: {policy_json.get('recommended_policy', 'N/A')}
参考事例: {', '.join(policy_json.get('referenced_policies', []))}
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
年齢: {agent_def['age']}歳、性別: {agent_def.get('gender', '不明')}、家族: {agent_def.get('family', '不明')}

上記の政策案を詳細に評価してください。

出力形式:
```json
{{
  "evaluator_name": "{agent_def['name']}",
  "overall_rating": 3,
  "detailed_evaluation": {{
    "personal_impact": {{"score": 3, "reason": "自分への影響"}},
    "family_impact": {{"score": 3, "reason": "家族への影響"}},
    "community_impact": {{"score": 3, "reason": "地域への影響"}},
    "fairness": {{"score": 3, "reason": "公平性"}},
    "sustainability": {{"score": 3, "reason": "持続可能性"}}
  }},
  "expectations": "期待すること（具体的に200文字程度）",
  "concerns": "懸念すること（具体的に200文字程度）",
  "recommendations": "提言（具体的に200文字程度）",
  "personal_story": "この政策が自分の生活にどう影響するか（具体的なエピソード）"
}}
```"""
            
            try:
                eval_response = ""
                async for event in citizen_agent.stream_async(eval_prompt):
                    if "data" in event:
                        chunk = event["data"]
                        yield {"type": "stream", "step": f"citizen_{i}", "data": chunk}
                        eval_response += chunk
                
                evaluation = extract_json(eval_response)
                if evaluation:
                    evaluation["is_directly_affected"] = agent_def.get("is_directly_affected", True)
                    citizen_evaluations.append(evaluation)
                    yield {"type": "evaluation", "data": evaluation}
            except Exception as e:
                citizen_evaluations.append({"evaluator_name": agent_def['name'], "error": str(e), "is_directly_affected": agent_def.get("is_directly_affected", True)})
        
        # ステップ5: 10年後評価（一時的政策でない場合）
        future_evaluations = []
        if not policy_json.get("is_temporary", False):
            yield {"type": "status", "data": "[ステップ5] 10年後の評価をシミュレーション中..."}
            
            for i, agent_def in enumerate(agent_defs["citizen_agents"][:5]):  # 代表5名
                yield {"type": "status", "data": f"10年後評価 {i+1}/5: {agent_def['name']}"}
                
                citizen_agent = Agent(
                    model="us.anthropic.claude-sonnet-4-20250514-v1:0",
                    system_prompt=agent_def["system_prompt"],
                    callback_handler=None
                )
                
                future_prompt = f"""{policy_summary}

あなたは10年後の{agent_def['age']+10}歳になっています。
この政策が実施されて10年が経過しました。

10年間の変化と現在の評価を述べてください。

出力形式:
```json
{{
  "evaluator_name": "{agent_def['name']} (10年後)",
  "age_now": {agent_def['age']+10},
  "ten_year_rating": 3,
  "changes_observed": "10年間で観察された変化",
  "long_term_impact": "長期的な影響の評価",
  "unexpected_outcomes": "予想外の結果",
  "current_opinion": "現在の意見"
}}
```"""
                
                try:
                    future_response = ""
                    async for event in citizen_agent.stream_async(future_prompt):
                        if "data" in event:
                            chunk = event["data"]
                            yield {"type": "stream", "step": f"future_{i}", "data": chunk}
                            future_response += chunk
                    
                    future_eval = extract_json(future_response)
                    if future_eval:
                        future_evaluations.append(future_eval)
                        yield {"type": "future_evaluation", "data": future_eval}
                except Exception as e:
                    pass
        
        result_json = {
            "status": "success",
            "user_message": user_message,
            "research_result": research_result,
            "demographics_data": demographics_data,
            "generated_agents": {
                "policy_agents": [{"name": a["name"], "expertise": a["expertise"]} for a in agent_defs["policy_agents"]],
                "citizen_agents": [{"name": a["name"], "age": a["age"], "profile": a["profile"], "is_directly_affected": a.get("is_directly_affected", True)} for a in agent_defs["citizen_agents"]],
                "reviewer": agent_defs.get("reviewer_agent", {}).get("name", "レビュアー")
            },
            "policy_proposal": policy_json,
            "review_result": review_result,
            "citizen_evaluations": citizen_evaluations,
            "future_evaluations": future_evaluations,
            "execution_status": {
                "completed": True,
                "policy_agents_count": len(agent_defs["policy_agents"]),
                "citizen_agents_count": len(agent_defs["citizen_agents"]),
                "has_future_evaluation": len(future_evaluations) > 0
            }
        }
        
        yield {"type": "complete", "data": result_json}
    
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        yield {"type": "error", "data": f"エラーが発生しました: {str(e)}"}
        print(f"\n\nエラー詳細:\n{error_msg}")

async def invoke_async(payload):
    """マルチエージェント政策システム（非同期）"""
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
    # AgentCore Runtimeデプロイ用
    app.run()
