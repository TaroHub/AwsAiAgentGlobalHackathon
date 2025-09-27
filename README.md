# 政令市条例メーカーレベル政策立案AI v2.0

AWS Bedrock Claude（複数モデル対応）を統合したStrandsAgentによる、市民の意見を議会提出可能レベルの政策提案に変換するAIシステムです。

## システム概要図

```
              市民の意見入力
                  │
                  ▼
┌───────────────────┐
│     Flask Web Application            │
│            (app.py)                  │
└───────────────────┘
                  │
                  ▼
┌─────────────────────┐
│    StrandsAgent v2.0 (AI統合)            │
│  AWS Bedrock Claude (マルチモデル対応)   │
│                                          │
│  ┌─────────────────┐  │
│  │   純粋AI政策分析:                │  │
│  │  • 社会的課題の分析              │  │
│  │  • 住民ニーズの特定              │  │
│  │  • 具体的な条例名と全条文        │  │
│  │  • 詳細な財政計画                │  │
│  │  • 実務運用のポイント            │  │
│  │  • 法律適合性の検証              │  │
│  └─────────────────┘  │
└─────────────────────┘
                  │
                  ▼
┌──────────────────┐
│         議会提出可能レベル         │
│         完全な政策提案             │
│                                    │
│  • 政策提案概要                    │
│  • 政策目的と背景                  │
│  • 条例の基本方針                  │
│  • 条文構成（見出し案）            │
│  • 条文（起草案）- 完全な条例条文  │
│  • 補足事項（実務・財政・留意点）  │
└──────────────────┘
                  │
                  ▼
┌──────────────────┐
│          Web UI表示                │
│      (templates/index.html)        │
└──────────────────┘
```

## Windows PCでの起動手順

### 前提条件
- Python 3.11 以上がインストールされていること
- AWS CLIがインストールされていること
- インターネット接続があること
- AWS アカウントとBedrock Claudeモデルへのアクセス権限

### 1. Python環境の準備

```cmd
# Pythonバージョン確認
python --version

# 仮想環境作成
python -m venv webapp_env

# 仮想環境有効化
webapp_env\Scripts\activate
```

**確認**: プロンプトの前に `(webapp_env)` が表示されていることを確認

### 2. 依存関係のインストール

```cmd
# 必要なPythonパッケージをインストール
pip install -r requirements.txt
```

### 3. AWS認証設定
AWSのCMO環境にて、CloudShellを開き以下のコマンドを実行
aws configure export-credentials

以下の値をメモしておき
 "AccessKeyId":"値"
 "SecretAccessKey:"値"
 "SessionToken":"値"
 


```cmd
# AWS CLIで認証情報を設定
aws configure
```

以下の情報を入力：
- **AWS Access Key ID**: [上記でメモしたアクセスキー]
- **AWS Secret Access Key**: [上記でメモしたシークレットキー]
- **AWS AWS Session Token&&**: [上記でメモしたセッショントークン]
- **Default region name**: `us-west-2` ⚠️ 必須：Claudeモデルが利用可能
- **Default output format**: `json`

### 4. アプリケーション起動

```cmd
python app.py
```

**起動成功時の表示例**:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### 5. ブラウザでアクセス

- ブラウザで以下のURLを開く：
  - `http://127.0.0.1:5000`
  - または `http://localhost:5000`

---

## システムの動作原理 v2.0

### 純粋AI処理フロー

1. **市民意見受付** (Web UI)
   - ユーザーが政策要望をテキストで入力
   - Flask サーバーがリクエストを受信

2. **StrandsAgent AI統合分析** (`StrandsAgent/core.py`)
   ```python
   result = strands_agent.process_citizen_input(citizen_input)
   ```
   - 市民入力を直接AWS Bedrock Claudeモデルに送信
   - AIが完全に0から政策分析を実行
   - テンプレート不使用、純粋AI応答

3. **完全な政策提案生成**
   - 社会的課題の分析
   - 住民ニーズの特定
   - 具体的な条例名と全条文
   - 詳細な財政計画と財源戦略
   - 実務運用のポイント
   - 法律適合性の検証

4. **議会提出可能レベル結果表示** (Web UI)
   - AIが生成した完全な政策提案を表示
   - 政令市条例メーカー相当の専門性

### AI統合の特徴

| 項目 | v1.0 (旧版) | v2.0 (統合版) |
|---|---|---|
| **分析方式** | テンプレート + AI強化 | 純粋AI分析 |
| **コード量** | 600行+ | 200行 |
| **依存関係** | StrandsAgent + BedrockIntegration | StrandsAgent のみ |
| **創造性** | 制限されたテンプレート | 無限のAI創造性 |
| **保守性** | 複雑な依存関係 | シンプルな統合設計 |

---

## 🎨 AI出力の豊富なカスタマイズ方法

このシステムの出力は `StrandsAgent/core.py` を編集することで幅広くカスタマイズできます。

### 📝 主要編集ファイル
```
StrandsAgent/core.py
├── _build_policy_analysis_prompt() (120-199行目) - プロンプト内容
├── _generate_ai_policy_analysis() (73-118行目) - AI設定
└── __init__() (17-23行目) - モデル・リージョン設定
```

### 🎯 基本カスタマイズ

| 要素 | 編集箇所 | デフォルト | カスタマイズ例 |
|---|---|---|---|
| **文量調整** | `max_tokens: 4000` (94行目) | 4000トークン | `8000` (詳細), `2000` (簡潔) |
| **創造性** | `temperature: 0.3` (95行目) | 0.3 (保守的) | `0.8` (創造的), `0.1` (堅実) |
| **AIモデル** | `model_id` (17行目) | Claude 3 Haiku | `claude-3-sonnet`, `claude-3-opus` |
| **リージョン** | `region_name` (17行目) | us-east-1 | `ap-southeast-2`, `eu-west-1` |

### 🏛️ 専門性・役割のカスタマイズ

**現在の設定 (124行目):**
```python
あなたは政令市レベルの政策立案専門家として...
```

**カスタマイズ例:**

| 専門分野 | 設定例 | 出力の特徴 |
|---|---|---|
| **法務専門** | `法制執務のエキスパートとして` | より法的根拠重視 |
| **財政専門** | `自治体財政の専門家として` | 詳細な予算・財源分析 |
| **市民参加重視** | `市民協働の専門家として` | 住民参加手法を重視 |
| **国際比較** | `比較政策学の研究者として` | 海外事例を多用 |
| **デジタル政策** | `デジタル政府の専門家として` | IT・DX要素を強化 |
| **環境政策** | `環境政策の専門家として` | 持続可能性を重視 |

### 📊 出力品質・レベルのカスタマイズ

**現在の設定 (153行目):**
```python
議会提出可能レベルの品質
```

**カスタマイズ例:**

| レベル | 設定 | 出力特徴 |
|---|---|---|
| **学術レベル** | `査読論文レベルの学術性` | 理論的・実証的 |
| **実務重視** | `即座に実行可能なレベル` | 実践的・具体的 |
| **市民向け** | `市民にわかりやすいレベル` | 平易・親しみやすい |
| **国際標準** | `OECD諸国標準レベル` | 国際的視点 |
| **イノベーション** | `先進的・実験的レベル` | 革新的・チャレンジング |

### 🔍 分析深度のカスタマイズ

**詳細要件セクション (139-148行目) への追加例:**

```python
【基本分析】
- 社会的課題の分析
- 住民ニーズの特定
- 国制度との関係性

【詳細分析 (追加例)】
- 国際比較事例の研究
- 長期的社会インパクト評価
- デジタル化・DX対応方針
- ジェンダー・多様性配慮
- 災害・リスク対応策
- 近隣自治体との連携方針
- NPO・民間との協働設計
- 地域経済への波及効果
- 環境・持続可能性評価
- 高齢化社会への対応
```

### 🏗️ 出力構造のカスタマイズ

**JSON構造 (159-194行目) のカスタマイズ例:**

```python
【基本構造】
{
  "政策提案概要": "...",
  "政策目的と背景": {...},
  "条例の基本方針": {...}
}

【カスタマイズ例】
{
  "エグゼクティブサマリー": "1分で読める要約",
  "市民向け説明": "わかりやすい解説",
  "国際比較": "他国の類似政策",
  "リスク分析": "想定される課題",
  "段階的実施計画": "5年間のロードマップ",
  "成功指標": "KPI・測定方法",
  "市民参加手法": "住民との協働方法"
}
```

### ⚙️ 高度なカスタマイズ

**1. 複数の専門家視点 (マルチエージェント風):**
```python
あなたは以下3つの専門家の視点で分析してください：
1. 法制執務の専門家として
2. 財政の専門家として
3. 市民参加の専門家として
```

**2. 特定分野特化:**
```python
# 子育て政策特化
子育て政策の専門家として、保育・教育・労働政策の統合的視点で...

# 高齢者政策特化
高齢者福祉の専門家として、医療・介護・生活支援の包括的視点で...
```

**3. イノベーション重視:**
```python
政策イノベーションの専門家として、従来にない革新的なアプローチを...
```

### 🎲 実験的カスタマイズ

**1. 感情・共感要素:**
```python
市民の感情や生活実感に寄り添った、温かみのある政策提案を...
```

**2. ストーリーテリング:**
```python
政策の効果を具体的な市民の物語で説明する形式で...
```

**3. 数値・データ重視:**
```python
可能な限り定量的データと統計に基づいた客観的分析を...
```

---

## 🤖 Amazon Bedrockモデル・マルチエージェント拡張

### 🔄 Bedrockモデルの変更

**基本的なモデル変更 (17行目):**

```python
# StrandsAgent/core.py の __init__ メソッド
def __init__(self, config: Optional[Dict[str, Any]] = None,
             model_id: str = "anthropic.claude-3-haiku-20240307-v1:0",
             region_name: str = "us-east-1"):
```

**利用可能なモデル例:**

| モデル | model_id | 特徴 | 推奨用途 | 呼び出し方式 |
|---|---|---|---|---|
| **Claude 3 Haiku** | `anthropic.claude-3-haiku-20240307-v1:0` | 高速・軽量 | 基本的な政策分析 | 直接呼び出し |
| **Claude 3 Sonnet** | `anthropic.claude-3-sonnet-20240229-v1:0` | バランス型 | 詳細な政策分析 | 直接呼び出し |
| **Claude 3 Opus** | `anthropic.claude-3-opus-20240229-v1:0` | 最高性能 | 複雑な政策分析 | 直接呼び出し |
| **Claude 3.5 Sonnet** | `anthropic.claude-3-5-sonnet-20240620-v1:0` | 最新・高性能 | プレミアム分析 | Inference Profile |
| **Claude Sonnet 4** | `anthropic.claude-sonnet-4-20250514-v1:0` | 最新・最高性能 | 最高品質分析 | Inference Profile |

**モデル変更例:**
```python
# 高性能モデルに変更（Inference Profile対応）
agent = StrandsAgent(model_id="anthropic.claude-sonnet-4-20250514-v1:0")

# 従来モデル（直接呼び出し）
agent = StrandsAgent(model_id="anthropic.claude-3-haiku-20240307-v1:0")

# 異なるリージョンを使用
agent = StrandsAgent(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region_name="ap-southeast-2"
)
```

### 🔗 マルチエージェントシステムの実装

#### 方法1: 複数エージェントの並列実行

**新しいクラスを作成 (`multi_agent.py`):**

```python
from StrandsAgent import StrandsAgent
import asyncio
import json

class MultiAgentPolicySystem:
    def __init__(self):
        # 専門分野別エージェント
        self.legal_agent = StrandsAgent(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0"
        )
        self.financial_agent = StrandsAgent(
            model_id="anthropic.claude-3-haiku-20240307-v1:0"
        )
        self.implementation_agent = StrandsAgent(
            model_id="anthropic.claude-3-haiku-20240307-v1:0"
        )
        self.evaluation_agent = StrandsAgent(
            model_id="anthropic.claude-3-5-sonnet-20240620-v1:0"
        )

    def analyze_with_multiple_agents(self, citizen_input: str):
        """複数エージェントによる分析"""

        # 1. 基本政策分析
        basic_analysis = self.legal_agent.process_citizen_input(citizen_input)

        # 2. 財政専門分析
        financial_prompt = f"財政専門家として以下の政策を分析: {citizen_input}"
        financial_analysis = self.financial_agent.process_citizen_input(financial_prompt)

        # 3. 実施専門分析
        impl_prompt = f"実施・運用専門家として以下の政策を分析: {citizen_input}"
        implementation_analysis = self.implementation_agent.process_citizen_input(impl_prompt)

        # 4. 評価エージェント
        eval_prompt = f"""
        以下の3つの分析結果を評価・統合してください:

        【法制分析】{json.dumps(basic_analysis, ensure_ascii=False)}
        【財政分析】{json.dumps(financial_analysis, ensure_ascii=False)}
        【実施分析】{json.dumps(implementation_analysis, ensure_ascii=False)}

        最終的な統合政策提案を作成してください。
        """

        final_result = self.evaluation_agent.process_citizen_input(eval_prompt)

        return {
            "legal_analysis": basic_analysis,
            "financial_analysis": financial_analysis,
            "implementation_analysis": implementation_analysis,
            "integrated_result": final_result,
            "multi_agent": True
        }
```

#### 方法2: 役割特化型プロンプト設計

**`StrandsAgent/core.py` を拡張:**

```python
class SpecializedStrandsAgent(StrandsAgent):
    def __init__(self, specialty: str = "general", **kwargs):
        super().__init__(**kwargs)
        self.specialty = specialty
        self.specialty_prompts = {
            "legal": "法制執務の専門家として、条例・規則の起草と法的適合性を重視して",
            "financial": "自治体財政の専門家として、予算・財源・費用対効果を重視して",
            "implementation": "行政実務の専門家として、実施可能性・運用面を重視して",
            "citizen_engagement": "市民参加・協働の専門家として、住民との関係性を重視して",
            "evaluation": "政策評価の専門家として、成果測定・改善サイクルを重視して",
            "innovation": "政策イノベーションの専門家として、革新性・先進性を重視して"
        }

    def _build_policy_analysis_prompt(self, citizen_input: str) -> str:
        specialty_instruction = self.specialty_prompts.get(
            self.specialty,
            "政令市レベルの政策立案専門家として"
        )

        prompt = f"""
{specialty_instruction}、市民の意見を分析し、議会提出可能レベルの政策提案を生成してください。

【市民の意見】
{citizen_input}

【専門性重点】{self.specialty}の観点を特に重視した分析を行ってください。

以下の構成で詳細な政策提案を作成し、JSON形式で回答してください：
...
"""
        return prompt
```

**使用例:**
```python
# 専門エージェント作成
legal_expert = SpecializedStrandsAgent(
    specialty="legal",
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0"
)

financial_expert = SpecializedStrandsAgent(
    specialty="financial",
    model_id="anthropic.claude-3-sonnet-20240229-v1:0"
)

evaluation_expert = SpecializedStrandsAgent(
    specialty="evaluation",
    model_id="anthropic.claude-3-opus-20240229-v1:0"
)
```

#### 方法3: パイプライン型マルチエージェント

**段階的処理システム:**

```python
class PipelineMultiAgent:
    def __init__(self):
        self.agents = {
            "stage1_analysis": StrandsAgent(
                model_id="anthropic.claude-3-haiku-20240307-v1:0"
            ),
            "stage2_elaboration": StrandsAgent(
                model_id="anthropic.claude-3-sonnet-20240229-v1:0"
            ),
            "stage3_refinement": StrandsAgent(
                model_id="anthropic.claude-3-5-sonnet-20240620-v1:0"
            ),
            "stage4_validation": StrandsAgent(
                model_id="anthropic.claude-3-opus-20240229-v1:0"
            )
        }

    def pipeline_analysis(self, citizen_input: str):
        # Stage 1: 基本分析 (高速モデル)
        result1 = self.agents["stage1_analysis"].process_citizen_input(
            f"簡潔に政策の骨格を分析: {citizen_input}"
        )

        # Stage 2: 詳細化 (バランス型モデル)
        result2 = self.agents["stage2_elaboration"].process_citizen_input(
            f"以下の分析を詳細化: {json.dumps(result1, ensure_ascii=False)}"
        )

        # Stage 3: 精緻化 (高性能モデル)
        result3 = self.agents["stage3_refinement"].process_citizen_input(
            f"以下の政策案を精緻化: {json.dumps(result2, ensure_ascii=False)}"
        )

        # Stage 4: 検証・最終化 (最高性能モデル)
        final_result = self.agents["stage4_validation"].process_citizen_input(
            f"""
            政策専門家として以下を最終検証・完成:
            {json.dumps(result3, ensure_ascii=False)}

            法的適合性、実施可能性、財政持続性を最終確認してください。
            """
        )

        return {
            "stage1_basic": result1,
            "stage2_detailed": result2,
            "stage3_refined": result3,
            "stage4_final": final_result,
            "pipeline_processing": True
        }
```

### 🎛️ app.py での統合方法

**マルチエージェントをWebアプリに統合:**

```python
# app.py に追加
from multi_agent import MultiAgentPolicySystem, PipelineMultiAgent

# グローバル変数
strands_agent = None
multi_agent_system = None
pipeline_agent = None

def init_services():
    global strands_agent, multi_agent_system, pipeline_agent

    if strands_agent is None:
        strands_agent = StrandsAgent()

    if multi_agent_system is None:
        multi_agent_system = MultiAgentPolicySystem()

    if pipeline_agent is None:
        pipeline_agent = PipelineMultiAgent()

@app.route('/api/analyze-multi', methods=['POST'])
def analyze_multi_agent():
    """マルチエージェント分析エンドポイント"""
    try:
        init_services()
        data = request.get_json()
        citizen_input = data['prompt']
        analysis_type = data.get('analysis_type', 'standard')

        if analysis_type == 'multi_agent':
            result = multi_agent_system.analyze_with_multiple_agents(citizen_input)
        elif analysis_type == 'pipeline':
            result = pipeline_agent.pipeline_analysis(citizen_input)
        else:
            result = strands_agent.process_citizen_input(citizen_input)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### 📊 性能・コスト最適化

**モデル選択の指針:**

| 用途 | 推奨モデル | 理由 |
|---|---|---|
| **プロトタイプ・開発** | Claude 3 Haiku | 高速・低コスト |
| **本格運用・詳細分析** | Claude 3 Sonnet | バランス重視 |
| **最高品質・複雑分析** | Claude 3.5 Sonnet | 最新・高性能 |
| **学術・研究レベル** | Claude 3 Opus | 最高品質 |

**コスト削減テクニック:**
- Stage 1はHaikuで高速処理
- 重要な部分のみSonnet/Opusを使用
- 並列処理でなく段階的処理でトークン節約

---

## 使用方法

### 基本的な使い方

1. **政策要望を入力**
   ```
   例：「子育て世帯を支援したい」
   例：「こども1人につき、国の補助金と合わせて生涯1000万円を現金で支払う政策を実現したい」
   ```

2. **「政策分析を開始」ボタンをクリック**
   - 処理時間：通常1-3分
   - StrandsAgent分析 → Bedrock AI強化の順で実行

3. **結果確認**
   - **政策提案概要**: 政策の全体像
   - **政策目的と背景**: 社会的課題、住民ニーズ
   - **条例の基本方針**: 制度の狙い、対象、効果
   - **条文構成**: 条例の章立て構造
   - **条文（起草案）**: 実際の条例条文（第1条〜附則）
   - **補足事項**: 実務運用、財政試算、法的留意点

### 高度な使用例

**複雑な政策要望**:
```
高齢者の孤立を防ぐため、地域コミュニティ拠点を各区に設置し、
専門スタッフによる見守りサービスと多世代交流プログラムを実施したい
```

**システムの出力**:
- 具体的な条例名（例：「○○市高齢者地域支援拠点条例」）
- 全条文（目的、定義、市の責務、実施体制等）
- 年間予算試算（人件費、施設費、運営費）
- 段階的実施計画（準備期間、開設スケジュール）

---

## トラブルシューティング

### よくあるエラーと解決方法

#### 1. Bedrock接続エラー
```
ERROR:bedrock_integration:政策分析強化エラー: Unable to locate credentials
```

**原因**: AWS認証情報が未設定または無効

**解決方法**:
```cmd
aws configure
aws sts get-caller-identity  # 認証確認
```

#### 2. リージョンエラー
```
Could not connect to the endpoint URL
```

**原因**: 間違ったリージョン設定

**解決方法**:
```cmd
aws configure set region us-east-1
```

#### 3. Pythonモジュールエラー
```
ModuleNotFoundError: No module named 'flask'
```

**原因**: 仮想環境が無効化されている

**解決方法**:
```cmd
webapp_env\Scripts\activate  # 仮想環境再有効化
pip install -r requirements.txt  # 再インストール
```

#### 4. ポート使用中エラー
```
Address already in use: Port 5000
```

**解決方法**:
- 他のプロセスを停止: `Ctrl+C`
- または別のポートを使用: アプリを再起動

#### 5. StrandsAgent動作確認
```python
# テスト用コード（Python コンソールで実行）
from StrandsAgent import StrandsAgent

# デフォルトモデル（Claude 4 Sonnet）
agent = StrandsAgent()
result = agent.process_citizen_input("テスト")
print(result.keys())  # 政策提案の構造が表示される

# 高性能モデル（Claude Sonnet 4）
agent_advanced = StrandsAgent(model_id="anthropic.claude-sonnet-4-20250514-v1:0")
result_advanced = agent_advanced.process_citizen_input("テスト")
print("高性能モデル動作確認完了")
```

---

## ファイル構成と役割

```
├── README.md                    # このドキュメント
├── app.py                      # Flask Webアプリケーション（メイン）
├── apprunner.yaml             # AWS App Runner設定ファイル
├── Dockerfile                 # コンテナ化用設定
├── AWS_DEPLOY_GUIDE.md        # AWSデプロイ手順書
├── requirements.txt            # Python依存関係定義
├── StrandsAgent/              # 政策分析フレームワーク
│   ├── __init__.py            # パッケージ初期化
│   ├── core.py                # メイン分析ロジック（6フレームワーク）
│   ├── policy_analyzer.py     # 政策分析機能
│   └── ordinance_generator.py # 条例生成機能
└── templates/                 # Web UI
    └── index.html             # メインページ（政策入力・結果表示）
```

### 主要ファイルの役割

- **`app.py`**: Flask Webサーバー、APIエンドポイント、StrandsAgent + Bedrock統合制御
- **`StrandsAgent/core.py`**: Bedrock統合AI政策分析（Inference Profile対応）
- **`apprunner.yaml`**: AWS App Runner用設定ファイル
- **`AWS_DEPLOY_GUIDE.md`**: AWSクラウドデプロイ手順書
- **`templates/index.html`**: ユーザーインターフェース、結果表示ロジック

---

## システム設計思想

### なぜStrandsAgent + Bedrock Claudeなのか？

1. **マルチモデル対応**: 用途に応じて最適なClaudeモデルを選択可能
2. **Inference Profile対応**: 最新の高性能モデル（Claude Sonnet 4等）に対応
3. **専門知識**: Claudeが法律・行政の専門知識を提供
4. **品質保証**: AI統合により議会提出可能レベルを実現
5. **スケーラビリティ**: AWS App Runnerでクラウド展開可能

### 出力品質レベル

- **政令市レベル**: 人口20万人以上の都市で適用可能な制度設計
- **議会提出可能レベル**: 実際の条例案として審議可能な完成度
- **実務対応**: 実際の行政運用を考慮した具体性

---

## 開発・カスタマイズ

### プロンプトのカスタマイズ

`StrandsAgent/core.py` の `_build_policy_analysis_prompt()` メソッドで、Claudeへの指示内容を変更可能：

```python
def _build_policy_analysis_prompt(self, citizen_input: str) -> str:
    prompt = f"""
    あなたは政令市レベルの政策立案専門家として...
    [カスタマイズ可能]
    """
```

### StrandsAgentの機能拡張

`StrandsAgent/core.py` で新しい分析フレームワークを追加可能

### UI/UXの変更

`templates/index.html` でWebインターフェースをカスタマイズ可能

---

このドキュメントを参考に、政策立案AIシステムをご活用ください。