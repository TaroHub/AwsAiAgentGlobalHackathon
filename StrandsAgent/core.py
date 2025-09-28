"""
Strands Agents SDKを使用したシンプルなラッパー
"""

from strands import BedrockModel, Agent

class StrandsAgent:
    """
    Strands SDKを使用したシンプルなエージェント
    """
    
    def __init__(self):
        self.model = BedrockModel(
            model_id="anthropic.claude-sonnet-4-20250514-v1:0",
            region="us-west-2"
        )
        self.agent = Agent(model=self.model)
    
    def process_citizen_input(self, input_text: str) -> dict:
        """市民意見を処理して政策提案を生成"""
        prompt = f"""
あなたは政令市レベルの政策立案専門家です。以下の市民意見を分析し、議会提出可能レベルの政策提案を生成してください。

【市民の意見】
{input_text}

以下の構成で政策提案を作成してください：
1. 政策目的と背景
2. 条例の基本方針
3. 条文構成案
4. 実施方法
5. 財政計画

具体的で実行可能な提案をお願いします。
"""
        
        response = self.agent.invoke(prompt)
        return {
            "政策提案概要": response,
            "ai_engine": "Strands Agents Bedrock Claude Sonnet 4",
            "output_quality": "議会提出可能レベル"
        }