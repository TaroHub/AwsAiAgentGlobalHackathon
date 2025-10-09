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
市民意見「{citizen_opinion}」に基づいて、多様な視点を持つ3つの市民エージェントの設定を決定してください。

以下のJSON形式で回答してください：
{{
  "citizen_agent_1": {{
    "name": "エージェント名",
    "age": 年齢,
    "occupation": "職業",
    "family": "家族構成",
    "values": "価値観・関心事",
    "perspective": "この政策への視点",
    "system_prompt": "詳細なシステムプロンプト"
  }},
  "citizen_agent_2": {{
    "name": "エージェント名",
    "age": 年齢,
    "occupation": "職業", 
    "family": "家族構成",
    "values": "価値観・関心事",
    "perspective": "この政策への視点",
    "system_prompt": "詳細なシステムプロンプト"
  }},
  "citizen_agent_3": {{
    "name": "エージェント名",
    "age": 年齢,
    "occupation": "職業",
    "family": "家族構成", 
    "values": "価値観・関心事",
    "perspective": "この政策への視点",
    "system_prompt": "詳細なシステムプロンプト"
  }}
}}

異なる年代・職業・立場の市民を設定し、多角的な評価ができるようにしてください。
"""
    
    result = setup_agent(prompt)
    if isinstance(result.message, dict):
        config_text = result.message['content'][0]['text']
    else:
        config_text = result.message
    
    try:
        citizen_agents_config = json.loads(config_text)
        names = [citizen_agents_config[f"citizen_agent_{i}"]["name"] for i in range(1, 4)]
        return f"市民エージェント設定完了: {', '.join(names)}"
    except:
        citizen_agents_config = {
            "citizen_agent_1": {"name": "一般市民A", "system_prompt": "政策を評価してください。"},
            "citizen_agent_2": {"name": "一般市民B", "system_prompt": "政策を評価してください。"},
            "citizen_agent_3": {"name": "一般市民C", "system_prompt": "政策を評価してください。"}
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

以下の詳細指標で100点満点で評価し、JSON形式で回答してください：

{{
  "citizen_satisfaction": {{
    "positive_reaction_rate": 点数,
    "negative_reaction_rate": 点数,
    "average_satisfaction": 点数,
    "nps_score": 点数
  }},
  "effectiveness": {{
    "feasibility_score": 点数,
    "cost_effectiveness": 点数,
    "risk_assessment": 点数
  }},
  "fairness": {{
    "target_coverage": 点数,
    "inequality_reduction": 点数,
    "gender_regional_balance": 点数
  }},
  "innovation": {{
    "novelty_score": 点数,
    "future_impact": 点数
  }},
  "overall_score": 総合点数,
  "experience_report": "実体験レポート",
  "improvement_suggestions": "改善提案",
  "recommendation": "strongly_recommend/recommend/neutral/not_recommend/strongly_not_recommend"
}}

評価基準:

1. 市民満足度関連指標
- positive_reaction_rate（肯定的反応率）: 好意的意見／全意見の割合
- negative_reaction_rate（否定的反応率）: 否定的意見／全意見の割合（低いほど良い）
- average_satisfaction（平均満足度スコア）: 10段階評価での市民満足度平均
- nps_score（NPS風指標）: 「推奨したい」回答者割合 − 「推奨したくない」回答者割合

2. 実効性・実現可能性関連指標
- feasibility_score（実現可能性評価）: コスト・法制度適合性・実装容易性での採点
- cost_effectiveness（費用対効果スコア）: 市民の期待効果 vs 想定コスト（効率的な施策は高得点）
- risk_assessment（リスク評価スコア）: 副作用や不公平感などの懸念度（低リスクほど高得点）

3. 公平性・包括性関連指標
- target_coverage（対象層カバレッジ）: 施策で恩恵を受ける市民層の広さ
- inequality_reduction（格差是正度）: 弱者・子育て世帯・高齢者など重点層への配慮度合い
- gender_regional_balance（ジェンダー/地域バランス）: 性別・地域間で不均衡を生まないかの評価

4. イノベーション・将来性関連指標
- novelty_score（新規性スコア）: 既存施策との差異や新規アイデア度
- future_impact（将来効果期待度）: 長期的な便益（人口増加、定住促進、財政改善への寄与）
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

以下の詳細指標で100点満点で評価し、JSON形式で回答してください：

{{
  "citizen_satisfaction": {{
    "positive_reaction_rate": 点数,
    "negative_reaction_rate": 点数,
    "average_satisfaction": 点数,
    "nps_score": 点数
  }},
  "effectiveness": {{
    "feasibility_score": 点数,
    "cost_effectiveness": 点数,
    "risk_assessment": 点数
  }},
  "fairness": {{
    "target_coverage": 点数,
    "inequality_reduction": 点数,
    "gender_regional_balance": 点数
  }},
  "innovation": {{
    "novelty_score": 点数,
    "future_impact": 点数
  }},
  "overall_score": 総合点数,
  "experience_report": "実体験レポート",
  "improvement_suggestions": "改善提案",
  "recommendation": "strongly_recommend/recommend/neutral/not_recommend/strongly_not_recommend"
}}

評価基準:

1. 市民満足度関連指標
- positive_reaction_rate（肯定的反応率）: 好意的意見／全意見の割合
- negative_reaction_rate（否定的反応率）: 否定的意見／全意見の割合（低いほど良い）
- average_satisfaction（平均満足度スコア）: 10段階評価での市民満足度平均
- nps_score（NPS風指標）: 「推奨したい」回答者割合 − 「推奨したくない」回答者割合

2. 実効性・実現可能性関連指標
- feasibility_score（実現可能性評価）: コスト・法制度適合性・実装容易性での採点
- cost_effectiveness（費用対効果スコア）: 市民の期待効果 vs 想定コスト（効率的な施策は高得点）
- risk_assessment（リスク評価スコア）: 副作用や不公平感などの懸念度（低リスクほど高得点）

3. 公平性・包括性関連指標
- target_coverage（対象層カバレッジ）: 施策で恩恵を受ける市民層の広さ
- inequality_reduction（格差是正度）: 弱者・子育て世帯・高齢者など重点層への配慮度合い
- gender_regional_balance（ジェンダー/地域バランス）: 性別・地域間で不均衡を生まないかの評価

4. イノベーション・将来性関連指標
- novelty_score（新規性スコア）: 既存施策との差異や新規アイデア度
- future_impact（将来効果期待度）: 長期的な便益（人口増加、定住促進、財政改善への寄与）
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

以下の詳細指標で100点満点で評価し、JSON形式で回答してください：

{{
  "citizen_satisfaction": {{
    "positive_reaction_rate": 点数,
    "negative_reaction_rate": 点数,
    "average_satisfaction": 点数,
    "nps_score": 点数
  }},
  "effectiveness": {{
    "feasibility_score": 点数,
    "cost_effectiveness": 点数,
    "risk_assessment": 点数
  }},
  "fairness": {{
    "target_coverage": 点数,
    "inequality_reduction": 点数,
    "gender_regional_balance": 点数
  }},
  "innovation": {{
    "novelty_score": 点数,
    "future_impact": 点数
  }},
  "overall_score": 総合点数,
  "experience_report": "実体験レポート",
  "improvement_suggestions": "改善提案",
  "recommendation": "strongly_recommend/recommend/neutral/not_recommend/strongly_not_recommend"
}}

評価基準:

1. 市民満足度関連指標
- positive_reaction_rate（肯定的反応率）: 好意的意見／全意見の割合
- negative_reaction_rate（否定的反応率）: 否定的意見／全意見の割合（低いほど良い）
- average_satisfaction（平均満足度スコア）: 10段階評価での市民満足度平均
- nps_score（NPS風指標）: 「推奨したい」回答者割合 − 「推奨したくない」回答者割合

2. 実効性・実現可能性関連指標
- feasibility_score（実現可能性評価）: コスト・法制度適合性・実装容易性での採点
- cost_effectiveness（費用対効果スコア）: 市民の期待効果 vs 想定コスト（効率的な施策は高得点）
- risk_assessment（リスク評価スコア）: 副作用や不公平感などの懸念度（低リスクほど高得点）

3. 公平性・包括性関連指標
- target_coverage（対象層カバレッジ）: 施策で恩恵を受ける市民層の広さ
- inequality_reduction（格差是正度）: 弱者・子育て世帯・高齢者など重点層への配慮度合い
- gender_regional_balance（ジェンダー/地域バランス）: 性別・地域間で不均衡を生まないかの評価

4. イノベーション・将来性関連指標
- novelty_score（新規性スコア）: 既存施策との差異や新規アイデア度
- future_impact（将来効果期待度）: 長期的な便益（人口増加、定住促進、財政改善への寄与）
"""
    
    result = agent(prompt)
    if isinstance(result.message, dict):
        return result.message['content'][0]['text']
    return result.message

@tool
def calculate_final_score(eval1: str, eval2: str, eval3: str) -> str:
    """最終スコア計算"""
    try:
        evaluations = [json.loads(eval1), json.loads(eval2), json.loads(eval3)]
        total_weighted_score = 0
        improvement_points = []
        
        for evaluation in evaluations:
            # 各カテゴリの平均を計算
            citizen_avg = sum(evaluation["citizen_satisfaction"].values()) / 4
            effectiveness_avg = sum(evaluation["effectiveness"].values()) / 3
            fairness_avg = sum(evaluation["fairness"].values()) / 3
            innovation_avg = sum(evaluation["innovation"].values()) / 2
            
            # 重み付き計算
            weighted_score = (
                citizen_avg * 0.4 +
                effectiveness_avg * 0.3 +
                fairness_avg * 0.2 +
                innovation_avg * 0.1
            )
            
            total_weighted_score += weighted_score
            improvement_points.append(evaluation.get("improvement_suggestions", ""))
        
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