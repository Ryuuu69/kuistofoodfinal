# project/backend/api/routers/store.py
from fastapi import APIRouter
from utils.opening_hours import is_open_now_and_next  # <-- import corrigé

router = APIRouter(prefix="/store", tags=["Store"])

@router.get("/status")
def store_status():
    open_now, next_open = is_open_now_and_next()
    return {"open": open_now, "next_open_at": next_open.isoformat() if next_open else None}
