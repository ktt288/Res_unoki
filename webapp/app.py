import json
import os
import queue
import threading
import uuid
from pathlib import Path

from flask import Flask, Response, render_template, request, send_from_directory

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# 実行中タスクのキュー管理
_tasks: dict[str, queue.Queue] = {}

SCREENSHOT_BASE = Path(__file__).parent / 'screenshots'


def _start_task(target, *args):
    task_id = str(uuid.uuid4())
    q: queue.Queue = queue.Queue()
    _tasks[task_id] = q
    thread = threading.Thread(target=target, args=(*args, q), daemon=True)
    thread.start()
    return task_id


# ---------------------------------------------------------------------------
# ルート
# ---------------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/reserve', methods=['POST'])
def api_reserve():
    import automation
    account_text = request.form.get('accounts', '')
    date_text = request.form.get('dates', '')
    task_id = _start_task(automation.run_reserve, account_text, date_text)
    return json.dumps({'task_id': task_id})


@app.route('/api/check', methods=['POST'])
def api_check():
    import automation
    account_text = request.form.get('accounts', '')
    task_id = str(uuid.uuid4())
    q: queue.Queue = queue.Queue()
    _tasks[task_id] = q
    screenshot_dir = str(SCREENSHOT_BASE / task_id)
    thread = threading.Thread(
        target=automation.run_check,
        args=(account_text, screenshot_dir, q),
        daemon=True
    )
    thread.start()
    return json.dumps({'task_id': task_id})


@app.route('/api/winning', methods=['POST'])
def api_winning():
    import automation
    account_text = request.form.get('accounts', '')
    task_id = _start_task(automation.run_winning, account_text)
    return json.dumps({'task_id': task_id})


@app.route('/api/stream/<task_id>')
def stream(task_id):
    q = _tasks.get(task_id)

    if not q:
        return Response(
            'data: {"type":"error","message":"タスクが見つかりません"}\n\n',
            mimetype='text/event-stream'
        )

    def generate():
        while True:
            try:
                msg = q.get(timeout=30)
                yield f'data: {json.dumps(msg, ensure_ascii=False)}\n\n'
                if msg.get('type') == 'done':
                    _tasks.pop(task_id, None)
                    break
            except queue.Empty:
                yield 'data: {"type":"heartbeat"}\n\n'

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
    )


@app.route('/api/screenshot/<task_id>/<filename>')
def screenshot(task_id, filename):
    screenshot_dir = SCREENSHOT_BASE / task_id
    return send_from_directory(screenshot_dir, filename)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
