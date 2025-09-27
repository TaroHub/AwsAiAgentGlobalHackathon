"""
政策提案システム Flask Webアプリケーション
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

# AI統合政策分析モジュールを使用
from StrandsAgent import StrandsAgent

# Flaskアプリケーション初期化
app = Flask(__name__)
CORS(app)  # CORS設定

# ロガー設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# グローバル変数でインスタンスを保持
strands_agent = None

def init_services():
    """サービス初期化"""
    global strands_agent

    if strands_agent is None:
        strands_agent = StrandsAgent()
        logger.info("StrandsAgent with integrated AI initialized")

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

        # Bedrock AI分析を実行（pure AIモード）
        use_bedrock = data.get('use_bedrock', True)

        if use_bedrock:
            try:
                # 統合されたStrandsAgentでAI分析を実行
                final_result = strands_agent.process_citizen_input(citizen_input)
                logger.info("StrandsAgent AI分析完了")

            except Exception as e:
                logger.error(f"StrandsAgent AI分析でエラー: {str(e)}")
                return jsonify({
                    'error': 'AI分析エラー',
                    'details': str(e),
                    'statusCode': 500
                }), 500
        else:
            # 統合AIを使用しない場合はエラー
            return jsonify({
                'error': 'テンプレートは削除されました',
                'details': 'use_bedrock=trueを指定してください',
                'statusCode': 400
            }), 400

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
            'strands_agent_with_ai': strands_agent is not None
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

if __name__ == '__main__':
    # 開発用設定
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )