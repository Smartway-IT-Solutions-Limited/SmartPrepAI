import { useEffect, useState } from "react";
import { TESTIMONIALS } from "../data/testimonials";

export default function Testimonials() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setIndex((i) => (i + 1) % TESTIMONIALS.length);
    }, 5500);
    return () => clearInterval(id);
  }, []);

  const t = TESTIMONIALS[index];

  return (
    <section className="border-y border-white/10 bg-surface/50">
      <div className="mx-auto max-w-3xl px-6 py-16 text-center">
        <p className="text-xs uppercase tracking-wide text-gold">What students are saying</p>

        <div className="mt-6 min-h-[160px]">
          <p className="font-display text-2xl leading-snug text-paper transition-opacity duration-500">
            "{t.quote}"
          </p>
          <p className="mt-5 text-sm text-slate">
            <span className="text-paper">{t.name}</span> · {t.role}
            {t.score && <span className="text-gold"> · {t.score}</span>}
          </p>
        </div>

        <div className="mt-6 flex justify-center gap-2">
          {TESTIMONIALS.map((_, i) => (
            <button
              key={i}
              aria-label={`Show testimonial ${i + 1}`}
              onClick={() => setIndex(i)}
              className={`h-1.5 rounded-full transition-all ${
                i === index ? "w-6 bg-gold" : "w-1.5 bg-white/20"
              }`}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
