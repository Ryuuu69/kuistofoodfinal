from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.session import async_engine
from database.base import Base
from api.routers import api_router
from api.routers.stripe_webhook import router as stripe_webhook_router


app = FastAPI(
    title="Restaurant API",
    description="API backend for a restaurant management system.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- CORS : autorise localhost + tous les sous-domaines *.gitpod.io ---
# NOTE: allow_credentials=True est important avec Gitpod/proxies pour que le preflight (OPTIONS)
# et les requêtes CORS passent correctement.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8000",
        "https://localhost:5173",
        "https://localhost:8000",
    ],
    allow_origin_regex=r"https://.*\.gitpod\.io$",
    allow_credentials=True,          # ✅ important
    allow_methods=["*"],
    allow_headers=["*"],             # inclut X-Admin-Token, Content-Type, etc.
    max_age=86400,
)

# Création des tables au démarrage (dev)
@app.on_event("startup")
async def create_db_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Routes API
app.include_router(api_router, prefix="/api")
app.include_router(stripe_webhook_router)  # /stripe/webhook

@app.get("/")
async def root():
    return {"message": "Restaurant API is running. Access docs at /docs"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
