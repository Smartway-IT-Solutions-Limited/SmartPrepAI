import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await register(fullName, email, password, phone || undefined);
      navigate("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Couldn't create your account. Please try again.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mx-auto max-w-sm px-6 py-20">
      <h1 className="font-display text-3xl text-paper">Create your account</h1>
      <p className="mt-2 text-sm text-slate">Your first 2 mock exams and AI tutor sessions are free.</p>

      <form onSubmit={handleSubmit} className="mt-8 space-y-4">
        <div>
          <label className="block text-sm text-slate">Full name</label>
          <input
            required value={fullName} onChange={(e) => setFullName(e.target.value)}
            className="mt-1 w-full rounded-md border border-white/10 bg-surface px-3 py-2 text-paper outline-none focus:border-gold"
          />
        </div>
        <div>
          <label className="block text-sm text-slate">Email</label>
          <input
            type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full rounded-md border border-white/10 bg-surface px-3 py-2 text-paper outline-none focus:border-gold"
          />
        </div>
        <div>
          <label className="block text-sm text-slate">Phone (optional)</label>
          <input
            value={phone} onChange={(e) => setPhone(e.target.value)}
            className="mt-1 w-full rounded-md border border-white/10 bg-surface px-3 py-2 text-paper outline-none focus:border-gold"
          />
        </div>
        <div>
          <label className="block text-sm text-slate">Password</label>
          <input
            type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full rounded-md border border-white/10 bg-surface px-3 py-2 text-paper outline-none focus:border-gold"
          />
          <p className="mt-1 text-xs text-slate">At least 8 characters.</p>
        </div>

        {error && <p className="text-sm text-danger">{error}</p>}

        <button
          disabled={busy}
          className="w-full rounded-md bg-gold py-2 font-medium text-ink hover:bg-gold/90 disabled:opacity-60"
        >
          {busy ? "Creating account…" : "Create account"}
        </button>
      </form>

      <p className="mt-6 text-sm text-slate">
        Already have an account?{" "}
        <Link to="/login" className="text-gold hover:underline">Sign in</Link>
      </p>
    </div>
  );
}
