from fastapi import APIRouter
from project.backend.utils.opening_hours import is_open_now_and_next

router = APIRouter(prefix="/store")

@router.get("/status")
def store_status():
    open_now, next_open = is_open_now_and_next()
    return {"open": open_now, "next_open_at": next_open.isoformat() if next_open else None}
