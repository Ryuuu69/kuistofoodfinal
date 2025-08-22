from fastapi import Header, HTTPException, status
from core.config import settings  # On importe les settings pour lire ADMIN_TOKEN depuis le .env

async def get_admin_token(x_admin_token: str = Header(...)):
    """
    Vérifie que le header 'X-Admin-Token' correspond bien au token défini
    dans le fichier .env (variable ADMIN_TOKEN).
    """
    if x_admin_token != settings.ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token admin invalide !"
        )
    return x_admin_token
