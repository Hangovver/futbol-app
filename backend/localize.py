import os, json, unicodedata
CACHE_PATH = os.path.join(os.path.dirname(__file__), "names_cache.json")
DEFAULT_MAP = {
    "FC Midtjylland":"Midtjylland","Bayern Munich":"Bayern Münih","Bayern München":"Bayern Münih",
    "FC Copenhagen":"Kopenhag","FC København":"Kopenhag","Kobenhavn":"Kopenhag","Sporting CP":"Sporting Lizbon",
    "Inter Milan":"Inter","Internazionale":"Inter","AC Milan":"Milan","AS Roma":"Roma","Borussia Monchengladbach":"M'gladbach","Borussia Mönchengladbach":"M'gladbach",
    "PSV Eindhoven":"PSV","Athletic Club":"Athletic Bilbao","Bayer Leverkusen":"Leverkusen","1. FC Köln":"Köln","FC Koln":"Köln","Koln":"Köln"
}
CITY_WORD_MAP={"copenhagen":"Kopenhag","kobenhavn":"Kopenhag","köbenhavn":"Kopenhag","munich":"Münih","münchen":"Münih","monchengladbach":"M'gladbach","mönchengladbach":"M'gladbach","koln":"Köln","köln":"Köln"}
TEAM_PREFIXES=["fc ","cf ","sc ","ac ","as ","sv ","fk ","sk ","club "]
def _strip_accents(s): return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
def _norm(s): import re; s=(s or "").strip(); s=re.sub(r"\s+"," ",s); return s
def _load_cache(): 
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH,"r",encoding="utf-8") as f: 
                d=json.load(f); 
                return d if isinstance(d,dict) else {}
        except Exception: return {}
    return {}
def _save_cache(cache: dict):
    try:
        with open(CACHE_PATH,"w",encoding="utf-8") as f: json.dump(cache,f,ensure_ascii=False,indent=2)
    except Exception: pass
def _heuristic(name: str) -> str:
    raw=name or ""; s=("".join(c for c in unicodedata.normalize("NFKD", raw) if not unicodedata.combining(c))).lower()
    for pref in TEAM_PREFIXES:
        if s.startswith(pref): s=s[len(pref):]; break
    for needle,tr in CITY_WORD_MAP.items():
        if needle in s: return tr if len(s.split())==1 else _norm(raw).replace(needle,tr)
    return _norm(raw)
def localize_team(name: str) -> str:
    if not name: return name
    key=_norm(name); cache=_load_cache(); user=cache.get("user_map",{})
    if key in user: return user[key]
    if key in DEFAULT_MAP: return DEFAULT_MAP[key]
    guess=_heuristic(key); cache.setdefault("auto_map",{}); cache["auto_map"][key]=guess; _save_cache(cache); return guess
def localize_league(name: str) -> str: return name
