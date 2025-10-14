from flask import Flask, render_template, request, jsonify, Response
import asyncio
import json
from multi_agent_app_enhanced import invoke_async_streaming

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        print(f"[DEBUG] Received prompt: {prompt}")
        
        if not prompt:
            return jsonify({'error': 'プロンプトが必要です'}), 400
        
        def generate():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                async def run_stream():
                    try:
                        async for chunk in invoke_async_streaming({'prompt': prompt}):
                            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                    except Exception as e:
                        error_chunk = {"type": "error", "data": str(e)}
                        yield f"data: {json.dumps(error_chunk, ensure_ascii=False)}\n\n"
                
                gen = run_stream()
                while True:
                    try:
                        result = loop.run_until_complete(gen.__anext__())
                        yield result
                    except StopAsyncIteration:
                        break
                    except Exception as e:
                        import traceback
                        error_detail = f"{str(e)}\n{traceback.format_exc()}"
                        print(f"[ERROR] Stream error: {error_detail}")
                        error_chunk = {"type": "error", "data": str(e), "detail": error_detail}
                        yield f"data: {json.dumps(error_chunk, ensure_ascii=False)}\n\n"
                        break
            except Exception as e:
                import traceback
                error_detail = f"{str(e)}\n{traceback.format_exc()}"
                print(f"[ERROR] Generate error: {error_detail}")
                error_chunk = {"type": "error", "data": str(e), "detail": error_detail}
                yield f"data: {json.dumps(error_chunk, ensure_ascii=False)}\n\n"
            finally:
                loop.close()
        
        return Response(generate(), mimetype='text/event-stream')
    
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"[ERROR] Evaluate endpoint error: {error_detail}")
        return jsonify({'error': str(e), 'detail': error_detail}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
