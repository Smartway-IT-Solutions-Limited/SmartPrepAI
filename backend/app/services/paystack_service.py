"""
Paystack integration.

SECURITY MODEL (important — do not weaken this):
  1. The frontend NEVER decides a payment succeeded. It only opens the
     Paystack checkout and then tells the backend "reference X finished".
  2. The backend independently calls Paystack's `verify` endpoint before
     activating any subscription — the client's word is never trusted.
  3. Paystack also POSTs a webhook on `charge.success`. We verify its
     HMAC-SHA512 signature against PAYSTACK_SECRET_KEY before acting on it.
     This is the authoritative path (works even if the user closes the tab
     mid-checkout); the `verify` call on redirect is a fast-path UX bonus.
  4. Every write is idempotent on `paystack_reference` (unique constraint +
     status check) so Paystack's automatic webhook retries can't double
     credit a subscription.
"""
import hashlib
import hmac

import httpx

from app.config import settings
from app.models import BillingCycle, SubscriptionPlan

PAYSTACK_BASE = "https://api.paystack.co"

# Keep pricing authoritative on the SERVER, never trust an amount/plan sent by
# the client. Semester pricing is discounted vs. 4x the monthly rate (roughly
# a "pay for 3.5, get 4" incentive to commit for the term/semester).
PRICING_NGN: dict[SubscriptionPlan, dict[BillingCycle, int]] = {
    SubscriptionPlan.secondary_standard: {BillingCycle.monthly: 2_000, BillingCycle.semester: 7_000},
    SubscriptionPlan.secondary_pro: {BillingCycle.monthly: 5_000, BillingCycle.semester: 17_000},
    SubscriptionPlan.secondary_guardian: {BillingCycle.monthly: 6_000, BillingCycle.semester: 20_000},
    SubscriptionPlan.tertiary_standard: {BillingCycle.monthly: 2_500, BillingCycle.semester: 9_000},
    SubscriptionPlan.tertiary_pro: {BillingCycle.monthly: 6_000, BillingCycle.semester: 20_000},
    SubscriptionPlan.tertiary_group: {BillingCycle.monthly: 15_000, BillingCycle.semester: 50_000},
}

PLAN_PRICES_KOBO: dict[SubscriptionPlan, dict[BillingCycle, int]] = {
    plan: {cycle: naira * 100 for cycle, naira in cycles.items()}
    for plan, cycles in PRICING_NGN.items()
}

# Duration depends only on the billing cycle chosen, not the plan itself.
DURATION_DAYS_BY_CYCLE: dict[BillingCycle, int] = {
    BillingCycle.monthly: 30,
    BillingCycle.semester: 120,  # ~4 months, covers a typical academic semester/term
}


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }


async def initialize_transaction(
    email: str, plan: SubscriptionPlan, billing_cycle: BillingCycle, reference: str
) -> dict:
    amount = PLAN_PRICES_KOBO[plan][billing_cycle]
    payload = {
        "email": email,
        "amount": amount,
        "reference": reference,
        "currency": "NGN",
        "callback_url": f"{settings.FRONTEND_URL}/payment/callback",
        "metadata": {"plan": plan.value, "billing_cycle": billing_cycle.value},
    }
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(f"{PAYSTACK_BASE}/transaction/initialize", json=payload, headers=_headers())
        resp.raise_for_status()
        return resp.json()["data"]


async def verify_transaction(reference: str) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(f"{PAYSTACK_BASE}/transaction/verify/{reference}", headers=_headers())
        resp.raise_for_status()
        return resp.json()["data"]


def verify_webhook_signature(raw_body: bytes, signature_header: str | None) -> bool:
    if not signature_header:
        return False
    computed = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode("utf-8"), raw_body, hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(computed, signature_header)
