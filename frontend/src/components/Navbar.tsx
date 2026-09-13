import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="border-b border-white/10">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-2">
          <img src="/logo-icon.png" alt="SmartPrepAI logo" className="h-9 w-auto" />
          <span className="font-display text-xl tracking-tight text-paper">
            SmartPrep<span className="text-gold">AI</span>
          </span>
        </Link>

        {user ? (
          <nav className="flex items-center gap-6 text-sm text-slate">
            <Link to="/dashboard" className="hover:text-paper">Dashboard</Link>
            <Link to="/mock-test" className="hover:text-paper">Mock Test</Link>
            <Link to="/tutor" className="hover:text-paper">AI Tutor</Link>
            <Link to="/pricing" className="hover:text-paper">Pricing</Link>
            <span className="rounded-full border border-gold/40 px-3 py-1 text-xs text-gold">
              {user.free_uses_remaining} free {user.free_uses_remaining === 1 ? "use" : "uses"} left
            </span>
            <button
              onClick={() => { logout(); navigate("/login"); }}
              className="text-slate hover:text-paper"
            >
              Sign out
            </button>
          </nav>
        ) : (
          <nav className="flex items-center gap-4 text-sm">
            <Link to="/login" className="text-slate hover:text-paper">Sign in</Link>
            <Link
              to="/register"
              className="rounded-md bg-gold px-4 py-2 font-medium text-ink hover:bg-gold/90"
            >
              Get started
            </Link>
          </nav>
        )}
      </div>
    </header>
  );
}
