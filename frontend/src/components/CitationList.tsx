interface Citation {
  book: string;
  chapter?: string | null;
  page?: number | null;
  snippet: string;
}

/**
 * "Active Citations": each source is a clickable <details> the student can
 * expand to verify the AI's answer against the original textbook excerpt.
 */
export default function CitationList({ citations }: { citations: Citation[] }) {
  if (!citations.length) return null;

  return (
    <div className="mt-4 border-t border-white/10 pt-4">
      <p className="mb-2 text-xs uppercase tracking-wide text-slate">Sources</p>
      <div className="space-y-2">
        {citations.map((c, i) => (
          <details key={i} className="rounded border border-white/10 bg-surface px-3 py-2">
            <summary className="cursor-pointer text-sm text-paper">
              {c.book}{c.page ? `, p. ${c.page}` : ""}{c.chapter ? ` — ${c.chapter}` : ""}
            </summary>
            <p className="mt-2 text-sm leading-relaxed text-slate">{c.snippet}</p>
          </details>
        ))}
      </div>
    </div>
  );
}
