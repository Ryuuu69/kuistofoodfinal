from __future__ import annotations
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from typing import Dict, Tuple, Optional
from core.config import settings  # <- import corrigé

WEEK = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
def _parse_windows(raw: str) -> Dict[int, Tuple[time, time]]:
    out={}
    for part in [p.strip() for p in raw.split(",") if p.strip()]:
        day, span = part.split(":"); st_s, en_s = span.split("-")
        out[WEEK.index(day[:3])] = (time.fromisoformat(st_s), time.fromisoformat(en_s))
    return out
_WINDOWS = _parse_windows(settings.ORDER_WINDOWS)
_TZ = ZoneInfo(settings.BUSINESS_TIMEZONE)

def is_open_now_and_next(now: Optional[datetime]=None):
    now = now.astimezone(_TZ) if now and now.tzinfo else (now or datetime.now(_TZ))
    dow, tnow = now.weekday(), now.time()
    def span(day:int): return _WINDOWS.get(day, (time(0,0), time(0,0)))
    st, en = span(dow)
    def inside(t, s, e): return (s <= t < e) if e > s else (t >= s or t < e)
    if inside(tnow, st, en) and not settings.FORCE_CLOSED: return True, None
    for i in range(0,8):
        d=(dow+i)%7; s,_=span(d)
        if s==_: continue
        cand=(now+timedelta(days=i)).replace(hour=s.hour, minute=s.minute, second=0, microsecond=0)
        if i==0 and tnow<s: cand=now.replace(hour=s.hour, minute=s.minute, second=0, microsecond=0)
        if cand>=now: return False, cand
    return False, None
