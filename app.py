import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.get("/")
def health():
    return jsonify({"service": "FairCheck", "status": "online"})

@app.get("/health")
def health_check():
    return jsonify({"status": "ok"})

@app.get("/callback")
def callback():
    # OAuth callback endpoint. Full X OAuth flow will be added next.
    return jsonify({
        "service": "FairCheck",
        "message": "X OAuth callback endpoint is ready."
    })

@app.post("/webhook")
def webhook():
    data = request.get_json(silent=True) or {}
    return jsonify({"received": True, "message": "FairCheck webhook ready", "data": data})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
