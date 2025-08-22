from pydantic_settings import BaseSettings, SettingsConfigDict
from decimal import Decimal
from typing import Optional  # <-- ajout

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    ADMIN_TOKEN: str

    RESTAURANT_LAT: float = 43.606206
    RESTAURANT_LNG: float = 3.870316
    DELIVERY_BASE_FEE: Decimal = Decimal("2.00")
    DELIVERY_PER_KM_FEE: Decimal = Decimal("1.00")
    DELIVERY_MAX_KM: float = 8.0

    STRIPE_SECRET_KEY: str
    # --- AJOUTS POUR LE WEBHOOK ---
    STRIPE_WEBHOOK_SECRET: str = ""              # whsec_... (obligatoire)
    STRIPE_WEBHOOK_SECRET_2: Optional[str] = None  # si tu as une 2e destination (optionnel)
    # --------------------------------

    FRONT_CONFIRM_URL: str
    FRONT_CANCEL_URL: str

settings = Settings()
