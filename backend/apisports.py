# backend/apisports.py
from __future__ import annotations

import os
import time
import datetime as dt
from typing import List, Dict, Any, Optional

import requests
from dotenv import load_dotenv
from zoneinfo import ZoneInfo  # Py 3.11+ yerleşik

load_dotenv()

API_KEY = os.getenv("API_FOOTBALL_KEY")
if not API_KEY:
    # Railway/Render'da env yoksa erken ve anlaşılır düşsün
    raise RuntimeError("Missing env var: API_FOOTBALL_KEY")

TZ = os.getenv("TZ", "Europe/Istanbul")
BASE = "https://v3.football.api-sports.io"

# HTTP
DEFAULT_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "25"))
# Basit bellek cache
CACHE_TTL = int(os.getenv("CACHE_TTL", "60"))

_session = requests.Session()
_session.headers.update({"x-apisports-key": API_KEY})

_cache: Dict[str, Dict[str, Any]] = {}


def _ck(path: str, params: Dict[str, Any]) -> str:
    return path + "|" + "&".join(f"{k}={params[k]}" for k in sorted(params))


def _get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    params = dict(params or {})
    # Tarih tabanlı isteklerde timezone ekleyelim (API, date'i bu TZ'ye göre yorumluyor)
    if "date" in params and "timezone" not in params:
        params["timezone"] = TZ

    resp = _session.get(BASE + path, params=params, timeout=DEFAULT_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    # API-FOOTBALL hata alanı varsa yüzeye çıkar
    if isinstance(data, dict) and data.get("errors"):
        err = "; ".join(f"{k}: {v}" for k, v in data["errors"].items())
        raise RuntimeError(f"API error {path}: {err}")

    return data


def fixtures_today() -> List[dict]:
    # "Bugün"ü TR saatine göre hesapla
    today_tr = dt.datetime.now(ZoneInfo(TZ)).date().isoformat()
    key = _ck("/fixtures", {"date": today_tr, "timezone": TZ})
    now = time.time()

    if key in _cache and now - _cache[key]["ts"] < CACHE_TTL:
        return _cache[key]["data"]

    data = _get("/fixtures", {"date": today_tr, "timezone": TZ})
    resp = data.get("response", []) if isinstance(data, dict) else []
    _cache[key] = {"ts": now, "data": resp}
    return resp


def last_n_fixtures(team_id: int, venue: str, n: int = 5) -> List[dict]:
    # API 'venue' için 'home'/'away' bekler
    params = {"team": team_id, "last": max(n, 5), "venue": venue}
    key = _ck("/fixtures", params)
    now = time.time()

    if key in _cache and now - _cache[key]["ts"] < CACHE_TTL:
        return _cache[key]["data"]

    data = _get("/fixtures", params)
    resp = data.get("response", []) if isinstance(data, dict) else []
    # En yeni N taneyi al
    resp = sorted(resp, key=lambda x: x.get("fixture", {}).get("date", ""), reverse=True)[:n]
    _cache[key] = {"ts": now, "data": resp}
    return resp


def live_all() -> List[dict]:
    data = _get("/fixtures", {"live": "all"})
    return data.get("response", []) if isinstance(data, dict) else []


def fixture_events(fixture_id: int) -> List[dict]:
    data = _get("/fixtures/events", {"fixture": fixture_id})
    return data.get("response", []) if isinstance(data, dict) else []


def fixture_stats(fixture_id: int) -> List[dict]:
    data = _get("/fixtures/statistics", {"fixture": fixture_id})
    return data.get("response", []) if isinstance(data, dict) else []


def fixture_odds(fixture_id: int) -> List[dict]:
    data = _get("/odds", {"fixture": fixture_id})
    return data.get("response", []) if isinstance(data, dict) else []


def fixture_lineups(fixture_id: int) -> List[dict]:
    data = _get("/fixtures/lineups", {"fixture": fixture_id})
    return data.get("response", []) if isinstance(data, dict) else []


def team_next_and_last(team_id: int) -> Dict[str, Any]:
    last5 = _get("/fixtures", {"team": team_id, "last": 5}).get("response", [])
    next5 = _get("/fixtures", {"team": team_id, "next": 5}).get("response", [])
    return {"last": last5, "next": next5}
