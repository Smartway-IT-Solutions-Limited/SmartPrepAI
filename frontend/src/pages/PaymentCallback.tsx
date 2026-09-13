import { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import api from "../api/client";

export default function PaymentCallback() {
  const [params] = useSearchParams();
  const reference = params.get("reference") || params.get("trxref");
  const [status, setStatus] = useState<"checking" | "success" | "failed">("checking");

  useEffect(() => {
    if (!reference) { setStatus("failed"); return; }
    // The frontend never decides success on its own — it asks the backend,
    // which independently re-verifies the transaction with Paystack before
    // activating anything.
    api.get(`/api/subscriptions/verify/${reference}`)
      .then(() => setStatus("success"))
      .catch(() => setStatus("failed"));
  }, [reference]);

  return (
    <div className="mx-auto max-w-md px-6 py-24 text-center">
      {status === "checking" && <p className="text-slate">Confirming your payment…</p>}
      {status === "success" && (
        <>
          <p className="font-display text-2xl text-gold">Payment confirmed</p>
          <p className="mt-2 text-slate">Your plan is now active.</p>
          <Link to="/dashboard" className="mt-6 inline-block rounded-md bg-gold px-5 py-2.5 font-medium text-ink">
            Go to dashboard
          </Link>
        </>
      )}
      {status === "failed" && (
        <>
          <p className="font-display text-2xl text-danger">We couldn't confirm this payment</p>
          <p className="mt-2 text-slate">If you were charged, contact support with your reference and it'll be resolved.</p>
          <Link to="/pricing" className="mt-6 inline-block rounded-md border border-white/20 px-5 py-2.5 font-medium text-paper">
            Back to pricing
          </Link>
        </>
      )}
    </div>
  );
}
