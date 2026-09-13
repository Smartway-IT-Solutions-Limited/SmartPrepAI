import { useState } from "react";
import api from "../api/client";
import MathMarkdown from "../components/MathMarkdown";
import CitationList from "../components/CitationList";

interface Citation { book: string; chapter?: string | null; page?: number | null; snippet: string; }
interface Turn { question: string; answer: string; citations: Citation[]; }

export default function Tutor() {
  const [question, setQuestion] = useState("");
  const [mode, setMode] = useState<"simplify" | "deep_dive">("simplify");
  const [history, setHistory] = useState<Turn[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const ask = async () => {
    if (!question.trim()) return;
    setBusy(true);
    setError(null);
    try {
      const { data } = await api.post("/api/tutor/ask", { question, mode });
      setHistory([{ question, answer: data.answer, citations: data.citations }, ...history]);
      setQuestion("");
    } catch (err: any) {
      setError(err.response?.data?.detail || "The AI tutor is unavailable right now.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-6 py-12">
      <h1 className="font-display text-3xl text-paper">AI Tutor</h1>
      <p className="mt-1 text-slate">
        Ask anything — every answer is grounded in your textbooks, with sources you can check.
      </p>

      <div className="mt-6 flex gap-2">
        <button
          onClick={() => setMode("simplify")}
          className={`rounded-full px-4 py-1.5 text-sm ${mode === "simplify" ? "bg-gold text-ink" : "border border-white/20 text-slate"}`}
        >
          Simplify
        </button>
        <button
          onClick={() => setMode("deep_dive")}
          className={`rounded-full px-4 py-1.5 text-sm ${mode === "deep_dive" ? "bg-gold text-ink" : "border border-white/20 text-slate"}`}
        >
          Deep dive
        </button>
      </div>

      <div className="mt-4 flex gap-2">
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); ask(); } }}
          placeholder="e.g. Explain how to find the limit of (sin x)/x as x approaches 0"
          rows={3}
          className="w-full rounded-md border border-white/10 bg-surface px-3 py-2 text-paper outline-none focus:border-gold"
        />
      </div>
      <button
        onClick={ask} disabled={busy}
        className="mt-3 rounded-md bg-gold px-5 py-2.5 font-medium text-ink hover:bg-gold/90 disabled:opacity-60"
      >
        {busy ? "Thinking…" : "Ask"}
      </button>

      {error && <p className="mt-4 text-sm text-danger">{error}</p>}

      <div className="mt-10 space-y-8">
        {history.map((turn, i) => (
          <div key={i} className="border-t border-white/10 pt-6">
            <p className="font-display text-lg text-paper">{turn.question}</p>
            <div className="mt-3">
              <MathMarkdown content={turn.answer} />
            </div>
            <CitationList citations={turn.citations} />
          </div>
        ))}
      </div>
    </div>
  );
}
