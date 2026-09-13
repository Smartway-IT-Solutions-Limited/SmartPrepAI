import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.deps import get_current_user
from app.models import Payment, PaymentStatus, Subscription, SubscriptionStatus, User
from app.schemas import InitPaymentRequest, InitPaymentResponse, SubscriptionOut
from app.services.paystack_service import (
    DURATION_DAYS_BY_CYCLE,
    PLAN_PRICES_KOBO,
    initialize_transaction,
    verify_transaction,
    verify_webhook_signature,
)

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])


@router.post("/init-payment", response_model=InitPaymentResponse)
async def init_payment(
    payload: InitPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.plan not in PLAN_PRICES_KOBO:
        raise HTTPException(status_code=400, detail="This plan cannot be purchased directly")

    reference = f"spa_{uuid.uuid4().hex[:20]}"

    sub = Subscription(
        user_id=current_user.id,
        plan=payload.plan,
        billing_cycle=payload.billing_cycle,
        status=SubscriptionStatus.pending,
    )
    db.add(sub)
    await db.flush()

    payment = Payment(
        user_id=current_user.id,
        subscription_id=sub.id,
        paystack_reference=reference,
        plan=payload.plan,
        billing_cycle=payload.billing_cycle,
        amount_kobo=PLAN_PRICES_KOBO[payload.plan][payload.billing_cycle],
        status=PaymentStatus.pending,
    )
    db.add(payment)
    await db.commit()

    data = await initialize_transaction(current_user.email, payload.plan, payload.billing_cycle, reference)

    return InitPaymentResponse(
        authorization_url=data["authorization_url"],
        access_code=data["access_code"],
        reference=reference,
        public_key=settings.PAYSTACK_PUBLIC_KEY,
    )


async def _activate_subscription(db: AsyncSession, payment: Payment):
    """Shared by both the redirect-verify path and the webhook path.
    Idempotent: does nothing if the payment was already marked success."""
    if payment.status == PaymentStatus.success:
        return  # already processed — webhook retries land here safely

    payment.status = PaymentStatus.success

    result = await db.execute(select(Subscription).where(Subscription.id == payment.subscription_id))
    sub = result.scalar_one_or_none()
    if sub:
        now = datetime.now(timezone.utc)
        sub.status = SubscriptionStatus.active
        sub.started_at = now
        sub.expires_at = now + timedelta(days=DURATION_DAYS_BY_CYCLE[payment.billing_cycle])

    await db.commit()


@router.get("/verify/{reference}", response_model=SubscriptionOut)
async def verify_payment(reference: str, db: AsyncSession = Depends(get_db)):
    """Fast-path UX check hit on the frontend's /payment/callback page right
    after Paystack redirects back. The webhook below is the source of truth
    that also fires independently, so this endpoint is safe even if the user
    closes the tab before it resolves."""
    result = await db.execute(select(Payment).where(Payment.paystack_reference == reference))
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    verified = await verify_transaction(reference)
    if verified.get("status") != "success":
        raise HTTPException(status_code=402, detail="Payment not successful")

    await _activate_subscription(db, payment)

    result = await db.execute(select(Subscription).where(Subscription.id == payment.subscription_id))
    return result.scalar_one()


@router.post("/paystack/webhook", include_in_schema=False)
async def paystack_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    raw_body = await request.body()
    signature = request.headers.get("x-paystack-signature")

    if not verify_webhook_signature(raw_body, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    event = await request.json()
    if event.get("event") == "charge.success":
        reference = event["data"]["reference"]
        result = await db.execute(select(Payment).where(Payment.paystack_reference == reference))
        payment = result.scalar_one_or_none()
        if payment:
            payment.raw_webhook_payload = event
            await _activate_subscription(db, payment)

    return {"received": True}


@router.get("/me", response_model=list[SubscriptionOut])
async def my_subscriptions(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Subscription).where(Subscription.user_id == current_user.id))
    return result.scalars().all()
