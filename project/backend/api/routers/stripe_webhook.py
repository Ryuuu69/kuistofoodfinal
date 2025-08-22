from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import stripe, json, base64

from core.config import settings
from api.deps import get_db
from crud.crud_operations import order_crud
from schemas.schemas import OrderCreate
from models.models import OrderStatus, PaymentMode

router = APIRouter(prefix="/stripe", tags=["Stripe Webhook"])
stripe.api_key = settings.STRIPE_SECRET_KEY

def _decode_order_from_metadata(md: dict) -> dict:
    # legacy
    if md.get("order_data"):
        return json.loads(md["order_data"])
    n = int(md.get("order_parts") or 0)
    if n <= 0:
        raise ValueError("order_parts manquant.")
    parts = []
    for i in range(n):
        k = f"order_data_b64_{i}"
        v = md.get(k)
        if not v:
            raise ValueError(f"segment {k} manquant.")
        parts.append(v)
    raw = base64.b64decode(("".join(parts)).encode("ascii")).decode("utf-8")
    return json.loads(raw)

@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    sig_header = request.headers.get("stripe-signature")
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    etype = event["type"]
    if etype not in ("payment_intent.succeeded", "payment_intent.processing"):
        return {"status": "ignored", "event": etype}

    succeeded = (etype == "payment_intent.succeeded")
    pi = event["data"]["object"]
    md = dict(pi.get("metadata") or {})

    # 1) Si la commande existe déjà en metadata → potentiellement MAJ statut
    if md.get("order_created") == "1" and md.get("order_id"):
        try:
            order_id = int(md["order_id"])
        except Exception:
            return {"status": "ok", "skipped": "invalid-order-id"}

        order = await order_crud.get(db, id=order_id)
        if not order:
            return {"status": "ok", "skipped": "order-not-found", "order_id": order_id}

        # Mettre en 'preparing' uniquement si payé (succeeded) et mode CB
        if succeeded and order.payment_mode == PaymentMode.cb and order.status != OrderStatus.preparing:
            order.status = OrderStatus.preparing
            await db.commit()
        return {"status": "ok", "order_id": order_id, "current_status": str(order.status)}

    # 2) Sinon, tenter de créer la commande depuis la metadata
    try:
        data = _decode_order_from_metadata(md)
        db_order = await order_crud.create(db, obj_in=OrderCreate(**data))

        # Si paiement confirmé, passer directement en 'preparing'
        if succeeded and db_order.payment_mode == PaymentMode.cb and db_order.status != OrderStatus.preparing:
            db_order.status = OrderStatus.preparing
            await db.commit()

        # Écrire l'order_id dans la metadata pour idempotence
        try:
            stripe.PaymentIntent.modify(
                pi["id"],
                metadata={**md, "order_created": "1", "order_id": str(db_order.id)},
            )
        except stripe.error.StripeError:
            pass

    except Exception as e:
        # On accepte l’évènement pour éviter les retries infinis ;
        # ta page de confirmation peut toujours appeler /orders/capture en fallback.
        print("[WEBHOOK] create/update failed:", e)

    return {"status": "success"}
