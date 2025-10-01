from flask import Flask, render_template, request, jsonify
import boto3
import json
import uuid
import os
from datetime import datetime

app = Flask(__name__)

# AWS設定
AGENT_RUNTIME_ARN = 'arn:aws:bedrock-agentcore:us-west-2:047786098634:runtime/app-3oJHjL6TFx'
REGION_NAME = 'us-west-2'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_policy():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'success': False, 'error': '入力が空です'})
        
        # boto3セッションとクライアントを作成
        session = boto3.Session(profile_name='default')
        client = session.client('bedrock-agentcore', region_name=REGION_NAME)
        
        # ペイロードを準備
        payload = json.dumps({"prompt": prompt})
        
        # セッションIDを生成（33文字以上必要）
        session_id = str(uuid.uuid4()).replace('-', '') + str(uuid.uuid4()).replace('-', '')[:5]
        
        # エージェントを呼び出し
        response = client.invoke_agent_runtime(
            agentRuntimeArn=AGENT_RUNTIME_ARN,
            runtimeSessionId=session_id,
            payload=payload,
            qualifier="DEFAULT"
        )
        
        # レスポンスを読み取り
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        
        # レスポンスから条例内容を抽出
        result = response_data.get('result', {})
        content = result.get('content', [])
        
        if content and len(content) > 0:
            text_content = content[0].get('text', '')
            
            # 構造化されたデータを作成
            structured_data = {
                'ai_response': text_content,
                'ai_engine': 'Bedrock AgentCore',
                'timestamp': datetime.now().isoformat(),
                'output_quality': '議会提出可能レベル',
                'session_id': session_id
            }
            
            return jsonify({
                'success': True,
                'data': structured_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'レスポンス内容が空です',
                'raw_response': response_data
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'エラー: {str(e)}'
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)