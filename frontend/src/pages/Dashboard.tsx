import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";

interface Summary {
  tests_completed: number;
  average_score_pct: number;
  free_uses_remaining: number;
  recent_tests: { mock_test_id: string; score: number; total_questions: number; percentage: number }[];
}

export default function Dashboard() {
  const [summary, setSummary] = useState<Summary | null>(null);

  useEffect(() => {
    api.get("/api/users/dashboard/summary").then((res) => setSummary(res.data));
  }, []);

  return (
    <div className="mx-auto max-w-5xl px-6 py-12">
      <h1 className="font-display text-3xl text-paper">Your workspace</h1>
      <p className="mt-1 text-slate">Mock test history, weak points, and daily progress.</p>

      <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="border border-white/10 p-5">
          <p className="text-xs uppercase tracking-wide text-slate">Tests completed</p>
          <p className="mt-2 font-display text-3xl text-paper">{summary?.tests_completed ?? "—"}</p>
        </div>
        <div className="border border-white/10 p-5">
          <p className="text-xs uppercase tracking-wide text-slate">Average score</p>
          <p className="mt-2 font-display text-3xl text-gold">{summary?.average_score_pct ?? "—"}%</p>
        </div>
        <div className="border border-white/10 p-5">
          <p className="text-xs uppercase tracking-wide text-slate">Free uses left</p>
          <p className="mt-2 font-display text-3xl text-paper">{summary?.free_uses_remaining ?? "—"}</p>
        </div>
      </div>

      <div className="mt-10 flex gap-4">
        <Link to="/mock-test" className="rounded-md bg-gold px-5 py-2.5 font-medium text-ink hover:bg-gold/90">
          Start a mock test
        </Link>
        <Link to="/tutor" className="rounded-md border border-white/20 px-5 py-2.5 font-medium text-paper hover:border-gold">
          Ask the AI tutor
        </Link>
      </div>

      <div className="mt-10">
        <h2 className="font-display text-xl text-paper">Recent tests</h2>
        <div className="mt-4 divide-y divide-white/10 border-y border-white/10">
          {summary?.recent_tests.length ? (
            summary.recent_tests.map((t) => (
              <div key={t.mock_test_id} className="flex items-center justify-between py-3">
                <span className="text-sm text-slate">{t.score} / {t.total_questions} correct</span>
                <span className="font-display text-lg text-gold">{t.percentage}%</span>
              </div>
            ))
          ) : (
            <p className="py-6 text-sm text-slate">No tests yet — your first mock exam is free.</p>
          )}
        </div>
      </div>
    </div>
  );
}
