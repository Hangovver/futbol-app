# backend/services.py
from typing import Dict, Any, List, Optional

from .apisports import (
    live_all,
    fixture_events,
    fixture_stats,
    fixture_odds,
    fixture_lineups,
    team_next_and_last,
)
from .localize import localize_team
from .rules_engine import DEFAULT_LOGO


def _logo(url: Optional[str]) -> str:
    return url or DEFAULT_LOGO


def live_fixtures() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for f in live_all():
        home = f.get("teams", {}).get("home", {})
        away = f.get("teams", {}).get("away", {})
        goals = f.get("goals") or {}
        elapsed = f.get("fixture", {}).get("status", {}).get("elapsed")
        out.append({
            "fixtureId": f.get("fixture", {}).get("id"),
            "home": localize_team(home.get("name") or ""),
            "away": localize_team(away.get("name") or ""),
            "score": f"{goals.get('home')} - {goals.get('away')}",
            "elapsed": elapsed,
            "logos": {"home": _logo(home.get("logo")), "away": _logo(away.get("logo"))},
        })
    return out


def match_full_details(fixture_id: int) -> Dict[str, Any]:
    events = fixture_events(fixture_id)
    stats = fixture_stats(fixture_id)
    odds = fixture_odds(fixture_id)
    lineups = fixture_lineups(fixture_id)

    ev = [{
        "time": e.get("time", {}).get("elapsed"),
        "team": (e.get("team") or {}).get("name"),
        "type": e.get("type"),
        "detail": e.get("detail"),
        "player": (e.get("player") or {}).get("name"),
    } for e in events]

    st: Dict[str, Dict[str, Any]] = {}
    for s in stats:
        team = (s.get("team") or {}).get("name")
        for it in (s.get("statistics") or []):
            k = it.get("type")
            v = it.get("value")
            if k is None:
                continue
            st.setdefault(k, {})
            st[k][team] = v

    book_odds: List[Dict[str, Any]] = []
    for o in odds:
        bk = (o.get("bookmaker") or {}).get("name")
        for m in (o.get("bets") or []):
            market = m.get("name")
            for v in (m.get("values") or []):
                book_odds.append({
                    "bookmaker": bk,
                    "market": market,
                    "label": v.get("value"),
                    "odd": v.get("odd"),
                })

    lu: List[Dict[str, Any]] = []
    for l in lineups:
        tm = (l.get("team") or {}).get("name")
        coach = (l.get("coach") or {}).get("name")
        formation = l.get("formation")
        start = [(x.get("player") or {}).get("name") for x in (l.get("startXI") or [])]
        subs = [(x.get("player") or {}).get("name") for x in (l.get("substitutes") or [])]
        lu.append({
            "team": tm,
            "formation": formation,
            "coach": coach,
            "startXI": start,
            "subs": subs,
        })

    return {"events": ev, "stats": st, "odds": book_odds, "lineups": lu}


def team_overview(team_id: int) -> Dict[str, Any]:
    data = team_next_and_last(team_id)

    def simplify(x: Dict[str, Any]) -> Dict[str, Any]:
        home = x.get("teams", {}).get("home", {})
        away = x.get("teams", {}).get("away", {})
        goals = x.get("goals") or {}
        return {
            "fixtureId": x.get("fixture", {}).get("id"),
            "home": localize_team(home.get("name") or ""),
            "away": localize_team(away.get("name") or ""),
            "score": f"{goals.get('home')} - {goals.get('away')}" if goals.get("home") is not None else None,
            "when": x.get("fixture", {}).get("date", ""),
        }

    return {
        "last": [simplify(xx) for xx in (data.get("last") or [])],
        "next": [simplify(xx) for xx in (data.get("next") or [])],
    }


def calc_implied_for_coupon(selections: List[Dict[str, Any]]) -> Dict[str, Any]:
    legs: List[Dict[str, Any]] = []
    prod = 1.0
    for s in selections:
        p = float(s.get("prob") or 0.0)
        p = max(0.0001, min(0.9999, p))
        dec = round(1.0 / p, 2)
        prod *= dec
        legs.append({"label": s.get("label"), "prob": round(p, 4), "decimal": dec})
    return {"legs": legs, "combinedDecimal": round(prod, 2)}
