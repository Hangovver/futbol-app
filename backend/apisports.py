import os, requests, datetime, time
from typing import List, Dict, Any
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}

def _get(path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    r = requests.get(BASE + path, params=params, headers=HEADERS, timeout=25)
    r.raise_for_status()
    return r.json()

_cache: Dict[str, Dict[str, Any]] = {}
def _ck(path: str, params: Dict[str,Any]) -> str:
    return path + "|" + "&".join(f"{k}={params[k]}" for k in sorted(params))

def fixtures_today() -> List[dict]:
    d = datetime.date.today().isoformat()
    key = _ck("/fixtures", {"date": d})
    now = time.time()
    if key in _cache and now - _cache[key]["ts"] < 60:
        return _cache[key]["data"]
    data = _get("/fixtures", {"date": d})
    resp = data.get("response", [])
    _cache[key] = {"ts": now, "data": resp}
    return resp

def last_n_fixtures(team_id: int, venue: str, n: int = 5) -> List[dict]:
    params = {"team": team_id, "last": max(n,5), "venue": venue}
    key = _ck("/fixtures", params); now = time.time()
    if key in _cache and now - _cache[key]["ts"] < 60:
        return _cache[key]["data"]
    data = _get("/fixtures", params); resp = data.get("response", [])
    resp = sorted(resp, key=lambda x: x.get("fixture",{}).get("date",""), reverse=True)[:n]
    _cache[key] = {"ts": now, "data": resp}; return resp

def live_all() -> List[dict]:
    data = _get("/fixtures", {"live": "all"})
    return data.get("response", [])

def fixture_events(fixture_id: int) -> List[dict]:
    data = _get("/fixtures/events", {"fixture": fixture_id})
    return data.get("response", [])

def fixture_stats(fixture_id: int) -> List[dict]:
    data = _get("/fixtures/statistics", {"fixture": fixture_id})
    return data.get("response", [])

def fixture_odds(fixture_id: int) -> List[dict]:
    data = _get("/odds", {"fixture": fixture_id})
    return data.get("response", [])

def fixture_lineups(fixture_id: int) -> List[dict]:
    data = _get("/fixtures/lineups", {"fixture": fixture_id})
    return data.get("response", [])

def team_next_and_last(team_id: int) -> Dict[str, Any]:
    last5 = _get("/fixtures", {"team": team_id, "last": 5}).get("response", [])
    next5 = _get("/fixtures", {"team": team_id, "next": 5}).get("response", [])
    return {"last": last5, "next": next5}
