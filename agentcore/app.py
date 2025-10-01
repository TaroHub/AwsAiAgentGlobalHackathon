from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent

app = BedrockAgentCoreApp()
agent = Agent(
    model="us.anthropic.claude-sonnet-4-20250514-v1:0",
    name="PolicyAnalysisAgent"
)

@app.entrypoint
def invoke(payload):
    """政策作成エージェント"""
    user_message = payload.get("prompt", "")
    
    if not user_message:
        return {"error": "プロンプトが必要です"}
    
    # 政策作成プロンプト構築
    prompt = f"""
あなたは政令市の法制執務担当職員です。以下の市民意見を受けて、実際の政策文書形式で条例案を作成してください。

【市民の意見】
{user_message}

以下の形式で条例案を作成してください：

【条例名】
（具体的な条例名を記載）

第一条（目的）
この条例は、（目的を記載）ことを目的とする。

第二条（定義）
この条例において、次の各号に掲げる用語の意義は、当該各号に定めるところによる。
（一）（用語定義）
（二）（用語定義）

第三条以降（具体的な条文）
（必要な条文を順次記載）

附則
この条例は、公布の日から施行する。

【提案理由書】
（条例制定の背景、必要性、期待される効果を記載）

【財政影響調書】
（予算見積もり、財源確保方法、費用対効果を記載）

実際の政策文書として使用できるレベルで作成し、法的根拠や他法令との整合性も考慮してください。
"""
    
    result = agent(prompt)
    return {"result": result.message}

if __name__ == "__main__":
    app.run()