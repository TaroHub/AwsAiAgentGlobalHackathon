from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool
import json

app = BedrockAgentCoreApp()

# グローバル変数でエージェント設定を保持
policy_agent_config = {}
citizen_agents_config = {}
broadlistening_analysis = {}

@tool
def analyze_broadlistening_results(citizen_opinion: str, broadlistening_data: str) -> str:
    """ブロードリスニング結果分析エージェント"""
    global broadlistening_analysis
    
    analysis_agent = Agent(
        model="us.anthropic.claude-sonnet-4-20250514-v1:0"
    )
    
    prompt = f"""
あなたはブロードリスニング結果分析の専門家です。
市民意見「{citizen_opinion}」に関連するブロードリスニングデータを分析してください。

ブロードリスニングデータ:
{broadlistening_data}

以下のJSON形式で分析結果を提供してください：
{{
  "main_themes": ["主要テーマ1", "主要テーマ2", "主要テーマ3"],
  "sentiment_analysis": {{
    "positive_ratio": 0.0から1.0の数値,
    "negative_ratio": 0.0から1.0の数値,
    "neutral_ratio": 0.0から1.0の数値
  }},
  "priority_issues": [
    {{
      "issue": "具体的な課題",
      "frequency": "言及頻度",
      "urgency": "緊急度（高/中/低）",
      "impact": "影響範囲"
    }}
  ],
  "demographic_insights": {{
    "target_groups": ["対象層1", "対象層2"],
    "regional_patterns": "地域的な傾向",
    "age_group_concerns": "年齢層別の関心事"
  }},
  "policy_recommendations": [
    "政策提案1",
    "政策提案2",
    "政策提案3"
  ],
  "implementation_considerations": [
    "実装時の考慮事項1",
    "実装時の考慮事項2"
  ]
}}

分析では以下の点に注目してください：
1. 市民の声の中で最も頻繁に言及される課題
2. 感情的な反応（不満、期待、要望）の傾向
3. 異なる市民層の異なるニーズ
4. 実現可能性と優先順位
5. 政策立案への具体的な示唆
"""
    
    result = analysis_agent(prompt)
    if isinstance(result.message, dict):
        analysis_text = result.message['content'][0]['text']
    else:
        analysis_text = result.message
    
    try:
        broadlistening_analysis = json.loads(analysis_text)
        return f"ブロードリスニング分析完了: {len(broadlistening_analysis.get('main_themes', []))}つの主要テーマを特定"
    except:
        broadlistening_analysis = {
            "main_themes": ["一般的な課題"],
            "sentiment_analysis": {"positive_ratio": 0.3, "negative_ratio": 0.5, "neutral_ratio": 0.2},
            "priority_issues": [{"issue": "基本的な課題", "frequency": "中", "urgency": "中", "impact": "中"}],
            "policy_recommendations": ["基本的な政策提案"]
        }
        return "デフォルトブロードリスニング分析設定"

@tool
def setup_policy_agent(citizen_opinion: str) -> str:
    """政策作成エージェントの設定"""
    global policy_agent_config
    
    setup_agent = Agent(
        model="us.anthropic.claude-sonnet-4-20250514-v1:0"
    )
    
    prompt = f"""
市民意見「{citizen_opinion}」に基づいて、最適な政策作成エージェントの設定を決定してください。

以下のJSON形式で回答してください：
{{
  "role": "具体的な専門家の役割",
  "specialty": "専門分野",
  "background": "経歴・背景",
  "system_prompt": "詳細なシステムプロンプト"
}}

例：子育て支援なら教育政策専門家、交通問題なら都市計画専門家など
"""
    
    result = setup_agent(prompt)
    if isinstance(result.message, dict):
        config_text = result.message['content'][0]['text']
    else:
        config_text = result.message
    
    try:
        policy_agent_config = json.loads(config_text)
        return f"政策作成エージェント設定完了: {policy_agent_config['role']}"
    except:
        policy_agent_config = {
            "role": "政策立案専門家",
            "specialty": "一般政策",
            "background": "行政経験",
            "system_prompt": "政策案を作成してください。"
        }
        return "デフォルト政策作成エージェント設定"

@tool
def setup_citizen_agents(citizen_opinion: str) -> str:
    """3つの市民エージェントの設定"""
    global citizen_agents_config

    setup_agent = Agent(
        model="us.anthropic.claude-sonnet-4-20250514-v1:0"
    )

    prompt = f"""
市民意見「{citizen_opinion}」に基づいて、現実的な賛否分布を反映した3つの市民エージェントを設定してください。

【基本方針】
この政策に対して「実際の市民の何%が賛成しそうか？」を考え、その分布に合わせて3人を設定してください。
全ての政策に機械的に「賛成・中立・反対」を割り当てるのではなく、政策の性質に応じて柔軟に選んでください。

【利害関係の5分類】（同じ分類を複数回選択してもOK）

• 支持派: 政策で生活が改善される当事者
• 条件付き支持派: 必要性は認めるが、やり方に懸念あり
• 中立派: 直接の利害は薄く、「まあ必要かな」程度
• 慎重派: 目的には賛同するが、実現可能性・副作用・コストに懸念
• 反対派: 政策により不利益を被る立場

【選択パターンの例】

賛成多数が予想される政策（安全対策、災害対応など）
→ 支持派2人 + 条件付き支持派1人

一般的な支援政策（子育て支援、インフラ整備など）
→ 支持派1人 + 条件付き支持派1人 + 慎重派1人

賛否が拮抗する政策（大規模開発、規制強化など）
→ 支持派1人 + 中立派1人 + 反対派1人

反対が多い政策（大幅増税、不公平な優遇など）
→ 条件付き支持派1人 + 慎重派1人 + 反対派1人

※上記は目安です。市民意見の内容を踏まえて柔軟に判断してください。

【JSON出力】
{{
  "citizen_agent_1": {{
    "name": "具体的な名前",
    "age": 年齢,
    "occupation": "職業",
    "family": "家族構成",
    "stake_in_policy": "支持派/条件付き支持派/中立派/慎重派/反対派",
    "values": "価値観・関心事",
    "personal_context": "この政策が自分の生活にどう関わるか、期待や懸念を具体的に",
    "system_prompt": "あなたは{{name}}です。{{age}}歳の{{occupation}}で、{{family}}という家族構成です。
価値観: {{values}}
立場: {{stake_in_policy}}
状況: {{personal_context}}

この政策を評価する際は、あなた自身の日常生活に基づいて評価してください。
「この政策が実施されたら、自分や家族の生活がどう変わるか」を具体的に想像し、
あなたの立場からの率直な期待や懸念を表現してください。"
  }},
  "citizen_agent_2": {{ ... }},
  "citizen_agent_3": {{ ... }}
}}
"""

    result = setup_agent(prompt)
    if isinstance(result.message, dict):
        config_text = result.message['content'][0]['text']
    else:
        config_text = result.message

    try:
        # JSON抽出（マークダウンのコードブロックに囲まれている場合に対応）
        import re
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', config_text, re.DOTALL)
        if json_match:
            config_text = json_match.group(1)
        elif '```' in config_text:
            config_text = config_text.split('```')[1].replace('json', '').strip()

        citizen_agents_config = json.loads(config_text)
        names = [citizen_agents_config[f"citizen_agent_{i}"]["name"] for i in range(1, 4)]
        return f"市民エージェント設定完了: {', '.join(names)}"
    except:
        citizen_agents_config = {
            "citizen_agent_1": {
                "name": "田中恵美",
                "age": 35,
                "occupation": "会社員（時短勤務中）",
                "family": "配偶者・未就学児2人（3歳と5歳）",
                "stake_in_policy": "支持派",
                "values": "子育てと仕事の両立、家族の時間、地域の子育て環境",
                "personal_context": "共働きで保育園の送迎が大変。子育て支援が充実すれば、仕事と育児の両立がしやすくなり、経済的負担も減る。地域で子育てしやすい環境を強く望んでいる。",
                "system_prompt": "あなたは田中恵美です。35歳の会社員（時短勤務中）で、配偶者・未就学児2人（3歳と5歳）という家族構成です。\n価値観: 子育てと仕事の両立、家族の時間、地域の子育て環境\n立場: 支持派\n状況: 共働きで保育園の送迎が大変。子育て支援が充実すれば、仕事と育児の両立がしやすくなり、経済的負担も減る。地域で子育てしやすい環境を強く望んでいる。\n\nこの政策を評価する際は、あなた自身の日常生活に基づいて評価してください。\n「この政策が実施されたら、自分や家族の生活がどう変わるか」を具体的に想像し、\nあなたの立場からの率直な期待や懸念を表現してください。"
            },
            "citizen_agent_2": {
                "name": "佐藤隆",
                "age": 50,
                "occupation": "自営業（飲食店経営）",
                "family": "配偶者・大学生の子供1人",
                "stake_in_policy": "中立派",
                "values": "公平な税負担、地域経済の活性化、持続可能な財政運営",
                "personal_context": "子育ては一段落したが、自営業として税負担は気になる。政策の費用対効果や、税金の使い道が適切かを重視。地域全体のためになるなら賛成だが、特定の人だけが得する政策には慎重。",
                "system_prompt": "あなたは佐藤隆です。50歳の自営業（飲食店経営）で、配偶者・大学生の子供1人という家族構成です。\n価値観: 公平な税負担、地域経済の活性化、持続可能な財政運営\n立場: 中立派\n状況: 子育ては一段落したが、自営業として税負担は気になる。政策の費用対効果や、税金の使い道が適切かを重視。地域全体のためになるなら賛成だが、特定の人だけが得する政策には慎重。\n\nこの政策を評価する際は、あなた自身の日常生活に基づいて評価してください。\n「この政策が実施されたら、自分や家族の生活がどう変わるか」を具体的に想像し、\nあなたの立場からの率直な期待や懸念を表現してください。"
            },
            "citizen_agent_3": {
                "name": "鈴木良子",
                "age": 68,
                "occupation": "年金生活者（元公務員）",
                "family": "配偶者と二人暮らし",
                "stake_in_policy": "慎重派",
                "values": "財政健全性、将来世代への責任、持続可能な制度設計",
                "personal_context": "年金生活で収入は限られている。新しい政策には賛成したいが、財政負担が将来世代に回らないか、本当に実現可能か、副作用はないかを慎重に考える。安易なバラマキには反対。",
                "system_prompt": "あなたは鈴木良子です。68歳の年金生活者（元公務員）で、配偶者と二人暮らしという家族構成です。\n価値観: 財政健全性、将来世代への責任、持続可能な制度設計\n立場: 慎重派\n状況: 年金生活で収入は限られている。新しい政策には賛成したいが、財政負担が将来世代に回らないか、本当に実現可能か、副作用はないかを慎重に考える。安易なバラマキには反対。\n\nこの政策を評価する際は、あなた自身の日常生活に基づいて評価してください。\n「この政策が実施されたら、自分や家族の生活がどう変わるか」を具体的に想像し、\nあなたの立場からの率直な期待や懸念を表現してください。"
            }
        }
        return "デフォルト市民エージェント設定"

@tool
def create_policy(citizen_opinion: str) -> str:
    """政策作成エージェントによる政策案作成（ブロードリスニング分析結果を含む）"""
    global policy_agent_config, broadlistening_analysis
    
    policy_agent = Agent(
        model="us.anthropic.claude-sonnet-4-20250514-v1:0"
    )
    
    system_prompt = policy_agent_config.get("system_prompt", "政策案を作成してください。")
    
    # ブロードリスニング分析結果を整形
    if broadlistening_analysis:
        analysis_summary = f"""
ブロードリスニング分析結果:
- 主要テーマ: {', '.join(broadlistening_analysis.get('main_themes', []))}
- 市民感情分析: 肯定的{broadlistening_analysis.get('sentiment_analysis', {}).get('positive_ratio', 0)*100:.1f}%, 否定的{broadlistening_analysis.get('sentiment_analysis', {}).get('negative_ratio', 0)*100:.1f}%
- 優先課題: {json.dumps(broadlistening_analysis.get('priority_issues', []), ensure_ascii=False, indent=2)}
- 政策提案: {', '.join(broadlistening_analysis.get('policy_recommendations', []))}
- 実装考慮事項: {', '.join(broadlistening_analysis.get('implementation_considerations', []))}
"""
    else:
        analysis_summary = "ブロードリスニング分析結果: 利用できません"
    
    prompt = f"""
{system_prompt}

市民意見: {citizen_opinion}

{analysis_summary}

上記の市民意見とブロードリスニング分析結果を総合的に考慮して、実現可能で具体的な政策案を作成してください。
特に以下の点を重視してください：
1. ブロードリスニングで特定された主要テーマへの対応
2. 市民の感情傾向を考慮した政策設計
3. 優先課題の解決策
4. 実装時の考慮事項への配慮
"""
    
    result = policy_agent(prompt)
    if isinstance(result.message, dict):
        return result.message['content'][0]['text']
    return result.message

@tool
def evaluate_policy_citizen1(policy_text: str) -> str:
    """市民エージェント1による評価"""
    global citizen_agents_config

    agent_config = citizen_agents_config.get("citizen_agent_1", {})
    agent = Agent(
        model="us.anthropic.claude-sonnet-4-20250514-v1:0"
    )

    system_prompt = agent_config.get("system_prompt", "政策を評価してください。")

    prompt = f"""
{system_prompt}

政策案: {policy_text}

以下の8つの観点で100点満点で評価し、JSON形式で回答してください。
あなた自身の日常生活、価値観、立場に基づいて率直に評価してください。

{{
  "personal_impact": {{
    "score": 0-100,
    "comment": "この政策があなた自身や家族にどう影響するか（恩恵と負担を総合して）"
  }},
  "feasibility": {{
    "score": 0-100,
    "comment": "本当に実現できそうか（予算、法制度、実装の難易度）"
  }},
  "cost_effectiveness": {{
    "score": 0-100,
    "comment": "かかる費用に対して、得られる効果は十分か"
  }},
  "coverage": {{
    "score": 0-100,
    "comment": "この政策で助かる人はどれくらいいるか、広く恩恵があるか"
  }},
  "fairness": {{
    "score": 0-100,
    "comment": "特定の人だけが得したり損したりしないか、不公平感はないか"
  }},
  "risks": {{
    "score": 0-100,
    "comment": "副作用や予期しない悪影響のリスク（高いほど安全）"
  }},
  "sustainability": {{
    "score": 0-100,
    "comment": "長期的に持続可能か、将来世代にツケを回さないか"
  }},
  "innovation": {{
    "score": 0-100,
    "comment": "新しい発想やアプローチか、従来の方法を超える可能性があるか"
  }},
  "reasoning": "総合評価の理由（あなたの立場と価値観からの率直な意見）",
  "improvement_suggestions": "改善提案"
}}

評価のポイント:
- personal_impact: あなたの生活が良くなる/悪くなる度合い
- feasibility: あなたの常識や経験から見て「本当にできそう」と思えるか
- cost_effectiveness: 税金の使い道として納得できるか
- coverage: あなたと同じような立場の人、それ以外の人も助かるか
- fairness: あなたから見て「不公平だ」と感じないか
- risks: あなたやあなたの大切な人に悪影響がないか
- sustainability: 一時的なものでなく、続けられそうか
- innovation: 今までと違う新しい試みとして評価できるか
"""

    result = agent(prompt)
    if isinstance(result.message, dict):
        return result.message['content'][0]['text']
    return result.message

@tool
def evaluate_policy_citizen2(policy_text: str) -> str:
    """市民エージェント2による評価"""
    global citizen_agents_config

    agent_config = citizen_agents_config.get("citizen_agent_2", {})
    agent = Agent(
        model="us.anthropic.claude-sonnet-4-20250514-v1:0"
    )

    system_prompt = agent_config.get("system_prompt", "政策を評価してください。")

    prompt = f"""
{system_prompt}

政策案: {policy_text}

以下の8つの観点で100点満点で評価し、JSON形式で回答してください。
あなた自身の日常生活、価値観、立場に基づいて率直に評価してください。

{{
  "personal_impact": {{
    "score": 0-100,
    "comment": "この政策があなた自身や家族にどう影響するか（恩恵と負担を総合して）"
  }},
  "feasibility": {{
    "score": 0-100,
    "comment": "本当に実現できそうか（予算、法制度、実装の難易度）"
  }},
  "cost_effectiveness": {{
    "score": 0-100,
    "comment": "かかる費用に対して、得られる効果は十分か"
  }},
  "coverage": {{
    "score": 0-100,
    "comment": "この政策で助かる人はどれくらいいるか、広く恩恵があるか"
  }},
  "fairness": {{
    "score": 0-100,
    "comment": "特定の人だけが得したり損したりしないか、不公平感はないか"
  }},
  "risks": {{
    "score": 0-100,
    "comment": "副作用や予期しない悪影響のリスク（高いほど安全）"
  }},
  "sustainability": {{
    "score": 0-100,
    "comment": "長期的に持続可能か、将来世代にツケを回さないか"
  }},
  "innovation": {{
    "score": 0-100,
    "comment": "新しい発想やアプローチか、従来の方法を超える可能性があるか"
  }},
  "reasoning": "総合評価の理由（あなたの立場と価値観からの率直な意見）",
  "improvement_suggestions": "改善提案"
}}

評価のポイント:
- personal_impact: あなたの生活が良くなる/悪くなる度合い
- feasibility: あなたの常識や経験から見て「本当にできそう」と思えるか
- cost_effectiveness: 税金の使い道として納得できるか
- coverage: あなたと同じような立場の人、それ以外の人も助かるか
- fairness: あなたから見て「不公平だ」と感じないか
- risks: あなたやあなたの大切な人に悪影響がないか
- sustainability: 一時的なものでなく、続けられそうか
- innovation: 今までと違う新しい試みとして評価できるか
"""

    result = agent(prompt)
    if isinstance(result.message, dict):
        return result.message['content'][0]['text']
    return result.message

@tool
def evaluate_policy_citizen3(policy_text: str) -> str:
    """市民エージェント3による評価"""
    global citizen_agents_config

    agent_config = citizen_agents_config.get("citizen_agent_3", {})
    agent = Agent(
        model="us.anthropic.claude-sonnet-4-20250514-v1:0"
    )

    system_prompt = agent_config.get("system_prompt", "政策を評価してください。")

    prompt = f"""
{system_prompt}

政策案: {policy_text}

以下の8つの観点で100点満点で評価し、JSON形式で回答してください。
あなた自身の日常生活、価値観、立場に基づいて率直に評価してください。

{{
  "personal_impact": {{
    "score": 0-100,
    "comment": "この政策があなた自身や家族にどう影響するか（恩恵と負担を総合して）"
  }},
  "feasibility": {{
    "score": 0-100,
    "comment": "本当に実現できそうか（予算、法制度、実装の難易度）"
  }},
  "cost_effectiveness": {{
    "score": 0-100,
    "comment": "かかる費用に対して、得られる効果は十分か"
  }},
  "coverage": {{
    "score": 0-100,
    "comment": "この政策で助かる人はどれくらいいるか、広く恩恵があるか"
  }},
  "fairness": {{
    "score": 0-100,
    "comment": "特定の人だけが得したり損したりしないか、不公平感はないか"
  }},
  "risks": {{
    "score": 0-100,
    "comment": "副作用や予期しない悪影響のリスク（高いほど安全）"
  }},
  "sustainability": {{
    "score": 0-100,
    "comment": "長期的に持続可能か、将来世代にツケを回さないか"
  }},
  "innovation": {{
    "score": 0-100,
    "comment": "新しい発想やアプローチか、従来の方法を超える可能性があるか"
  }},
  "reasoning": "総合評価の理由（あなたの立場と価値観からの率直な意見）",
  "improvement_suggestions": "改善提案"
}}

評価のポイント:
- personal_impact: あなたの生活が良くなる/悪くなる度合い
- feasibility: あなたの常識や経験から見て「本当にできそう」と思えるか
- cost_effectiveness: 税金の使い道として納得できるか
- coverage: あなたと同じような立場の人、それ以外の人も助かるか
- fairness: あなたから見て「不公平だ」と感じないか
- risks: あなたやあなたの大切な人に悪影響がないか
- sustainability: 一時的なものでなく、続けられそうか
- innovation: 今までと違う新しい試みとして評価できるか
"""

    result = agent(prompt)
    if isinstance(result.message, dict):
        return result.message['content'][0]['text']
    return result.message

@tool
def calculate_final_score(eval1: str, eval2: str, eval3: str) -> str:
    """最終スコア計算"""
    try:
        # JSON抽出（マークダウンのコードブロックに囲まれている場合に対応）
        import re

        def extract_json(text):
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_match:
                return json_match.group(1)
            elif '```' in text:
                return text.split('```')[1].replace('json', '').strip()
            return text

        evaluations = [
            json.loads(extract_json(eval1)),
            json.loads(extract_json(eval2)),
            json.loads(extract_json(eval3))
        ]

        total_weighted_score = 0
        improvement_points = []

        for evaluation in evaluations:
            # 8指標のスコアを取得
            personal_impact = evaluation["personal_impact"]["score"]
            feasibility = evaluation["feasibility"]["score"]
            cost_effectiveness = evaluation["cost_effectiveness"]["score"]
            coverage = evaluation["coverage"]["score"]
            fairness = evaluation["fairness"]["score"]
            risks = evaluation["risks"]["score"]
            sustainability = evaluation["sustainability"]["score"]
            innovation = evaluation["innovation"]["score"]

            # 重み付き計算
            weighted_score = (
                personal_impact * 0.25 +
                feasibility * 0.15 +
                cost_effectiveness * 0.15 +
                coverage * 0.12 +
                fairness * 0.10 +
                risks * 0.10 +
                sustainability * 0.08 +
                innovation * 0.05
            )

            total_weighted_score += weighted_score
            improvement_points.append(evaluation.get("improvement_suggestions", ""))

        # 3人の単純平均
        average_score = total_weighted_score / 3

        # 承認判定
        if average_score >= 70:
            status = "承認"
            needs_improvement = False
        elif average_score >= 50:
            status = "改善ループ"
            needs_improvement = True
        else:
            status = "廃案"
            needs_improvement = False

        return json.dumps({
            "average_weighted_score": round(average_score, 2),
            "status": status,
            "approved": average_score >= 70,
            "needs_improvement": needs_improvement,
            "improvement_points": improvement_points
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

@tool
def improve_policy(current_policy: str, improvement_points: str) -> str:
    """政策改善ツール（ブロードリスニング分析結果を考慮）"""
    global policy_agent_config, broadlistening_analysis
    
    policy_agent = Agent(
        model="us.anthropic.claude-sonnet-4-20250514-v1:0"
    )
    
    system_prompt = policy_agent_config.get("system_prompt", "政策案を作成してください。")
    
    # ブロードリスニング分析結果を整形
    if broadlistening_analysis:
        analysis_summary = f"""
ブロードリスニング分析結果（参考）:
- 主要テーマ: {', '.join(broadlistening_analysis.get('main_themes', []))}
- 優先課題: {', '.join([issue.get('issue', '') for issue in broadlistening_analysis.get('priority_issues', [])])}
- 政策提案: {', '.join(broadlistening_analysis.get('policy_recommendations', []))}
"""
    else:
        analysis_summary = ""
    
    prompt = f"""
{system_prompt}

現在の政策案:
{current_policy}

市民からの改善提案:
{improvement_points}

{analysis_summary}

上記の改善提案を反映し、ブロードリスニング分析結果も考慮して、より良い政策案を作成してください。
"""
    
    result = policy_agent(prompt)
    if isinstance(result.message, dict):
        return result.message['content'][0]['text']
    return result.message

@app.entrypoint
def invoke(payload):
    """マルチエージェント政策システム（個別エージェント対応）"""
    user_message = payload.get("prompt", "")
    
    if not user_message:
        return {"error": "プロンプトが必要です"}
    
    # ブロードリスニングデータのサンプル（実際の実装では外部システムから取得）
    sample_broadlistening_data = json.dumps({
        "query": f"{user_message} lang:ja",
        "collection_window": {
            "from": "2025-09-15T00:00:00Z",
            "to": "2025-10-02T00:00:00Z",
            "timezone": "Asia/Tokyo"
        },
        "meta": {
            "language": "ja",
            "total_collected": 480,
            "filtered_count": 300
        },
        "samples": [
            "保育園の待機児童がまだ解消されていない。もっと枠を増やしてほしい。",
            "子育て支援の給付申請が分かりづらい。オンライン申請の手順を簡単にしてほしい。",
            "学童の定員が足りず、仕事を早退せざるを得ない。放課後の受け皿を増やしてほしい。",
            "交通費負担が大きい。通学や通園の補助があると助かる。"
        ]
    }, ensure_ascii=False)
    
    # 監督エージェント
    supervisor = Agent(
        model="us.anthropic.claude-sonnet-4-20250514-v1:0",
        tools=[
            analyze_broadlistening_results,
            setup_policy_agent, 
            setup_citizen_agents, 
            create_policy, 
            evaluate_policy_citizen1, 
            evaluate_policy_citizen2, 
            evaluate_policy_citizen3, 
            calculate_final_score,
            improve_policy
        ]
    )
    
    supervisor_prompt = f"""
市民意見「{user_message}」に対して、以下の手順で政策検討を行ってください：

1. analyze_broadlistening_resultsツールでブロードリスニング結果を分析（引数: citizen_opinion="{user_message}", broadlistening_data="{sample_broadlistening_data}"）
2. setup_policy_agentツールで政策作成エージェントを設定
3. setup_citizen_agentsツールで3つの市民エージェントを設定
4. 最大3回まで繰り返し：
   a) create_policyツールで政策案を作成（市民意見とブロードリスニング分析結果を考慮）
   b) evaluate_policy_citizen1, evaluate_policy_citizen2, evaluate_policy_citizen3ツールで各市民エージェントの評価を取得
   c) calculate_final_scoreツールで最終スコアを計算
   d) 70点以上なら承認で終了、未満ならimprove_policyツールで改善して次のループへ

承認基準:
- 70点以上: 承認
- 50-69点: 改善ループ（最大3回まで）
- 50点未満: 廃案

最終的に結果をまとめて報告してください。ブロードリスニング分析結果がどのように政策に反映されたかも含めてください。
"""
    
    result = supervisor(supervisor_prompt)
    
    if isinstance(result.message, dict):
        response_text = result.message['content'][0]['text']
    else:
        response_text = result.message
    
    return {"result": response_text}

if __name__ == "__main__":
    app.run()