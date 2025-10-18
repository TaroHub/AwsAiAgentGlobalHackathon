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
    """マルチエージェント施策システム（拡張版・ストリーミング対応）"""
    try:
        user_message = payload.get("prompt", "")
       
        if not user_message:
            yield {"type": "error", "data": "プロンプトが必要です"}
            return
       
        # ステップ0: 類似施策の調査
        yield {"type": "status", "data": "[ステップ0] 他自治体の類似施策を調査中..."}
       
        research_agent = Agent(
            model="us.anthropic.claude-haiku-4-5-20251001-v1:0",
            callback_handler=None,
            system_prompt="""あなたは自治体施策の調査専門家です。
市民意見に関連する既存の施策事例を調査し、参考になる事例を提示してください。
 
調査優先順位:
1. 大阪市の事例を最優先
2. 大阪市に事例がなければ他の政令指定都市や大阪府内の市区町村
3. それでもなければ日本全国の自治体事例
 
出力形式:
```json
{
  "similar_policies": [
    {"municipality": "自治体名", "policy_name": "施策名", "summary": "概要", "results": "成果"}
  ],
  "has_references": true/false,
  "search_scope": "大阪市/他の市区町村/日本全体"
}
```"""
        )
       
        research_response = ""
        async for event in research_agent.stream_async(f"市民意見: {user_message}\n\nまず大阪市の類似施策事例を調査してください。大阪市に事例がなければ他の市区町村や日本全国の事例を3つ程度調査してください。"):
            if "data" in event:
                chunk = event["data"]
                yield {"type": "stream", "step": "research", "data": chunk}
                research_response += chunk
       
        research_result = extract_json(research_response) or {"similar_policies": [], "has_references": False}
        yield {"type": "research", "data": research_result}
        yield {"type": "stream", "step": "research_complete", "data": f"\n\n【調査完了】類似施策: {len(research_result.get('similar_policies', []))}件"}
       
        # ステップ1a: 人口動態調査
        yield {"type": "status", "data": "[ステップ1a] 対象地域の人口動態を調査中..."}
       
        demographics_agent = Agent(
            model="us.anthropic.claude-haiku-4-5-20251001-v1:0",
            callback_handler=None,
            system_prompt="""あなたは人口統計の専門家です。
市民意見から対象地域を特定し、その地域の人口動態を調査してください。
 
調査優先順位:
1. 大阪市の人口動態を最優先
2. 市民意見で特定の地域が明示されている場合はその地域
3. 大阪市のデータが不明な場合は他の政令指定都市や日本全体の統計
 
重要: データが存在しない場合は、フェルミ推定を使用してください。
- 類似都市のデータから類推
- 日本全体の統計から地域特性を考慮して補正
- 人口規模、産業構造、地理的特性から推定
- 推定方法を必ずdata_sourceに明記すること
 
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
  "data_source": "データソース",
  "data_scope": "大阪市/他の市区町村/日本全体"
}
```"""
        )
       
        demographics_response = ""
        async for event in demographics_agent.stream_async(f"市民意見: {user_message}\n\nまず大阪市の人口動態を調査してください。大阪市のデータが不明な場合は他の市区町村や日本全体の統計を使用してください。\n\nデータが存在しない場合は、フェルミ推定で合理的な推定値を算出してください。推定方法をdata_sourceに明記してください。"):
            if "data" in event:
                chunk = event["data"]
                yield {"type": "stream", "step": "demographics", "data": chunk}
                demographics_response += chunk
       
        demographics_data = extract_json(demographics_response)
        if not demographics_data:
            yield {"type": "error", "data": "人口動態データの取得に失敗しました"}
            return
        yield {"type": "demographics", "data": demographics_data}
        yield {"type": "stream", "step": "demographics_complete", "data": f"\n\n【調査完了】対象地域: {demographics_data.get('target_area', '不明')}\n年齢分布: {json.dumps(demographics_data.get('age_distribution', {}), ensure_ascii=False)}\n性別比率: {json.dumps(demographics_data.get('gender_ratio', {}), ensure_ascii=False)}"}
       
        # ステップ1b: SVエージェントがエージェント定義を生成（調査した人口動態に基づく）
        yield {"type": "status", "data": "[ステップ1b] エージェント定義を生成中（調査した人口動態に基づく、最低10名）..."}
       
        demographics_text = f"""
対象地域: {demographics_data.get('target_area', '不明')}
年齢分布: {json.dumps(demographics_data.get('age_distribution', {}), ensure_ascii=False)}
性別比率: {json.dumps(demographics_data.get('gender_ratio', {}), ensure_ascii=False)}
家族構成: {json.dumps(demographics_data.get('family_types', []), ensure_ascii=False)}
"""
       
        sv_agent = Agent(
            model="us.anthropic.claude-haiku-4-5-20251001-v1:0",
            callback_handler=None,
            system_prompt="""市民意見を分析し、施策検討に必要なエージェントを設計してください。
 
あなたの役割:
1. 市民意見の内容を分析
2. 必要な施策立案エージェントの数と専門分野を決定（目安: 2-4名）
   - 大阪市の施策担当者の視点を含める
3. 市民評価エージェントを最低10名設定（提供された人口動態データに基づく）
   - 大阪市民の多様な視点を反映
4. 市民意見に直接関係ない層も含める（例：子育て施策なら独身高齢者も）
 
市民エージェント設定基準:
- 提供された人口動態データの年齢分布・性別比率・家族構成に従う
- 大阪市の地域特性（商業都市、多様性等）を考慮
- 施策の直接的影響を受けない層も含める
 
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
 
注意: is_directly_affected は施策の直接的な恩恵を受けるかどうかを示します（true=恩恵を受ける、false=恩恵を受けない/関係ない層）"""
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
        yield {"type": "status", "data": f"[ステップ1b] 生成完了: 市民エージェント{len(agent_defs.get('citizen_agents', []))}名（うち施策対象外{unaffected_count}名）"}
       
        yield {"type": "agent_defs", "data": agent_defs}
       
        # ステップ2: Swarmで施策立案（類似施策を参考に）
        yield {"type": "status", "data": "[ステップ2] 施策立案エージェントが協調実行中..."}
       
        reference_text = ""
        if research_result.get("has_references"):
            reference_text = f"\n\n参考事例:\n{json.dumps(research_result['similar_policies'], ensure_ascii=False, indent=2)}\n上記事例を参考にしてください。"
       
        swarm_agent = Agent(
            model="us.anthropic.claude-haiku-4-5-20251001-v1:0",
            tools=[swarm],
            callback_handler=None
        )
       
        swarm_prompt = f"""以下のエージェント定義に基づいてswarmを作成し、市民意見「{user_message}」に対する**1つの統合された施策案**をJSON形式で作成してください。
 
**重要**: 以下の出力形式を厳守してください。
- JSON形式のみを出力し、余分な説明を追加しないでください
- JSONは1セットのみ出力してください（複数出力しないこと）
 
エージェント定義:
{json.dumps(agent_defs['policy_agents'], ensure_ascii=False, indent=2)}
{reference_text}
 
出力形式:
```json
{{
  "policy_title": "施策名（簡潔で分かりやすいタイトル、50文字以内）",
  "summary": "施策概要（この施策が何を目的とし、誰を対象とするかを簡潔に説明、200-400文字）",
  "referenced_policies": ["参考にした自治体施策名（具体的な自治体名と施策名）"],
  "problem_analysis": "問題分析（現状の課題、なぜこの施策が必要なのか、データや具体例を含めて説明、300-500文字）",
  "detailed_policy": "施策詳細（具体的な施策内容、支援内容、対象者の条件、実施方法、予算規模の目安、必要な体制、考慮すべき事項（法律、既存施策との関係など）を詳しく記載、500-800文字）",
  "implementation_plan": "実施計画（どれくらいの期間でどのように進めていくか、各フェーズの期間と内容、段階的な展開方法を記載、300-500文字）",
  "expected_effects": "期待効果（定量的効果（例：年間○○人が利用、○○%改善）と定性的効果（例：市民満足度向上、地域活性化）を具体的に記載、300-500文字）",
  "is_temporary": true/false（一時的な施策ならtrue、恒久的な施策ならfalse）
}}
```
 
**必須事項**:
- 上記の全ての項目を必ず含めてください
- 各項目の説明に従って、具体的かつ詳細に記載してください
- 文字数目安を参考に、十分な情報量を確保してください
- 長い文章は適宜改行を入れて読みやすくしてください（段落の区切りや項目の列挙時など）"""
       
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
            model="us.anthropic.claude-haiku-4-5-20251001-v1:0",
            system_prompt=agent_defs.get("reviewer_agent", {}).get("system_prompt", "法律と実現性の観点でレビューしてください"),
            callback_handler=None
        )
       
        review_result = None
        for attempt in range(1, 4):
            yield {"type": "status", "data": f"[ステップ3] レビュー試行 {attempt}/3"}
           
            review_prompt = f"""以下の施策案を法律と実現性の観点でレビューしてください。
 
施策案:
{json.dumps(policy_json, ensure_ascii=False, indent=2)}
 
**評価観点（例示）**:
- 法律適合性: 自治体の権限、関連法律、条例、個人情報保護、平等原則など
- 実現可能性: 予算、財源、人員、スケジュール、既存施策との整合性など
  ※上記は例示です。施策内容に応じて適切な観点で評価してください。
 
**スコア基準**:
- 5点: 全く問題なし、完璧に適合している
- 4点: 軽微な改善余地はあるが、概ね良好
- 3点: 一部に問題があり、修正が必要
- 2点: 重大な問題があり、大幅な修正が必要
- 1点: 法律違反または実現不可能
 
**承認基準**:
- approved: true → 法律適合性4点以上 AND 実現可能性4点以上
- approved: false → 上記を満たさない場合
 
**問題点（issues）の書き方**: 障壁・問題になる可能性のある懸念点や検討が必須な重要事項を理由も添えて指摘（考慮が抜けている場合には「...の明記がない」ではなく、「...の明記が必要」のように出力する。）
**推奨事項（recommendations）の書き方**: 問題を解決する具体的な修正案・追記内容を提示
 
**重要**: 以下の出力形式を厳守してください。
- JSON形式のみを出力し、余分な説明を追加しないでください
- JSONは1セットのみ出力してください（複数出力しないこと）
 
出力形式:
```json
{{
  "legal_compliance": {{
    "score": 5,
    "issues": ["問題点1", "問題点2"],
    "recommendations": ["推奨事項1", "推奨事項2"]
  }},
  "feasibility": {{
    "score": 4,
    "issues": ["問題点1", "問題点2"],
    "recommendations": ["推奨事項1", "推奨事項2"]
  }},
  "overall_assessment": "総合評価の文章",
  "approved": true,
  "improvement_suggestions": "改善提案の文章（承認されない場合）"
}}
```
 
**文字数の目安**:
- issues: 全項目を合わせて300〜500文字程度
- recommendations: 全項目を合わせて300〜500文字程度
- overall_assessment: 300文字程度
- improvement_suggestions: 300文字程度
 
注意: issuesとrecommendationsは必ず文字列の配列で、各要素は簡潔にしてください。"""
           
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
                yield {"type": "status", "data": f"[ステップ3] 承認されず、施策案を改善中..."}
               
                # 施策案を改善
                improvement_prompt = f"""以下の施策案がレビューで承認されませんでした。
 
元の施策案:
{json.dumps(policy_json, ensure_ascii=False, indent=2)}
 
レビュー結果:
{json.dumps(review_result, ensure_ascii=False, indent=2)}
 
改善提案に基づいて施策案を修正してください。出力形式は元の施策案と同じJSON形式です。"""
               
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
施策名: {policy_json.get('policy_title', 'N/A')}
施策概要: {policy_json.get('summary', 'N/A')}
問題分析: {policy_json.get('problem_analysis', 'N/A')}
施策詳細: {policy_json.get('detailed_policy', 'N/A')}
実施計画: {policy_json.get('implementation_plan', 'N/A')}
期待効果: {policy_json.get('expected_effects', 'N/A')}
参考事例: {', '.join(policy_json.get('referenced_policies', []))}
"""
       
        citizen_evaluations = []
       
        for i, agent_def in enumerate(agent_defs["citizen_agents"]):
            yield {"type": "status", "data": f"市民{i+1}/{len(agent_defs['citizen_agents'])}: {agent_def['name']}"}
           
            citizen_agent = Agent(
                model="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                system_prompt=agent_def["system_prompt"],
                callback_handler=None
            )
           
            eval_prompt = f"""{policy_summary}
 
あなたの立場: {agent_def['profile']}
年齢: {agent_def['age']}歳、性別: {agent_def.get('gender', '不明')}、家族: {agent_def.get('family', '不明')}
 
上記の施策案を、あなた自身の生活や立場から評価してください。
 
**重要**: 以下の出力形式を厳守してください。
- JSON形式のみを出力し、余分な説明を追加しないでください
- JSONは1セットのみ出力してください（複数出力しないこと）
 
**スコア基準**:
- 5点: とても賛成、ぜひ実施してほしい
- 4点: 賛成、実施してほしい
- 3点: どちらでもない
- 2点: あまり賛成できない
- 1点: 反対、実施してほしくない
 
出力形式:
```json
{{
  "evaluator_name": "{agent_def['name']}",
  "overall_rating": 3,
  "personal_impact": "この施策が自分の生活にどう影響するか（具体的に200文字程度）",
  "expectations": "期待すること（具体的に200文字程度）",
  "concerns": "懸念すること（具体的に200文字程度）",
  "recommendations": "提言（具体的に200文字程度）"
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
       
        # ステップ5: 10年後評価（一時的施策でない場合）
        future_evaluations = []
        if not policy_json.get("is_temporary", False):
            yield {"type": "status", "data": "[ステップ5] 10年後の評価をシミュレーション中..."}
           
            total_citizens = len(agent_defs["citizen_agents"])
            for i, agent_def in enumerate(agent_defs["citizen_agents"]):
                yield {"type": "status", "data": f"10年後評価 {i+1}/{total_citizens}: {agent_def['name']}"}
               
                citizen_agent = Agent(
                    model="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    system_prompt=agent_def["system_prompt"],
                    callback_handler=None
                )
               
                future_prompt = f"""{policy_summary}
 
あなたは10年後の{agent_def['age']+10}歳になっています。
この施策が実施されて10年が経過しました。
 
10年間の変化と現在の評価を述べてください。
 
**重要**: 以下の出力形式を厳守してください。
- JSON形式のみを出力し、余分な説明を追加しないでください
- JSONは1セットのみ出力してください（複数出力しないこと）
 
**スコア基準**:
- 5点: とても良かった、継続・拡大してほしい
- 4点: 良かった、継続してほしい
- 3点: どちらでもない
- 2点: あまり良くなかった
- 1点: 悪かった、見直すべき
 
出力形式:
```json
{{
  "evaluator_name": "{agent_def['name']} (10年後)",
  "age_now": {agent_def['age']+10},
  "ten_year_rating": 3,
  "changes_observed": "10年間で観察された変化（具体的に200文字程度）",
  "long_term_impact": "長期的な影響の評価（具体的に200文字程度）",
  "unexpected_outcomes": "予想外の結果（具体的に200文字程度）",
  "current_opinion": "現在の意見（具体的に200文字程度）"
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
       
        # ステップ6: 最終評価
        yield {"type": "status", "data": "[ステップ6] 最終評価を算出中..."}
       
        # 効果・成果スコア（市民評価の平均）
        citizen_ratings = [e.get("overall_rating", 0) for e in citizen_evaluations if "overall_rating" in e]
        effectiveness_score = (sum(citizen_ratings) / len(citizen_ratings) * 20) if citizen_ratings else 50
       
        final_evaluator = Agent(
            model="us.anthropic.claude-haiku-4-5-20251001-v1:0",
            callback_handler=None,
            system_prompt="""あなたは施策評価の専門家です。
以下の5つの観点から施策を評価してください。
 
1. 公平性（Equity）- 重み25%
2. 効果・成果（Effectiveness）- 重み25% （市民評価を反映）
3. 透明性・説明責任（Transparency）- 重み20%
4. 持続可能性・コスト効率（Sustainability）- 重み15%
5. 社会的受容性・倫理性（Ethical Acceptability）- 重み10%
 
**重要**: 以下の出力形式を厳守してください。
- JSON形式のみを出力し、余分な説明を追加しないでください
- JSONは1セットのみ出力してください（複数出力しないこと）
- recommendationフィールドは「推奨」「条件付き推奨」「再検討推奨」のどれかの値で必ず出力してください
 
出力形式:
```json
{{
  "equity": {{"score": 75, "comment": "評価コメント"}},
  "effectiveness": {{"score": 80, "comment": "評価コメント"}},
  "transparency": {{"score": 70, "comment": "評価コメント"}},
  "sustainability": {{"score": 65, "comment": "評価コメント"}},
  "ethical_acceptability": {{"score": 85, "comment": "評価コメント"}},
  "total_score": 75.5,
  "overall_comment": "総合評価コメント",
  "recommendation": "推奨/条件付き推奨/再検討推奨"
}}
```"""
        )
       
        final_prompt = f"""施策案:
{json.dumps(policy_json, ensure_ascii=False, indent=2)}
 
市民評価数: {len(citizen_evaluations)}名
市民評価データ:
{json.dumps(citizen_evaluations, ensure_ascii=False, indent=2)}
 
以下の5つの観点で施策を評価してください：
 
1. 公平性（Equity）- 重み25%
   - 施策が特定層に偏らず、公平に恩恵が行き渡るか
   - 施策対象外の市民の意見も考慮
   - 支援対象分布の偏り、格差是正度を評価
 
2. 効果・成果（Effectiveness）- 重み25%
   - 市民平均評価: {sum(citizen_ratings)/len(citizen_ratings):.2f}/5 ({effectiveness_score:.1f}/100)
   - このスコアをそのまま使用: {effectiveness_score:.1f}点
   - 市民満足度を直接反映
 
3. 透明性・説明責任（Transparency）- 重み20%
   - 意思決定の根拠や過程が明示されているか
   - 市民の"concerns"や"recommendations"から説明不足の指摘を分析
   - 根拠データ数、説明可能性を評価
 
4. 持続可能性・コスト効率（Sustainability）- 重み15%
   - 財政的・人的リソース観点から継続可能か
   - 市民の"concerns"から財政負担への懸念を分析
   - コスト対効果比、長期的影響度を評価
 
5. 社会的受容性・倫理性（Ethical Acceptability）- 重み10%
   - 人権・プライバシー・倫理的観点から適切か
   - 市民の"concerns"から倫理的懸念を分析
   - AIによる施策立案における倫理リスクを評価
 
総合スコア = 公平性×0.25 + 効果・成果×0.25 + 透明性×0.20 + 持続可能性×0.15 + 倫理性×0.10
 
推奨判定基準:
- 70点以上: 推奨
- 50-69点: 条件付き推奨
- 50点未満: 再検討推奨
"""
       
        final_response = ""
        async for event in final_evaluator.stream_async(final_prompt):
            if "data" in event:
                chunk = event["data"]
                yield {"type": "stream", "step": "final_assessment", "data": chunk}
                final_response += chunk
 
        final_assessment = extract_json(final_response) or {"total_score": 0}
        yield {"type": "final_assessment", "data": final_assessment}
       
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
            "final_assessment": final_assessment,
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
 
@app.entrypoint
async def invoke(payload):
    """AgentCore Runtime エントリーポイント（ストリーミング対応）"""
    async for chunk in invoke_async_streaming(payload):
        yield chunk
 
if __name__ == "__main__":
    # AgentCore Runtimeデプロイ用
    app.run()
 