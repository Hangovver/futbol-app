from typing import Dict, Any, List, Tuple
import os, json, time
from backend.apisports import (
    live_all, fixture_events, fixture_stats, fixture_odds, fixture_lineups,
    team_next_and_last, standings, fixture_by_id, last_n_fixtures, head_to_head
)
from backend.localize import localize_team, localize_league
from backend.rules_engine import DEFAULT_LOGO

def _logo(url): return url or DEFAULT_LOGO

# ------------------ Mevcut servisler ------------------

def live_fixtures() -> List[Dict[str,Any]]:
    out = []
    for f in live_all():
        home, away = f.get('teams',{}).get('home',{}), f.get('teams',{}).get('away',{})
        goals = f.get('goals') or {}
        elapsed = f.get('fixture',{}).get('status',{}).get('elapsed')
        out.append({
            "fixtureId": f.get('fixture',{}).get('id'),
            "home": localize_team(home.get('name') or ''),
            "away": localize_team(away.get('name') or ''),
            "score": f"{goals.get('home')} - {goals.get('away')}",
            "elapsed": elapsed,
            "logos": {"home": _logo(home.get('logo')), "away": _logo(away.get('logo'))}
        })
    return out

def match_full_details(fixture_id: int) -> Dict[str,Any]:
    events = fixture_events(fixture_id)
    stats = fixture_stats(fixture_id)
    odds = fixture_odds(fixture_id)
    lineups = fixture_lineups(fixture_id)

    ev = [{
        "time": e.get("time",{}).get("elapsed"),
        "team": e.get("team",{}).get("name"),
        "type": e.get("type"),
        "detail": e.get("detail"),
        "player": (e.get("player") or {}).get("name")
    } for e in events]

    st = {}
    for s in stats:
        team = (s.get("team") or {}).get("name")
        for it in s.get("statistics") or []:
            k = it.get("type"); v = it.get("value")
            st.setdefault(k, {}); st[k][team] = v

    book_odds = []
    for o in odds:
        bk = (o.get("bookmaker") or {}).get("name")
        for m in o.get("bets") or []:
            market = m.get("name")
            for v in m.get("values") or []:
                book_odds.append({"bookmaker": bk, "market": market, "label": v.get("value"), "odd": v.get("odd")})

    lu = []
    for l in lineups:
        tm = (l.get("team") or {}).get("name")
        coach = (l.get("coach") or {}).get("name")
        formation = l.get("formation")
        start = [(x.get("player") or {}).get("name") for x in (l.get("startXI") or [])]
        subs = [(x.get("player") or {}).get("name") for x in (l.get("substitutes") or [])]
        lu.append({"team": tm, "formation": formation, "coach": coach, "startXI": start, "subs": subs})

    return {"events": ev, "stats": st, "odds": book_odds, "lineups": lu}

def team_overview(team_id: int) -> Dict[str,Any]:
    data = team_next_and_last(team_id)
    def simplify(x):
        home, away = x.get('teams',{}).get('home',{}), x.get('teams',{}).get('away',{})
        goals = x.get('goals') or {}
        return {
            "fixtureId": x.get('fixture',{}).get('id'),
            "home": localize_team(home.get('name') or ''),
            "away": localize_team(away.get('name') or ''),
            "score": f"{goals.get('home')} - {goals.get('away')}" if goals.get('home') is not None else None,
            "when": x.get('fixture',{}).get('date','')
        }
    return {"last": [simplify(xx) for xx in data.get("last",[])], "next": [simplify(xx) for xx in data.get("next",[])]}

def calc_implied_for_coupon(selections: List[Dict[str,Any]]):
    legs = []
    prod = 1.0
    for s in selections:
        p = float(s.get("prob") or 0.0)
        p = max(0.0001, min(0.9999, p))
        dec = round(1.0/p, 2)
        prod *= dec
        legs.append({"label": s.get("label"), "prob": round(p,4), "decimal": dec})
    return {"legs": legs, "combinedDecimal": round(prod, 2)}

# ------------------ YENİ: Standings ------------------

def standings_for_fixture(fixture_id:int) -> Dict[str,Any]:
    fix = fixture_by_id(fixture_id)
    if not fix:
        return {"error": True, "code":"NOT_FOUND", "message":"Fixture not found."}
    lg = fix.get("league") or {}
    league_id = lg.get("id"); season = lg.get("season")
    name = lg.get("name") or ""
    round_name = lg.get("round") or ""

    lname = name.lower()
    if any(x in lname for x in ["friendly"]):
        return {"hidden": True, "context":{"competitionType":"friendly","leagueId":league_id,"leagueName":name,"season":season,"group":None}, "rows":[]}

    comp = "league"
    if "champions league" in lname: comp = "ucl"
    elif "europa conference" in lname or "uefa conference" in lname: comp = "uecl"
    elif "europa league" in lname: comp = "uel"

    res = standings(league_id, season)
    rows = []
    group = None
    if res:
        league_obj = (res[0] or {}).get("league",{})
        st_blocks = league_obj.get("standings") or []
        chosen = []
        if isinstance(st_blocks, list) and len(st_blocks)>0:
            if "group" in round_name.lower():
                group = round_name.split()[-1]
                for grp in st_blocks:
                    if grp and (grp[0].get("group") or "").endswith(str(group)):
                        chosen = grp; break
            if not chosen:
                chosen = st_blocks[0]
            for r in chosen:
                team = r.get("team") or {}
                rows.append({
                    "pos": r.get("rank"),
                    "teamId": team.get("id"),
                    "team": localize_team(team.get("name") or ""),
                    "logo": team.get("logo"),
                    "played": r.get("all",{}).get("played"),
                    "win": r.get("all",{}).get("win"),
                    "draw": r.get("all",{}).get("draw"),
                    "loss": r.get("all",{}).get("lose"),
                    "goalsFor": r.get("all",{}).get("goals",{}).get("for"),
                    "goalsAgainst": r.get("all",{}).get("goals",{}).get("against"),
                    "goalDiff": r.get("goalsDiff"),
                    "points": r.get("points"),
                    "form": r.get("form"),
                    "home": r.get("home"), "away": r.get("away")
                })

    return {
        "hidden": False,
        "context": {"competitionType": comp, "leagueId": league_id, "leagueName": name, "season": season, "group": group},
        "rows": rows,
    }

# ------------------ YENİ: Comparison + Form ------------------

def _simplify_fixture(x:dict)->dict:
    home, away = x.get('teams',{}).get('home',{}), x.get('teams',{}).get('away',{})
    goals = x.get('goals') or {}
    return {
        "date": x.get('fixture',{}).get('date',''),
        "home": localize_team(home.get('name') or ''),
        "away": localize_team(away.get('name') or ''),
        "score": { "home": goals.get('home'), "away": goals.get('away') },
        "competition": localize_league((x.get("league") or {}).get("name") or "")
    }

def _wdl_of_match(team_id:int, fx:dict) -> str:
    """W/D/L: takıma göre sonucu çıkar."""
    home = (fx.get("teams") or {}).get("home",{}) or {}
    away = (fx.get("teams") or {}).get("away",{}) or {}
    hg = (fx.get("goals") or {}).get("home")
    ag = (fx.get("goals") or {}).get("away")
    if hg is None or ag is None:
        return "?"
    if team_id == home.get("id"):
        if hg > ag: return "W"
        if hg == ag: return "D"
        return "L"
    if team_id == away.get("id"):
        if ag > hg: return "W"
        if ag == hg: return "D"
        return "L"
    return "?"

def _wdl_list(team_id:int, arr:List[dict]) -> List[str]:
    return [_wdl_of_match(team_id, x) for x in arr][:5]

def comparison_for_fixture(fixture_id:int, n:int=5) -> Dict[str,Any]:
    fix = fixture_by_id(fixture_id)
    if not fix:
        return {"error": True, "code":"NOT_FOUND", "message":"Fixture not found."}
    home = (fix.get("teams") or {}).get("home") or {}
    away = (fix.get("teams") or {}).get("away") or {}
    hid, aid = home.get("id"), away.get("id")

    home_last = last_n_fixtures(hid, venue="", n=n)
    home_home = last_n_fixtures(hid, venue="home", n=n)
    away_last = last_n_fixtures(aid, venue="", n=n)
    away_away = last_n_fixtures(aid, venue="away", n=n)
    h2h = head_to_head(hid, aid, last=n)

    return {
        "fixtureId": fixture_id,
        "home": { "id":hid, "name": localize_team(home.get("name") or ""), "logo": home.get("logo") },
        "away": { "id":aid, "name": localize_team(away.get("name") or ""), "logo": away.get("logo") },
        "lists": {
            "home_last": [ _simplify_fixture(x) for x in home_last ],
            "home_home": [ _simplify_fixture(x) for x in home_home ],
            "away_last": [ _simplify_fixture(x) for x in away_last ],
            "away_away": [ _simplify_fixture(x) for x in away_away ],
            "h2h": [ _simplify_fixture(x) for x in h2h ],
        },
        "meta": {
            "n": n,
            "hasH2H": len(h2h)>0,
            "home_wdl": _wdl_list(hid, home_last),
            "away_wdl": _wdl_list(aid, away_last)
        }
    }

def form_for_fixture(fixture_id:int, n:int=5) -> Dict[str,Any]:
    """Form sekmesi: W/D/L çubukları + son listeler (genel/home-away ayrımı)."""
    cmp = comparison_for_fixture(fixture_id, n=n)
    if cmp.get("error"): return cmp
    hid = cmp["home"]["id"]; aid = cmp["away"]["id"]

    # WDL dizileri
    home_last = cmp["lists"]["home_last"]
    away_last = cmp["lists"]["away_last"]
    home_home = cmp["lists"]["home_home"]
    away_away = cmp["lists"]["away_away"]

    return {
        "fixtureId": fixture_id,
        "home": cmp["home"],
        "away": cmp["away"],
        "wdl": {
            "home_last": _wdl_list(hid, _raw_from_simplified(home_last, hid, aid)),
            "away_last": _wdl_list(aid, _raw_from_simplified(away_last, hid, aid)),
            "home_home": _wdl_list(hid, _raw_from_simplified(home_home, hid, aid)),
            "away_away": _wdl_list(aid, _raw_from_simplified(away_away, hid, aid)),
        },
        "lists": cmp["lists"]
    }

def _raw_from_simplified(lst:List[dict], hid:int, aid:int)->List[dict]:
    """_wdl_of_match ham yapıyı bekliyor; basit dönüştürücü."""
    out=[]
    for x in lst:
        out.append({
            "teams": {"home":{"id":hid}, "away":{"id":aid}},
            "goals": {"home": x.get("score",{}).get("home"), "away": x.get("score",{}).get("away")}
        })
    return out

# ------------------ YENİ: Live Detail özet ------------------

def live_detail(fixture_id:int) -> Dict[str,Any]:
    """Canlı maç için üst kısım özet + mevcut match_full_details birleştirilmiş."""
    fix = fixture_by_id(fixture_id)
    if not fix:
        return {"error": True, "code":"NOT_FOUND", "message":"Fixture not found."}
    sta = (fix.get("fixture") or {}).get("status") or {}
    goals = fix.get("goals") or {}
    halftime = (fix.get("score") or {}).get("halftime") or {}

    base = match_full_details(fixture_id)
    base["header"] = {
        "elapsed": sta.get("elapsed"),
        "status": sta.get("short") or sta.get("long"),
        "score": {"home": goals.get("home"), "away": goals.get("away")},
        "halftime": {"home": halftime.get("home"), "away": halftime.get("away")}
    }
    return base

# ------------------ YENİ: Yorumlar (in-file depolama) ------------------

COMMENTS_DIR = os.path.join(os.path.dirname(__file__), "static", "comments")
os.makedirs(COMMENTS_DIR, exist_ok=True)

def _comments_path(fixture_id:int) -> str:
    return os.path.join(COMMENTS_DIR, f"{fixture_id}.json")

def get_comments(fixture_id:int) -> Dict[str,Any]:
    p = _comments_path(fixture_id)
    if not os.path.exists(p):
        return {"fixtureId": fixture_id, "items": []}
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {"fixtureId": fixture_id, "items": []}
    return data

def add_comment(fixture_id:int, user:str, text:str) -> Dict[str,Any]:
    user = (user or "Anon")[:32]
    text = (text or "").strip()
    if not text:
        return {"error": True, "code":"BAD_REQUEST", "message": "text required"}
    data = get_comments(fixture_id)
    item = {"ts": int(time.time()), "user": user, "text": text[:500]}
    data.setdefault("items", []).append(item)
    p = _comments_path(fixture_id)
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception as e:
        return {"error": True, "code":"IO_ERROR", "message": str(e)}
    return data
