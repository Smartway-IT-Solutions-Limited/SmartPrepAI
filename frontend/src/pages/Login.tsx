import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Couldn't sign you in. Check your details and try again.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mx-auto max-w-sm px-6 py-20">
      <h1 className="font-display text-3xl text-paper">Welcome back</h1>
      <p className="mt-2 text-sm text-slate">Sign in to continue your revision plan.</p>

      <form onSubmit={handleSubmit} className="mt-8 space-y-4">
        <div>
          <label className="block text-sm text-slate">Email</label>
          <input
            type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full rounded-md border border-white/10 bg-surface px-3 py-2 text-paper outline-none focus:border-gold"
          />
        </div>
        <div>
          <label className="block text-sm text-slate">Password</label>
          <input
            type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full rounded-md border border-white/10 bg-surface px-3 py-2 text-paper outline-none focus:border-gold"
          />
        </div>

        {error && <p className="text-sm text-danger">{error}</p>}

        <button
          disabled={busy}
          className="w-full rounded-md bg-gold py-2 font-medium text-ink hover:bg-gold/90 disabled:opacity-60"
        >
          {busy ? "Signing in…" : "Sign in"}
        </button>
      </form>

      <p className="mt-6 text-sm text-slate">
        New here?{" "}
        <Link to="/register" className="text-gold hover:underline">Create an account — first 2 mock exams are free</Link>
      </p>
    </div>
  );
}
