import { useState } from "react";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

type Audience = "secondary" | "tertiary";
type Cycle = "monthly" | "semester";

interface Plan {
  id: string;
  name: string;
  tagline: string;
  desc: string;
  prices: Record<Cycle, number>;
}

// Mirrors backend/app/services/paystack_service.py::PRICING_NGN exactly —
// the backend is the source of truth for what's actually charged; this is
// display-only. If you change prices, update both places.
const PLANS: Record<Audience, Plan[]> = {
  secondary: [
    {
      id: "secondary_standard", name: "Jambite", tagline: "Standard",
      desc: "Full WAEC/JAMB/NECO/GCE past-question bank with AI explanations.",
      prices: { monthly: 2000, semester: 7000 },
    },
    {
      id: "secondary_pro", name: "Distinction", tagline: "Most popular",
      desc: "Adaptive revision planner and priority Socratic AI tutoring.",
      prices: { monthly: 5000, semester: 17000 },
    },
    {
      id: "secondary_guardian", name: "Guardian", tagline: "For parents",
      desc: "Covers up to 3 student profiles plus weekly WhatsApp progress reports.",
      prices: { monthly: 6000, semester: 20000 },
    },
  ],
  tertiary: [
    {
      id: "tertiary_standard", name: "Core", tagline: "Standard",
      desc: "Course-level past questions and AI explanations across Maths, Medicine, Accounting, Engineering, Law and more.",
      prices: { monthly: 2500, semester: 9000 },
    },
    {
      id: "tertiary_pro", name: "Pro", tagline: "Most popular",
      desc: "Priority AI tutoring, deep-dive derivations, and unlimited cited answers per course.",
      prices: { monthly: 6000, semester: 20000 },
    },
    {
      id: "tertiary_group", name: "Study Group", tagline: "For coursemates",
      desc: "Shared plan for study groups or department reading clubs — up to 5 members.",
      prices: { monthly: 15000, semester: 50000 },
    },
  ],
};

const formatNaira = (n: number) => `₦${n.toLocaleString("en-NG")}`;

export default function Pricing() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [audience, setAudience] = useState<Audience>("secondary");
  const [cycle, setCycle] = useState<Cycle>("monthly");
  const [busyPlan, setBusyPlan] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const subscribe = async (planId: string) => {
    if (!user) { navigate("/register"); return; }
    setBusyPlan(planId);
    setError(null);
    try {
      // Backend independently prices the plan+cycle and initializes the
      // Paystack transaction server-side — the frontend only ever redirects
      // to the authorization_url Paystack returns, never handling the amount.
      const { data } = await api.post("/api/subscriptions/init-payment", {
        plan: planId,
        billing_cycle: cycle,
      });
      window.location.href = data.authorization_url;
    } catch (err: any) {
      setError(err.response?.data?.detail || "Couldn't start checkout. Please try again.");
      setBusyPlan(null);
    }
  };

  return (
    <div className="mx-auto max-w-5xl px-6 py-16">
      <h1 className="font-display text-3xl text-paper">Plans for every stage</h1>
      <p className="mt-2 text-slate">
        Every new account starts with 2 free mock exams or tutor sessions — no card required.
      </p>

      {/* Audience tabs */}
      <div className="mt-8 inline-flex rounded-full border border-white/10 p-1">
        {(["secondary", "tertiary"] as Audience[]).map((a) => (
          <button
            key={a}
            onClick={() => setAudience(a)}
            className={`rounded-full px-5 py-2 text-sm font-medium transition-colors ${
              audience === a ? "bg-gold text-ink" : "text-slate hover:text-paper"
            }`}
          >
            {a === "secondary" ? "Secondary School" : "Tertiary (University & Polytechnic)"}
          </button>
        ))}
      </div>

      {/* Billing cycle toggle */}
      <div className="mt-4 flex items-center gap-3">
        <span className={`text-sm ${cycle === "monthly" ? "text-paper" : "text-slate"}`}>Monthly</span>
        <button
          role="switch"
          aria-checked={cycle === "semester"}
          onClick={() => setCycle(cycle === "monthly" ? "semester" : "monthly")}
          className="relative h-6 w-11 rounded-full bg-surfaceAlt transition-colors"
        >
          <span
            className={`absolute top-0.5 h-5 w-5 rounded-full bg-gold transition-transform ${
              cycle === "semester" ? "translate-x-5" : "translate-x-0.5"
            }`}
          />
        </button>
        <span className={`text-sm ${cycle === "semester" ? "text-paper" : "text-slate"}`}>
          Per semester <span className="text-gold">(best value)</span>
        </span>
      </div>

      {error && <p className="mt-4 text-sm text-danger">{error}</p>}

      <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-3">
        {PLANS[audience].map((plan) => (
          <div key={plan.id} className="flex flex-col border border-white/10 p-6">
            <p className="text-xs uppercase tracking-wide text-gold">{plan.tagline}</p>
            <h2 className="mt-1 font-display text-xl text-paper">{plan.name}</h2>
            <p className="mt-2 font-display text-2xl text-gold">
              {formatNaira(plan.prices[cycle])}
              <span className="text-sm font-normal text-slate"> / {cycle === "monthly" ? "month" : "semester"}</span>
            </p>
            <p className="mt-3 flex-1 text-sm text-slate">{plan.desc}</p>
            <button
              onClick={() => subscribe(plan.id)}
              disabled={busyPlan === plan.id}
              className="mt-6 rounded-md bg-gold py-2.5 font-medium text-ink hover:bg-gold/90 disabled:opacity-60"
            >
              {busyPlan === plan.id ? "Redirecting to Paystack…" : "Subscribe"}
            </button>
          </div>
        ))}
      </div>

      <p className="mt-8 text-xs text-slate">
        All payments are processed securely by Paystack. Plans renew automatically at the
        selected cycle — cancel anytime from your dashboard before renewal.
      </p>
    </div>
  );
}
