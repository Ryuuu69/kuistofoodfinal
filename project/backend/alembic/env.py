import os
import sys
import asyncio
import ssl
from logging.config import fileConfig
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from dotenv import load_dotenv

# ------------------------------------------------------------------
# S'assurer que "backend/" est sur le PYTHONPATH
HERE = os.path.dirname(__file__)                       # .../backend/alembic
BACKEND_DIR = os.path.abspath(os.path.join(HERE, ".."))  # .../backend
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
# ------------------------------------------------------------------

# Charger .env (dans backend/.env)
env_path = os.path.join(BACKEND_DIR, ".env")
load_dotenv(dotenv_path=env_path)

# Alembic config
config = context.config

# Override l'URL via settings si dispo
from core.config import settings  # expose settings.DATABASE_URL
if getattr(settings, "DATABASE_URL", None):
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata cible
from database.base import Base  # importe aussi les modèles
target_metadata = Base.metadata


def _prepare_url_and_ssl(raw_url: str):
    """
    Si l'URL contient sslmode, construit un SSLContext.
    Si SKIP_SSL_VERIFY=1, désactive la vérif (DEV UNIQUEMENT).
    Retourne (url_sans_sslmode, ssl_context_ou_None).
    """
    parsed = urlparse(raw_url)
    qs = parse_qs(parsed.query)
    ssl_ctx = None

    if "sslmode" in qs:
        mode = qs.get("sslmode", [None])[0]
        if mode in ("require", "verify-full", "verify-ca"):
            if os.getenv("SKIP_SSL_VERIFY") == "1":
                ssl_ctx = ssl.create_default_context()
                ssl_ctx.check_hostname = False
                ssl_ctx.verify_mode = ssl.CERT_NONE
            else:
                ssl_ctx = ssl.create_default_context()
        qs.pop("sslmode", None)

    new_query = urlencode({k: v[0] for k, v in qs.items()})
    cleaned = parsed._replace(query=new_query)
    cleaned_url = urlunparse(cleaned)
    return cleaned_url, ssl_ctx


def run_migrations_offline():
    """Migrations en mode offline."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Migrations en mode online (connexion réelle)."""
    raw_url = config.get_main_option("sqlalchemy.url")
    if not raw_url:
        raise RuntimeError("Aucune URL de base de données pour Alembic.")

    cleaned_url, ssl_ctx = _prepare_url_and_ssl(raw_url)
    connect_args = {"ssl": ssl_ctx} if ssl_ctx else {}

    engine = create_async_engine(
        cleaned_url,
        poolclass=pool.NullPool,
        future=True,
        connect_args=connect_args,
    )

    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
