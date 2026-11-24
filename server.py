import hmac
import os
import threading
import time
from collections import deque

from flask import Flask, jsonify, request

import execute
import installer

v1 = os.environ.get("V1", "")
v2 = int(os.environ.get("PORT", "8080"))
v3 = int(os.environ.get("V8", "60"))
v4 = {v15.strip() for v15 in os.environ.get("V2", "python,node,java,lune,lua,typescript,c,cpp,go,bash,php").split(",") if v15.strip()}
v5 = threading.BoundedSemaphore(int(os.environ.get("V9", "3")))
v6 = deque()
v7 = threading.Lock()
v8 = Flask(__name__)
v8.config["MAX_CONTENT_LENGTH"] = 400000


@v8.get("/")
@v8.get("/health")
def v9():
    return jsonify({"ok": True, "languages": dict(installer.v6), "timeout_s": execute.v1})


def v10():
    v16 = time.time()
    with v7:
        while v6 and v16 - v6[0] > 60:
            v6.popleft()
        if len(v6) >= v3:
            return False
        v6.append(v16)
        return True


def v11(v17):
    def v12():
        if not v1 or not hmac.compare_digest(request.headers.get("X-Runner-Key", ""), v1):
            return jsonify({"ok": False, "error": "unauthorized"}), 401
        if v17 not in v4:
            return jsonify({"ok": False, "error": f"{v17} dang tat"}), 404
        if not execute.v16(v17):
            return jsonify({"ok": False, "error": f"{v17} chua san sang: {installer.v6.get(v17)}"}), 503
        if not v10():
            return jsonify({"ok": False, "error": f"rate limited ({v3}/phut)"}), 429
        v18 = request.get_json(silent=True) or {}
        v19 = v18.get("code")
        if not isinstance(v19, str) or not v19.strip():
            return jsonify({"ok": False, "error": "thieu code"}), 400
        if not v5.acquire(timeout=30):
            return jsonify({"ok": False, "error": "runner ban, thu lai"}), 429
        try:
            return jsonify(execute.v18(v17, v19, str(v18.get("stdin", ""))))
        finally:
            v5.release()

    v12.__name__ = f"r_{v17}"
    return v12


for v14 in execute.v12:
    v8.add_url_rule(f"/{v14}", view_func=v11(v14), methods=["POST"])


@v8.errorhandler(413)
def v13(v20):
    return jsonify({"ok": False, "error": "code qua lon"}), 413


if __name__ == "__main__":
    if len(v1) < 16:
        raise SystemExit("Dat V1 (khoa, >=16 ky tu)")
    installer.v13(v4)
    try:
        from waitress import serve
        serve(v8, host="0.0.0.0", port=v2, threads=8, channel_timeout=420, cleanup_interval=30)
    except ImportError:
        v8.run(host="0.0.0.0", port=v2, threaded=True)
