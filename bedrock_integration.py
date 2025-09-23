"""
AWS Bedrock統合モジュール
"""

import json
import boto3
import logging
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError

class BedrockIntegration:
    """AWS Bedrock統合クラス"""

    def __init__(self, region_name: str = "us-east-1"):
        self.region_name = region_name
        self.bedrock_client = None
        self.logger = logging.getLogger(__name__)

    def _get_bedrock_client(self):
        """Bedrockクライアントの取得"""
        if not self.bedrock_client:
            try:
                self.bedrock_client = boto3.client(
                    'bedrock-runtime',
                    region_name=self.region_name
                )
            except Exception as e:
                self.logger.error(f"Bedrockクライアント初期化エラー: {str(e)}")
                raise

        return self.bedrock_client

    def enhance_policy_analysis(self, citizen_input: str, basic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        基本分析結果をBedrockで強化
        """
        try:
            client = self._get_bedrock_client()

            # プロンプト構築
            prompt = self._build_enhancement_prompt(citizen_input, basic_analysis)

            # Claude 3 Haikuを使用
            response = client.invoke_model(
                modelId="anthropic.claude-3-haiku-20240307-v1:0",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 4000,
                    "temperature": 0.3
                })
            )

            response_body = json.loads(response['body'].read())
            enhanced_content = response_body['content'][0]['text']

            # JSON形式で返すように構造化
            try:
                enhanced_analysis = json.loads(enhanced_content)
                return enhanced_analysis
            except json.JSONDecodeError:
                # JSONパースに失敗した場合はテキストとして返す
                return {
                    "enhanced_analysis": enhanced_content,
                    "source": "bedrock_claude_3_haiku"
                }

        except ClientError as e:
            self.logger.error(f"Bedrock API エラー: {e}")
            # Bedrockが利用できない場合は基本分析をそのまま返す
            return basic_analysis
        except Exception as e:
            self.logger.error(f"政策分析強化エラー: {str(e)}")
            return basic_analysis

    def _build_enhancement_prompt(self, citizen_input: str, basic_analysis: Dict[str, Any]) -> str:
        """強化用プロンプトの構築"""

        prompt = f"""
あなたは政令市レベルの政策立案専門家として、市民の意見を分析し、議会提出可能レベルの政策提案を生成してください。
市として実装可能な条例案に落とし込み、そのまま提出できる具体条文化まで含めたパッケージを作成してください。

【市民の意見】
{citizen_input}

【基本分析結果】
{json.dumps(basic_analysis, ensure_ascii=False, indent=2)}

以下の構成で詳細な政策提案を作成し、JSON形式で回答してください：

【必須出力構成】
1. 政策目的と背景
2. 条例の基本方針
3. 条文構成（見出し案）
4. 条文（起草案）- 完全な条例条文
5. 補足事項（実務・財政・留意点）

【詳細要件】
- 社会的課題の分析
- 住民ニーズの特定
- 国制度との関係性
- 具体的な条例名と全条文
- 財政試算と財源戦略
- 実務運用のポイント
- 法律適合性の検証
- 制度設計オプション
- 運用イメージの数値例

【出力要件】
- 必ずJSON形式で出力
- 政令市レベルの専門性を持った内容
- 議会提出可能レベルの品質
- 具体的で実行可能な提案
- 法的根拠を明確化
- 完全な条例条文を含む
- 詳細な財政計画を含む

【重要】以下のJSON構造で必ず出力してください：
{{
  "政策提案概要": "市民意見に対する政策提案の要約",
  "政策目的と背景": {{
    "社会的課題": "...",
    "住民ニーズ": "...",
    "国制度との関係": "..."
  }},
  "条例の基本方針": {{
    "狙い": "...",
    "対象": "...",
    "効果": "..."
  }},
  "条文構成": [
    "目的",
    "定義",
    "市の責務",
    "..."
  ],
  "条文起草案": {{
    "条例名": "...",
    "条文": [
      {{
        "条項": "第1条（目的）",
        "内容": "この条例は..."
      }}
    ]
  }},
  "補足事項": {{
    "実務運用のポイント": "...",
    "財政試算": "...",
    "法律適合性": "...",
    "制度設計オプション": "...",
    "運用イメージ": "..."
  }}
}}

JSON形式で回答してください：
"""

        return prompt

    def generate_ordinance_draft(self, policy_framework: Dict[str, Any]) -> str:
        """
        Bedrockを使用して条例草案を生成
        """
        try:
            client = self._get_bedrock_client()

            prompt = self._build_ordinance_prompt(policy_framework)

            response = client.invoke_model(
                modelId="anthropic.claude-3-haiku-20240307-v1:0",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 4000,
                    "temperature": 0.2
                })
            )

            response_body = json.loads(response['body'].read())
            ordinance_draft = response_body['content'][0]['text']

            return ordinance_draft

        except Exception as e:
            self.logger.error(f"条例草案生成エラー: {str(e)}")
            return "条例草案の生成でエラーが発生しました。"

    def _build_ordinance_prompt(self, policy_framework: Dict[str, Any]) -> str:
        """条例草案生成用プロンプト"""

        prompt = f"""
以下の政策フレームワークに基づいて、政令市レベルの条例草案を生成してください。

【政策フレームワーク】
{json.dumps(policy_framework, ensure_ascii=False, indent=2)}

【条例草案作成要件】
1. 適切な条例名を設定
2. 目的、定義、基本理念を明確化
3. 市・市民・事業者の責務を規定
4. 具体的な施策内容を条文化
5. 推進体制と財政措置を規定
6. 法的整合性を確保

【出力形式】
条例名、各条文を適切な構成で出力してください。

条例草案を生成してください：
"""

        return prompt