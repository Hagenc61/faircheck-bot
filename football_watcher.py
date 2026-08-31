# FairCheck football watcher
import os
import time
from datetime import datetime, timedelta, timezone
import requests

TARGET_LEAGUES = {203:"Türkiye Süper Lig",206:"Türkiye Kupası",39:"Premier League",45:"FA Cup",140:"La Liga",143:"Copa del Rey",135:"Serie A",137:"Coppa Italia",78:"Bundesliga",81:"DFB-Pokal",61:"Ligue 1",66:"Coupe de France",2:"UEFA Champions League",3:"UEFA Europa League",848:"UEFA Conference League"}
FOOTBALL_POLL_SECONDS = int(os.environ.get("FOOTBALL_POLL_SECONDS", "1200"))
ENABLE_FOOTBALL_POSTING = os.environ.get("ENABLE_FOOTBALL_POSTING", "false").lower() == "true"
API_URL = "https://v3.football.api-sports.io/fixtures"

def _api_key():
    key = os.environ.get("FOOTBALL_API_KEY")
    if not key:
        raise RuntimeError("Missing environment variable: FOOTBALL_API_KEY")
    return key

def _api(params):
    r = requests.get(API_URL, headers={"x-apisports-key": _api_key()}, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    if data.get("errors"):
        raise RuntimeError(f"API-Football errors: {data['errors']}")
    return data.get("response", [])

def fetch_live():
    return _api({"live":"all"})

def fetch_upcoming(days=1):
    now = datetime.now(timezone.utc)
    fixtures = []
    for i in range(days + 1):
        fixtures.extend(_api({"date":(now + timedelta(days=i)).strftime("%Y-%m-%d")}))
    return fixtures

def is_selected(fixture):
    return (fixture.get("league") or {}).get("id") in TARGET_LEAGUES

def important_event(event):
    event_type = event.get("type", "")
    detail = (event.get("detail") or "").lower()
    return event_type in {"Goal","Card","Var"} or any(x in detail for x in ["penalty","offside","red","var","goal cancelled"])

def event_text(fixture, event):
    teams = fixture.get("teams") or {}
    home = (teams.get("home") or {}).get("name", "Ev sahibi")
    away = (teams.get("away") or {}).get("name", "Deplasman")
    league = (fixture.get("league") or {}).get("name", "")
    tm = event.get("time") or {}
    minute = tm.get("elapsed")
    extra = tm.get("extra")
    minute_text = f"{minute}'" if minute is not None else ""
    if extra:
        minute_text += f"+{extra}"
    typ = event.get("type", "")
    detail = event.get("detail") or ""
    player = (event.get("player") or {}).get("name")
    team = (event.get("team") or {}).get("name")
    if typ == "Goal":
        return f"⚽ {league}\n{minute_text} {home} vs {away}\n{team or ''}: {player or 'Gol'}\n\n📖 IFAB Law 10\nFairCheck: Gol olayı kaydedildi."
    if typ == "Card":
        icon = "🟥" if "red" in detail.lower() else "🟨"
        return f"{icon} {league}\n{minute_text} {home} vs {away}\n{team or ''}: {player or 'Oyuncu'} — {detail}\n\n📖 IFAB Law 12\nFairCheck: Disiplin kararı Law 12 kapsamında değerlendirilir."
    if typ == "Var":
        return f"📺 {league}\n{minute_text} {home} vs {away}\nVAR: {detail}\n\n📖 IFAB VAR Protokolü\nFairCheck: Pozisyon ilgili oyun kuralı ve VAR protokolü kapsamında değerlendirilir."
    return None

def football_loop(x_client=None):
    print("FairCheck football watcher starting...", flush=True)
    if not ENABLE_FOOTBALL_POSTING:
        print("Football posting disabled (ENABLE_FOOTBALL_POSTING=false).", flush=True)
        return
    if x_client is None:
        print("Football watcher has no X client; not posting.", flush=True)
        return
    seen_events = set()
    while True:
        try:
            upcoming = [f for f in fetch_upcoming(1) if is_selected(f)]
            print(f"Football schedule OK. Selected upcoming matches: {len(upcoming)}", flush=True)
            live = [f for f in fetch_live() if is_selected(f)]
            print(f"Football check OK. Active selected matches: {len(live)}", flush=True)
            for fixture in live:
                fixture_id = (fixture.get("fixture") or {}).get("id")
                for event in fixture.get("events") or []:
                    if not important_event(event):
                        continue
                    event_id = f"{fixture_id}:{event.get('time',{}).get('elapsed')}:{event.get('type')}:{event.get('detail')}:{(event.get('player') or {}).get('id')}"
                    if event_id in seen_events:
                        continue
                    text = event_text(fixture, event)
                    if text:
                        x_client.create_tweet(text=text, user_auth=True)
                        seen_events.add(event_id)
                        print(f"Football post created: {event_id}", flush=True)
            if len(seen_events) > 1000:
                seen_events = set(list(seen_events)[-500:])
        except Exception as exc:
            print(f"Football watcher error: {type(exc).__name__}: {exc}", flush=True)
        time.sleep(FOOTBALL_POLL_SECONDS)
