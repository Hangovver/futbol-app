import os
from typing import List, Dict, Any
import pytz
from dotenv import load_dotenv
from apisports import fixtures_today, last_n_fixtures
from localize import localize_team, localize_league
load_dotenv()
TZ = os.getenv("TZ","Europe/Istanbul")
DEFAULT_MIN_PROB = float(os.getenv("MIN_PROB","0.70"))
DEFAULT_LOGO = "/static/default_logo.png"

def _goals(m):
    g = m.get("goals") or {}
    return g.get("home"), g.get("away")

def _derive_booleans(team_id: int, venue: str, n: int = 5):
    matches = last_n_fixtures(team_id, venue, n)
    out = {"team_ge1":[], "team_ge2":[], "team_ge3":[], "tot_ge2":[], "tot_ge3":[], "tot_ge4":[], "btts":[], "win":[], "draw":[], "not_lose":[], "sample":0}
    for m in matches:
        hg, ag = _goals(m)
        if hg is None or ag is None: 
            continue
        out["sample"] += 1
        is_home = (m.get("teams",{}).get("home",{}).get("id") == team_id)
        tg = hg if is_home else ag; og = ag if is_home else hg
        out["team_ge1"].append((tg or 0) >= 1)
        out["team_ge2"].append((tg or 0) >= 2)
        out["team_ge3"].append((tg or 0) >= 3)
        tot = (hg or 0) + (ag or 0)
        out["tot_ge2"].append(tot >= 2)
        out["tot_ge3"].append(tot >= 3)
        out["tot_ge4"].append(tot >= 4)
        out["btts"].append((tg or 0) >= 1 and (og or 0) >= 1)
        home_w = m.get("teams",{}).get("home",{}).get("winner")
        away_w = m.get("teams",{}).get("away",{}).get("winner")
        if is_home:
            out["win"].append(home_w is True); out["draw"].append(home_w is None and (hg==ag)); out["not_lose"].append((home_w is True) or (hg==ag))
        else:
            out["win"].append(away_w is True); out["draw"].append(away_w is None and (hg==ag)); out["not_lose"].append((away_w is True) or (hg==ag))
    return out

def _ratio(arr): return round((sum(1 for x in arr if x)/len(arr)) if arr else 0.0, 4)
def _both_min(a,b): return min(_ratio(a), _ratio(b))

def _tr_time(iso):
    tz = pytz.timezone(TZ); import datetime as dt
    dtv = dt.datetime.fromisoformat(iso.replace("Z","+00:00")).astimezone(tz)
    return dtv.strftime("%d.%m.%Y %H:%M")

def _labelize(team): return localize_team(team.get("name") or "")
def _logo(url): return url or DEFAULT_LOGO

def get_fixtures_today() -> List[Dict[str,Any]]:
    items = []
    for f in fixtures_today():
        home, away = f.get("teams",{}).get("home",{}), f.get("teams",{}).get("away",{})
        items.append({
            "fixtureId": f.get("fixture",{}).get("id"),
            "league": localize_league(f.get("league",{}).get("name") or ""),
            "country": f.get("league",{}).get("country") or "",
            "homeId": home.get("id"), "awayId": away.get("id"),
            "home": _labelize(home), "away": _labelize(away),
            "whenTR": _tr_time(f.get("fixture",{}).get("date","")),
            "logos": {"home": _logo(home.get("logo")), "away": _logo(away.get("logo"))},
        })
    return items

def get_predictions_today(min_prob: float = DEFAULT_MIN_PROB) -> List[Dict[str,Any]]:
    out = []
    for f in fixtures_today():
        home, away = f.get("teams",{}).get("home",{}), f.get("teams",{}).get("away",{})
        hid, aid = home.get("id"), away.get("id")
        if not hid or not aid: 
            continue
        H = _derive_booleans(hid, "home", 5); A = _derive_booleans(aid, "away", 5)
        probs = {}
        probs["HOME_O0.5"] = _ratio(H["team_ge1"]); probs["HOME_O1.5"] = _ratio(H["team_ge2"]); probs["HOME_O2.5"] = _ratio(H["team_ge3"])
        probs["AWAY_O0.5"] = _ratio(A["team_ge1"]); probs["AWAY_O1.5"] = _ratio(A["team_ge2"]); probs["AWAY_O2.5"] = _ratio(A["team_ge3"])
        probs["O1.5"] = _both_min(H["tot_ge2"], A["tot_ge2"]); probs["O2.5"] = _both_min(H["tot_ge3"], A["tot_ge3"]); probs["O3.5"] = _both_min(H["tot_ge4"], A["tot_ge4"])
        probs["BTTS"] = _both_min(H["btts"], A["btts"]); probs["BTTS_AND_O2.5"] = min(probs["BTTS"], probs["O2.5"])
        probs["MS1"] = _ratio(H["win"]); probs["MS2"] = _ratio(A["win"]); probs["MSX"] = _both_min(H["draw"], A["draw"])
        probs["DC_1X"] = _ratio(H["not_lose"]); probs["DC_X2"] = _ratio(A["not_lose"]); probs["DC_12"] = min(_ratio(H["win"]), _ratio(A["win"]))
        probs["DNB1"] = _ratio(H["win"]); probs["DNB2"] = _ratio(A["win"])
        filtered = {}
        for k, v in probs.items():
            if v >= min_prob:
                if k.startswith("U") or "_U" in k: continue
                filtered[k] = round(v, 2)
        if not filtered: continue
        top_key, top_p = max(probs.items(), key=lambda kv: kv[1])
        out.append({
            "fixtureId": f.get("fixture",{}).get("id"),
            "league": localize_league(f.get("league",{}).get("name") or ""),
            "country": f.get("league",{}).get("country") or "",
            "homeId": hid, "awayId": aid,
            "home": _labelize(home), "away": _labelize(away),
            "whenTR": _tr_time(f.get("fixture",{}).get("date","")),
            "topPick": {"bet": top_key, "p": round(top_p,2)},
            "probs": dict(sorted(filtered.items(), key=lambda kv: -kv[1])),
            "logos": {"home": _logo(home.get("logo")), "away": _logo(away.get("logo"))},
            "samples": {"home": H["sample"], "away": A["sample"]},
        })
    out.sort(key=lambda x: x["topPick"]["p"], reverse=True)
    return out
