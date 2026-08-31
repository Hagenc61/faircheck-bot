import os
import threading
from app import app, bot_loop

threading.Thread(target=bot_loop, daemon=True, name="faircheck-x-bot").start()

port = int(os.environ.get("PORT", "10000"))
app.run(host="0.0.0.0", port=port)
