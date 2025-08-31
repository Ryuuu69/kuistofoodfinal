# project/backend/deps/opening_guard.py
from fastapi import HTTPException
from utils.opening_hours import is_open_now_and_next

def enforce_open_hours():
    open_now, next_open = is_open_now_and_next()
    if not open_now:
        msg = "Commandes fermées pour le moment."
        if next_open:
            msg += " Prochaine ouverture : " + next_open.strftime("%a %H:%M")
        raise HTTPException(status_code=403, detail=msg)
