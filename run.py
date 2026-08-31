import os
import threading
from app import app, bot_loop, make_client
from football_watcher import football_loop

threading.Thread(target=bot_loop, daemon=True, name="faircheck-x-bot").start()


def start_football_watcher():
    try:
        client = make_client()
        football_loop(client)
    except Exception as exc:
        print(f"Football watcher failed to start: {type(exc).__name__}: {exc}", flush=True)


threading.Thread(target=start_football_watcher, daemon=True, name="faircheck-football").start()

port = int(os.environ.get("PORT", "10000"))
app.run(host="0.0.0.0", port=port)
