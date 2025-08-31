from pydantic_settings import BaseSettings, SettingsConfigDict
from decimal import Decimal
from typing import Optional  # <-- ajout

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    ADMIN_TOKEN: str

    RESTAURANT_LAT: float = 43.6053907723102
    RESTAURANT_LNG: float = 3.876522854376451
    DELIVERY_BASE_FEE: Decimal = Decimal("1.00")
    DELIVERY_PER_KM_FEE: Decimal = Decimal("1.30")
    DELIVERY_MAX_KM: float = 8.0
     # --- AJOUTER CES 3 CHAMPS ---
    BUSINESS_TIMEZONE: str = "Europe/Paris"
    ORDER_WINDOWS: str = (
        "Mon:20:00-06:00,"
        "Tue:20:00-06:00,"
        "Wed:20:00-06:00,"
        "Thu:20:00-06:00,"
        "Fri:20:00-06:00,"
        "Sat:20:00-06:00,"
        "Sun:20:00-06:00"
    )
    FORCE_CLOSED: bool = False

    STRIPE_SECRET_KEY: str
    # --- AJOUTS POUR LE WEBHOOK ---
    STRIPE_WEBHOOK_SECRET: str = "whsec_cSPgQdFPtsH03IBYZEgdl95NS3LMLkld"              # whsec_... (obligatoire)
    STRIPE_WEBHOOK_SECRET_2: Optional[str] = None  # si tu as une 2e destination (optionnel)
    # --------------------------------

    FRONT_CONFIRM_URL: str
    FRONT_CANCEL_URL: str

settings = Settings()
