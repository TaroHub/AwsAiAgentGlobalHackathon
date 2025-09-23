# 政令市条例メーカーレベル政策立案AI

StrandsAgentとAWS Bedrock Claude 3 Haikuを統合した、市民の意見を議会提出可能レベルの政策提案に変換するWebアプリケーションです。

## システム概要図

```
              市民の意見入力
                  │
                  ▼
┌───────────────────┐
│         Flask Web Application        │
│              (app.py)                │
└───────────────────┘
                  │
                  ▼
┌─────────────────────┐
│          StrandsAgent                    │
│        (基本政策分析)                    │
│                                          │
│  ┌─────────────────┐  │
│  │   6つのフレームワーク分析        │  │
│  │  1. 市民意見分析                 │  │
│  │  2. 政策設計フレームワーク       │  │
│  │  3. 法制・制度的フレームワーク   │  │
│  │  4. 財政持続可能性計画           │  │
│  │  5. 実施・執行計画               │  │
│  │  6. 効果測定・評価               │  │
│  └─────────────────┘  │
└─────────────────────┘
                  │ 基本分析結果
                  ▼
┌────────────────────┐
│       AWS Bedrock Claude 3 Haiku       │
│          (AI分析強化)                  │
│                                        │
│  ┌────────────────┐  │
│  │  StrandsAgentの結果を強化:     │  │
│  │  • 詳細な条例条文生成          │  │
│  │  • 専門的な財政試算            │  │
│  │  • 具体的な実務運用手順        │  │
│  │  • 法的根拠の詳細化            │  │
│  └────────────────┘  │
└────────────────────┘
                  │ 強化された分析結果
                  ▼
┌──────────────────┐
│           統合結果                 │
│     (議会提出可能レベル)           │
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
- インターネット接続があること
- AWS アカウントとBedrock Claude 3 Haikuへのアクセス権限

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

```cmd
# AWS CLIで認証情報を設定
aws configure
```

以下の情報を入力：
- **AWS Access Key ID**: [あなたのアクセスキー]
- **AWS Secret Access Key**: [あなたのシークレットキー]
- **Default region name**: `us-east-1` ⚠️ 必須：Claude 3 Haikuが利用可能
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

## システムの動作原理

### 処理フロー詳細

1. **市民意見受付** (Web UI)
   - ユーザーが政策要望をテキストで入力
   - Flask サーバーがリクエストを受信

2. **StrandsAgent基本分析** (`StrandsAgent/core.py`)
   ```python
   basic_result = strands_agent.process_citizen_input(citizen_input)
   ```
   - キーワードベースの政策分類
   - 6つのフレームワークでの構造化分析
   - 基本的な政策骨格を生成

3. **Bedrock AI強化** (`bedrock_integration.py`)
   ```python
   enhanced_result = bedrock_integration.enhance_policy_analysis(citizen_input, basic_result)
   ```
   - StrandsAgentの基本分析結果を入力として使用
   - Claude 3 Haikuが専門知識で詳細化
   - 具体的な条例条文、財政計画を生成

4. **統合結果表示** (Web UI)
   - StrandsAgent + AI強化の統合結果を表示
   - 政令市レベル・議会提出可能レベルの品質

### StrandsAgent の 6つのフレームワーク

| フレームワーク | 機能 | 出力例 |
|---|---|---|
| **市民意見分析** | 核心的関心事項の特定 | 背景課題、影響市民層 |
| **政策設計フレームワーク** | 制度設計の基本構造 | 政策名称、目標成果 |
| **法制・制度的フレームワーク** | 法的根拠と条例構造 | 条例名、章立て |
| **財政持続可能性計画** | 予算・財源戦略 | 費用便益分析、収入戦略 |
| **実施・執行計画** | 段階的展開スケジュール | 実施フェーズ、運営体制 |
| **効果測定・評価** | 成果指標と評価手法 | KPI、フィードバック仕組み |

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
agent = StrandsAgent()
result = agent.process_citizen_input("テスト")
print(result.keys())  # 6つのフレームワークが表示されるはず
```

---

## ファイル構成と役割

```
├── README.md                    # このドキュメント
├── app.py                      # Flask Webアプリケーション（メイン）
├── bedrock_integration.py      # AWS Bedrock統合モジュール
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
- **`bedrock_integration.py`**: AWS Bedrock Claude 3 Haikuとの通信、プロンプト管理
- **`StrandsAgent/core.py`**: 6つのフレームワークによる基本政策分析
- **`templates/index.html`**: ユーザーインターフェース、結果表示ロジック

---

## システム設計思想

### なぜStrandsAgent + Claude 3 Haikuなのか？

1. **構造化分析**: StrandsAgentが政策の基本構造を整理
2. **専門知識**: Claude 3 Haikuが法律・行政の専門知識を提供
3. **品質保証**: 両方の組み合わせで議会提出可能レベルを実現
4. **スケーラビリティ**: 将来的な機能拡張への対応

### 出力品質レベル

- **政令市レベル**: 人口20万人以上の都市で適用可能な制度設計
- **議会提出可能レベル**: 実際の条例案として審議可能な完成度
- **実務対応**: 実際の行政運用を考慮した具体性

---

## 開発・カスタマイズ

### プロンプトのカスタマイズ

`bedrock_integration.py` の `_build_enhancement_prompt()` メソッドで、Claude 3 Haikuへの指示内容を変更可能：

```python
def _build_enhancement_prompt(self, citizen_input: str, basic_analysis: Dict[str, Any]) -> str:
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