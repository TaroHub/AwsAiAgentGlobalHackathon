"""
StrandsAgent コアモジュール
"""

import json
import logging
import boto3
from typing import Dict, Any, Optional
from datetime import datetime
from botocore.exceptions import ClientError

class StrandsAgent:
    """
    政策提案システムのコアエージェント
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, model_id: str = "claude-sonnet-4", region_name: str = "us-west-2"):
        self.config = config or {}
        self.version = "1.0.0"
        self.model_id = model_id
        self.region_name = region_name
        self.bedrock_client = None
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """ロガーの設定"""
        logger = logging.getLogger("StrandsAgent")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

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

    def process_citizen_input(self, input_text: str) -> Dict[str, Any]:
        """
        市民の意見を処理し、AI による政策提案を生成する
        """
        self.logger.info(f"市民意見の処理開始: {input_text[:50]}...")

        # AI による直接的な政策分析
        ai_analysis = self._generate_ai_policy_analysis(input_text)

        result = {
            **ai_analysis,
            "agent": "StrandsAgent with Integrated AI",
            "version": self.version,
            "expertise_level": "政令市条例メーカー相当",
            "output_quality": "議会提出可能レベル",
            "ai_engine": f"Bedrock {self.model_id}",
            "timestamp": datetime.now().isoformat()
        }

        self.logger.info("AI政策提案生成完了")
        return result

    def _generate_ai_policy_analysis(self, citizen_input: str) -> Dict[str, Any]:
        """
        AIによる政策分析の生成
        """
        try:
            client = self._get_bedrock_client()

            # プロンプト構築
            prompt = self._build_policy_analysis_prompt(citizen_input)

            # モデルIDに応じてInference Profileを使用
            if "claude-sonnet-4" in self.model_id:
                # Claude Sonnet 4用の正しいInference Profile ID
                inference_profile_id = "us.anthropic.claude-sonnet-4-20250514-v1:0"
                response = client.invoke_model(
                    modelId=inference_profile_id,
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
            elif "claude-3-5-sonnet" in self.model_id:
                # Claude 3.5 Sonnet用のInference Profile ID
                inference_profile_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
                response = client.invoke_model(
                    modelId=inference_profile_id,
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
            else:
                # 従来のモデル（Claude 3 Haiku等）- 直接呼び出し
                response = client.invoke_model(
                    modelId=self.model_id,
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
            ai_content = response_body['content'][0]['text']

            # JSON形式で返すように構造化
            try:
                # コードブロック形式の場合は中身を抽出
                if ai_content.strip().startswith('```json'):
                    # ```json と ``` を除去
                    json_content = ai_content.strip()
                    json_content = json_content.replace('```json', '').replace('```', '').strip()
                    ai_analysis = json.loads(json_content)
                else:
                    ai_analysis = json.loads(ai_content)
                return ai_analysis
            except json.JSONDecodeError:
                # JSONパースに失敗した場合はテキストとして返す
                return {
                    "政策提案概要": ai_content,
                    "source": "bedrock_integrated_analysis"
                }

        except ClientError as e:
            self.logger.error(f"Bedrock API エラー: {e}")
            raise
        except Exception as e:
            self.logger.error(f"AI政策分析エラー: {str(e)}")
            raise

    def _build_policy_analysis_prompt(self, citizen_input: str) -> str:
        """政策分析用プロンプトの構築"""

        prompt = f"""
あなたは政令市レベルの政策立案専門家として、市民の意見を分析し、議会提出可能レベルの政策提案を生成してください。
市として実装可能な条例案に落とし込み、そのまま提出できる具体条文化まで含めたパッケージを作成してください。

【市民の意見】
{citizen_input}

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

