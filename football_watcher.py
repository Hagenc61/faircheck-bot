import os
import time
from datetime import datetime, timezone

import requests

# Selected major leagues + Turkey. API-Football league IDs.
TARGET_LEAGUES = {
    203: "Türkiye Süper Lig",
    206: "Türkiye Kupası",
    39: "Premier League",
    45: "FA Cup",
    140: "La Liga",
    143: "Copa del Rey",
    135: "Serie A",
    137: "Coppa Italia",
    78: "Bundesliga",
    81: "DFB-Pokal",
    61: "Ligue 1",
    66: "Coupe de France",
    2: "UEFA Champions League",
    3: "UEFA Europa League",
    848: "UEFA Conference League",
}

# Keep below the Free plan's 100 requests/day. 20 minutes = 72 calls/day.
FOOTBALL_POLL_SECONDS = int(os.environ.get("FOOTBALL_POLL_SECONDS", "1200"))
ENABLE_FOOTBALL_POSTING = os.environ.get("ENABLE_FOOTBALL_POSTING", "false").lower() == "true"
API_URL = "https://v3.football.api-sports.io/fixtures"


def _api_key():
    key = os.environ.get("FOOTBALL_API_KEY")
    if not key:
        raise RuntimeError("Missing environment variable: FOOTBALL_API_KEY")
    return key


def _event_text(fixture, event):
    teams = fixture.get("teams") or {}
    home = (teams.get("home") or {}).get("name", "Ev sahibi")
    away = (teams.get("away") or {}).get("name", "Deplasman")
    minute = (event.get("time") or {}).get("elapsed")
    extra = (event.get("time") or {}).get("extra")
    minute_text = f"{minute}'" if minute is not None else ""
    if extra:
        minute_text += f"+{extra}"

    event_type = event.get("type", "")
    detail = event.get("detail") or ""
    player = (event.get("player") or {}).get("name")
    team = (event.get("team") or {}).get("name")

    if event_type == "Goal":
        return f"⚽ {minute_text} {home} {home and 'vs'} {away}\n{team or ''}: {player or 'Gol'}\n\nFairCheck: Gol kararı."
    if event_type == "Card":
        icon = "🟥" if "Red" in detail else "🟨"
        return f"{icon} {minute_text} {home} vs {away}\n{team or ''}: {player or 'Oyuncu'} — {detail}\n\n📖 IFAB Law 12 – Fouls and Misconduct\nFairCheck: Disiplin kararı ilgili Law 12 kriterleri kapsamında değerlendirilir."
    if event_type == "subst":
        return f"🔄 {minute_text} {home} vs {away}\n{team or ''}: oyuncu değişikliği\n\n📖 IFAB Law 3 – The Players\nFairCheck: Oyuncu değişikliği Law 3 kapsamında."
    if event_type == "Var":
        return f"📺 {minute_text} {home} vs {away}\nVAR: {detail}\n\n📖 IFAB Law 5/6 + ilgili oyun kuralı\nFairCheck: VAR incelemesi ilgili olayın kuralı ve VAR protokolü kapsamında değerlendirilir."
    return None


def _important(event):
    event_type = event.get("type", "")
    detail = (event.get("detail") or "").lower()
    if event_type in {"Goal", "Card", "Var"}:
        return True
    if event_type == "subst":
        return False
    return any(x in detail for x in ["penalty", "offside", "red", "var", "goal cancelled"])


def _load_seen():
    return set((os.environ.get("FOOTBALL_SEEN", "")).split(",")) - {""}


def _save_seen(seen):
    # Keep only a bounded in-memory set; this is intentionally not persistent.
    if len(seen) > 500:
        return set(list(seen)[-250:])
    return seen


def fetch_live():
    response = requests.get(
        API_URL,
        headers={"x-apisports-key": _api_key()},
        params={"live": "all"},
        timeout=20,
    )
    response.raise_for_status()
    return response.json().get("response", [])


def football_loop(x_client=None):
    print("FairCheck football watcher starting...", flush=True)
    if not ENABLE_FOOTBALL_POSTING:
        print("Football posting disabled (ENABLE_FOOTBALL_POSTING=false).", flush=True)
        return
    if x_client is None:
        print("Football watcher has no X client; not posting.", flush=True)
        return

    seen = set()
    while True:
        try:
            fixtures = fetch_live()
            target_count = 0
            for fixture in fixtures:
                league = fixture.get("league") or {}
                league_id = league.get("id")
                if league_id not in TARGET_LEAGUES:
                    continue
                target_count += 1
                events = fixture.get("events") or []
                for event in events:
                    if not _important(event):
                        continue
                    fixture_id = (fixture.get("fixture") or {}).get("id")
                    event_id = f"{fixture_id}:{event.get('time', {}).get('elapsed')}:{event.get('type')}:{event.get('detail')}:{(event.get('player') or {}).get('id')}"
                    if event_id in seen:
                        continue
                    text = _event_text(fixture, event)
                    if not text:
                        continue
                    x_client.create_tweet(text=text, user_auth=True)
                    seen.add(event_id)
                    print(f"Football post created: {event_id}", flush=True)
            seen = _save_seen(seen)
            print(f"Football check OK. Active selected matches: {target_count}", flush=True)
        except Exception as exc:
            print(f"Football watcher error: {type(exc).__name__}: {exc}", flush=True)
        time.sleep(FOOTBALL_POLL_SECONDS)
