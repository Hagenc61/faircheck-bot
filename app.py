import os
import threading
import time
import tweepy
from flask import Flask, jsonify

app = Flask(__name__)
POLL_SECONDS = int(os.environ.get("POLL_SECONDS", "30"))


def make_client():
    required = ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"]
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise RuntimeError("Missing environment variables: " + ", ".join(missing))
    return tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )


def bot_loop():
    print("FairCheck X bot starting...", flush=True)
    try:
        client = make_client()
        me = client.get_me(user_auth=True)
        bot_id = me.data.id
        print(f"FairCheck X connection OK. Bot user id: {bot_id}", flush=True)
    except Exception as exc:
        print(f"FairCheck X connection failed: {type(exc).__name__}: {exc}", flush=True)
        return

    last_id = None
    while True:
        try:
            response = client.get_users_mentions(
                id=bot_id,
                since_id=last_id,
                max_results=10,
                tweet_fields=["author_id", "created_at", "text"],
                user_auth=True,
            )
            tweets = list(reversed(response.data or []))
            for tweet in tweets:
                last_id = tweet.id
                if tweet.author_id == bot_id:
                    continue
                reply = (
                    "⚽ FairCheck bağlantısı aktif.\n\n"
                    "Pozisyonu IFAB kurallarına göre değerlendirebilmem için "
                    "pozisyon videosunu veya görselini bu gönderiye ekleyin."
                )
                client.create_tweet(text=reply, in_reply_to_tweet_id=tweet.id, user_auth=True)
                print(f"Replied to tweet {tweet.id}", flush=True)
        except Exception as exc:
            print(f"X polling error: {type(exc).__name__}: {exc}", flush=True)
        time.sleep(POLL_SECONDS)


@app.get("/")
def health():
    return jsonify({"service": "FairCheck", "status": "online"})


@app.get("/health")
def health_check():
    return jsonify({"status": "ok"})


@app.get("/callback")
def callback():
    return jsonify({"service": "FairCheck", "message": "X OAuth callback endpoint is ready."})


if __name__ == "__main__":
    threading.Thread(target=bot_loop, daemon=True, name="faircheck-x-bot").start()
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
