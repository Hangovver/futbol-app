import os, time
from typing import Optional, Dict, Any
from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from backend.rules_engine import get_predictions_today, get_fixtures_today, DEFAULT_MIN_PROB
from backend.services import live_fixtures, match_full_details, team_overview, calc_implied_for_coupon
load_dotenv()

app = FastAPI(title="Football Auto API (Full)", version="5.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/api/health")
def health(): return {"ok": True, "ts": int(time.time())}

@app.get("/api/fixtures")
def fixtures()->Dict[str,Any]:
    items = get_fixtures_today()
    return {"count": len(items), "items": items}

@app.get("/api/leagues")
def leagues()->Dict[str,Any]:
    items = get_fixtures_today()
    leagues = sorted({ i.get("league","") for i in items if i.get("league") })
    return {"count": len(leagues), "items": leagues}

@app.get("/api/predictions")
def predictions(minProb: Optional[float] = Query(None), league: Optional[str] = Query(None))->Dict[str,Any]:
    mp = float(minProb) if (minProb is not None) else DEFAULT_MIN_PROB
    items = get_predictions_today(min_prob=mp)
    if league:
        items = [x for x in items if x.get("league","").lower() == league.lower()]
    return {"count": len(items), "minProb": mp, "items": items}

@app.get("/api/live")
def live():
    return {"items": live_fixtures()}

@app.get("/api/match/{fixture_id}")
def match_api(fixture_id: int):
    return match_full_details(fixture_id)

@app.get("/api/team/{team_id}")
def team_api(team_id: int):
    return team_overview(team_id)

@app.post("/api/implied-odds")
def implied_odds(body: Dict[str, Any] = Body(...)):
    return calc_implied_for_coupon(body.get("selections") or [])
