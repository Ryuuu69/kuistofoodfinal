# project/backend/utils/opening_hours.py
from __future__ import annotations
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from typing import Dict, Tuple, Optional
from core.config import settings  # OK avec 'uvicorn main:app'

WEEK = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def _parse_windows(raw: str) -> Dict[int, Tuple[time, time]]:
    """
    Format attendu (séparés par des virgules) :
      Mon:20:00-02:00, Tue:20:00-02:00, ...
    On split UNIQUEMENT sur le premier ':' pour séparer le jour du créneau.
    """
    out: Dict[int, Tuple[time, time]] = {}
    if not raw:
        return out

    parts = [p.strip() for p in raw.split(",") if p.strip()]
    for part in parts:
        if ":" not in part:
            raise ValueError(f"Fenêtre invalide (pas de ':') : '{part}'")

        day_raw, span = part.split(":", 1)  # <-- le fix est ici
        day = day_raw.strip()[:3].title()   # "Mon", "Tue", ...

        try:
            start_s, end_s = [s.strip() for s in span.split("-", 1)]
            st = time.fromisoformat(start_s)
            en = time.fromisoformat(end_s)
        except Exception as e:
            raise ValueError(f"Fenêtre invalide: '{part}' (attendu 'Mon:20:00-02:00')") from e

        try:
            idx = WEEK.index(day)
        except ValueError as e:
            raise ValueError(f"Jour invalide: '{day_raw}' (utilise Mon,Tue,Wed,Thu,Fri,Sat,Sun)") from e

        out[idx] = (st, en)

    return out

# Valeurs safe par défaut si l'ENV manque
_raw_windows = getattr(settings, "ORDER_WINDOWS", "") or (
    "Mon:20:00-02:00,"
    "Tue:20:00-02:00,"
    "Wed:20:00-02:00,"
    "Thu:20:00-02:00,"
    "Fri:20:00-04:00,"
    "Sat:20:00-04:00,"
    "Sun:20:00-02:00"
)
_WINDOWS = _parse_windows(_raw_windows)

_tz_name = getattr(settings, "BUSINESS_TIMEZONE", "Europe/Paris")
_TZ = ZoneInfo(_tz_name)

def _is_force_closed() -> bool:
    val = getattr(settings, "FORCE_CLOSED", False)
    if isinstance(val, str):
        return val.strip().lower() in {"1", "true", "yes", "on"}
    return bool(val)

def is_open_now_and_next(now: Optional[datetime] = None):
    now = now.astimezone(_TZ) if now and now.tzinfo else (now or datetime.now(_TZ))
    dow, tnow = now.weekday(), now.time()

    def span_for(day: int): 
        return _WINDOWS.get(day, (time(0, 0), time(0, 0)))

    st_today, en_today = span_for(dow)

    def in_span(t: time, st: time, en: time) -> bool:
        # Fenêtre classique
        if en > st:
            return st <= t < en
        # Fenêtre qui passe minuit (ex. 20:00-02:00)
        return t >= st or t < en

    if in_span(tnow, st_today, en_today) and not _is_force_closed():
        return True, None

    # Cherche la prochaine ouverture
    for i in range(0, 8):
        day = (dow + i) % 7
        st, en = span_for(day)
        if st == en:
            continue
        candidate = (now + timedelta(days=i)).replace(hour=st.hour, minute=st.minute, second=0, microsecond=0)
        if i == 0 and tnow < st:
            candidate = now.replace(hour=st.hour, minute=st.minute, second=0, microsecond=0)
        if candidate >= now:
            return False, candidate

    return False, None
