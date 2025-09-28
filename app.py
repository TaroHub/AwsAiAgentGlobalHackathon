"""
政策提案システム Flask Webアプリケーション
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# strands-agentsライブラリを使用
from strands import Agent

# Flaskアプリケーション初期化
app = Flask(__name__)
CORS(app)  # CORS設定

# ログディレクトリ作成
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# ロガー設定（コンソールとファイル両方に出力）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'app.log'), encoding='utf-8'),
        logging.StreamHandler()  # コンソール出力も維持
    ]
)
logger = logging.getLogger(__name__)

# グローバル変数でインスタンスを保持
agent = None

def init_services():
    """サービス初期化"""
    global agent

    if agent is None:
        agent = Agent(
            model="us.anthropic.claude-sonnet-4-20250514-v1:0",
            name="PolicyAnalysisAgent"
        )
        logger.info("Strands Agent initialized")

@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_policy():
    """政策分析APIエンドポイント"""
    try:
        # サービス初期化
        init_services()

        # リクエストデータ取得
        data = request.get_json()

        if not data or 'prompt' not in data:
            return jsonify({
                'error': 'プロンプトが指定されていません',
                'statusCode': 400
            }), 400

        citizen_input = data['prompt']
        if not citizen_input.strip():
            return jsonify({
                'error': '有効なプロンプトを入力してください',
                'statusCode': 400
            }), 400

        logger.info(f"政策提案処理開始: {citizen_input[:50]}...")

        # Strands Agentで政策分析を実行
        try:
            prompt = build_policy_prompt(citizen_input)
            result = agent(prompt)
            # AgentResult.messageは辞書形式でcontent配列を持つ
            ai_content = result.message['content'][0]['text']
            
            # レスポンスを構造化
            final_result = {
                "政策提案概要": ai_content,
                "ai_engine": f"Strands Agent ({agent.name})",
                "timestamp": datetime.now().isoformat(),
                "output_quality": "議会提出可能レベル"
            }
            
            logger.info("Strands Agent分析完了")

        except Exception as e:
            logger.error(f"Strands Agent分析でエラー: {str(e)}")
            return jsonify({
                'error': 'AI分析エラー',
                'details': str(e),
                'statusCode': 500
            }), 500

        logger.info("政策提案生成完了")

        return jsonify({
            'success': True,
            'data': final_result,
            'statusCode': 200
        })

    except Exception as e:
        logger.error(f"Flask API エラー: {str(e)}")
        return jsonify({
            'error': '内部サーバーエラー',
            'details': str(e),
            'statusCode': 500
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """ヘルスチェックエンドポイント"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'strands_agent': agent.name if agent else None
        }
    })

@app.errorhandler(404)
def not_found(error):
    """404エラーハンドラー"""
    return jsonify({
        'error': 'Not Found',
        'message': 'リクエストされたリソースが見つかりません',
        'statusCode': 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500エラーハンドラー"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': '内部サーバーエラーが発生しました',
        'statusCode': 500
    }), 500

def build_policy_prompt(citizen_input: str) -> str:
    """政策分析用プロンプトの構築"""
    return f"""
あなたは政令市の法制執務担当職員です。以下の市民意見を受けて、実際の政策文書形式で条例案を作成してください。

【市民の意見】
{citizen_input}

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    logger.info(f"アプリケーション起動開始 - ポート: {port}, デバッグモード: {debug_mode}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )