import { useState } from "react";
import api from "../api/client";

interface Question {
  id: string;
  question_text: string;
  options: Record<string, string>;
}

interface Result {
  score: number;
  total_questions: number;
  percentage: number;
  breakdown: { question_id: string; correct_option: string; selected_option: string; is_correct: boolean; explanation: string }[];
}

const EXAM_TYPES = ["WAEC", "JAMB", "NECO", "GCE"];

export default function MockTest() {
  const [examType, setExamType] = useState("JAMB");
  const [subject, setSubject] = useState("Mathematics");
  const [mockTestId, setMockTestId] = useState<string | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const startTest = async () => {
    setError(null);
    setBusy(true);
    setResult(null);
    try {
      const { data } = await api.post("/api/mock-tests/start", {
        exam_type: examType, subject, num_questions: 10,
      });
      setMockTestId(data.id);
      setQuestions(data.questions);
      setAnswers({});
    } catch (err: any) {
      setError(err.response?.data?.detail || "Couldn't start the test.");
    } finally {
      setBusy(false);
    }
  };

  const submitTest = async () => {
    if (!mockTestId) return;
    setBusy(true);
    setError(null);
    try {
      const payload = {
        answers: Object.entries(answers).map(([question_id, selected_option]) => ({ question_id, selected_option })),
      };
      const { data } = await api.post(`/api/mock-tests/${mockTestId}/submit`, payload);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Couldn't submit your answers.");
    } finally {
      setBusy(false);
    }
  };

  if (result) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-16 text-center">
        <p className="text-xs uppercase tracking-wide text-slate">Your result</p>
        <p className="mt-2 font-display text-6xl text-gold">{result.percentage}%</p>
        <p className="mt-2 text-slate">{result.score} out of {result.total_questions} correct</p>
        <button
          onClick={() => { setMockTestId(null); setQuestions([]); setResult(null); }}
          className="mt-8 rounded-md bg-gold px-5 py-2.5 font-medium text-ink hover:bg-gold/90"
        >
          Take another test
        </button>
      </div>
    );
  }

  if (mockTestId && questions.length) {
    const allAnswered = questions.every((q) => answers[q.id]);
    return (
      <div className="mx-auto max-w-3xl px-6 py-12">
        <h1 className="font-display text-2xl text-paper">{subject} — {examType} mock test</h1>
        <div className="mt-8 space-y-8">
          {questions.map((q, idx) => (
            <div key={q.id} className="border-b border-white/10 pb-6">
              <p className="text-sm text-slate">Question {idx + 1} of {questions.length}</p>
              <p className="mt-2 text-paper">{q.question_text}</p>
              <div className="mt-4 space-y-2">
                {Object.entries(q.options).map(([key, text]) => (
                  <label
                    key={key}
                    className={`flex cursor-pointer items-center gap-3 rounded-md border px-3 py-2 ${
                      answers[q.id] === key ? "border-gold bg-surfaceAlt" : "border-white/10"
                    }`}
                  >
                    <input
                      type="radio" name={q.id} value={key}
                      checked={answers[q.id] === key}
                      onChange={() => setAnswers({ ...answers, [q.id]: key })}
                      className="accent-gold"
                    />
                    <span className="text-sm text-paper"><strong>{key}.</strong> {text}</span>
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>

        {error && <p className="mt-4 text-sm text-danger">{error}</p>}

        <button
          onClick={submitTest}
          disabled={!allAnswered || busy}
          className="mt-6 w-full rounded-md bg-gold py-3 font-medium text-ink hover:bg-gold/90 disabled:opacity-50"
        >
          {busy ? "Submitting…" : "Submit answers"}
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-md px-6 py-20">
      <h1 className="font-display text-3xl text-paper">Start a mock test</h1>
      <p className="mt-2 text-sm text-slate">Timed CBT-style practice with instant scoring.</p>

      <div className="mt-8 space-y-4">
        <div>
          <label className="block text-sm text-slate">Exam</label>
          <select
            value={examType} onChange={(e) => setExamType(e.target.value)}
            className="mt-1 w-full rounded-md border border-white/10 bg-surface px-3 py-2 text-paper"
          >
            {EXAM_TYPES.map((e) => <option key={e} value={e}>{e}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm text-slate">Subject</label>
          <input
            value={subject} onChange={(e) => setSubject(e.target.value)}
            className="mt-1 w-full rounded-md border border-white/10 bg-surface px-3 py-2 text-paper"
          />
        </div>
      </div>

      {error && <p className="mt-4 text-sm text-danger">{error}</p>}

      <button
        onClick={startTest} disabled={busy}
        className="mt-8 w-full rounded-md bg-gold py-3 font-medium text-ink hover:bg-gold/90 disabled:opacity-60"
      >
        {busy ? "Loading…" : "Start test"}
      </button>
    </div>
  );
}
