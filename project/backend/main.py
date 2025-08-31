# project/backend/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database.session import async_engine
from database.base import Base

from api.routers import api_router
from api.routers.stripe_webhook import router as stripe_webhook_router
from api.routers.store import router as store_router  # /store/status
from utils.opening_hours import is_open_now_and_next  # statut ouvert/fermé

app = FastAPI(
    title="Restaurant API",
    description="API backend for a restaurant management system.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://krokburger.fr",
        "https://www.krokburger.fr",
        "http://localhost:8000",
        "https://localhost:5173",
        "https://localhost:8000",
    ],
    allow_origin_regex=r"https://.*\.gitpod\.io$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=86400,
)

# --- Création des tables au démarrage (dev) ---
@app.on_event("startup")
async def create_db_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# --- Middleware: bloque les écritures /api/orders* hors horaires ---
@app.middleware("http")
async def close_when_off_hours(request: Request, call_next):
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        p = request.url.path
        # protège toutes les routes commandes, mais pas le webhook Stripe
        if p.startswith("/api/orders") and not p.startswith("/api/stripe/webhook"):
            open_now, next_open = is_open_now_and_next()
            if not open_now:
                msg = "Commandes fermées pour le moment."
                if next_open:
                    msg += " Prochaine ouverture : " + next_open.strftime("%a %H:%M")
                return JSONResponse(status_code=403, content={"detail": msg})
    return await call_next(request)

# --- Routes API ---
app.include_router(api_router, prefix="/api")
app.include_router(store_router, prefix="/api")          # => /api/store/status
app.include_router(stripe_webhook_router, prefix="/api") # => /api/stripe/webhook

@app.get("/")
async def root():
    return {"message": "Restaurant API is running. Access docs at /docs"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
