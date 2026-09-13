import { Link } from "react-router-dom";
import { CheckCircle2, GraduationCap, BookOpenCheck, Sparkles } from "lucide-react";
import Testimonials from "../components/Testimonials";
import FieldsGrid from "../components/FieldsGrid";

const FEATURES = [
  {
    icon: BookOpenCheck,
    title: "Real CBT-style mock exams",
    desc: "Timed practice from actual WAEC, JAMB, NECO and GCE past questions — plus course-level tests for university modules.",
  },
  {
    icon: Sparkles,
    title: "An AI tutor that shows its work",
    desc: "Every explanation is grounded in your own textbooks, with clickable citations so you can verify the answer instead of just trusting it.",
  },
  {
    icon: GraduationCap,
    title: "One platform, every stage",
    desc: "From your first JAMB mock to a 400-level engineering course — the same adaptive tutor follows you all the way through.",
  },
];

export default function Landing() {
  return (
    <div>
      {/* Hero */}
      <section className="mx-auto max-w-3xl px-6 py-24">
        <p className="text-sm uppercase tracking-wide text-gold">
          WAEC · JAMB · NECO · GCE — and Medicine, Engineering, Accounting, Law & more
        </p>
        <h1 className="mt-4 font-display text-5xl leading-tight text-paper">
          The exam prep app that grows up with you.
        </h1>
        <p className="mt-6 max-w-xl text-lg text-slate">
          Start with free mock exams for your WAEC or JAMB. Stay for an AI tutor
          that keeps explaining your coursework long after secondary school —
          whether that's calculus, physiology, structural engineering, or
          financial accounting.
        </p>
        <div className="mt-8 flex flex-wrap gap-4">
          <Link to="/register" className="rounded-md bg-gold px-6 py-3 font-medium text-ink hover:bg-gold/90">
            Start free — 2 mock exams on us
          </Link>
          <Link to="/pricing" className="rounded-md border border-white/20 px-6 py-3 font-medium text-paper hover:border-gold">
            See plans for your stage
          </Link>
        </div>

        <div className="mt-10 flex flex-wrap gap-x-8 gap-y-2 text-sm text-slate">
          {["No card required to start", "Cited AI answers", "Secondary + university"].map((t) => (
            <span key={t} className="flex items-center gap-2">
              <CheckCircle2 size={16} className="text-gold" /> {t}
            </span>
          ))}
        </div>
      </section>

      {/* Feature grid */}
      <section className="mx-auto max-w-5xl px-6 py-16">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
          {FEATURES.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="border border-white/10 p-6">
              <Icon className="h-6 w-6 text-gold" strokeWidth={1.75} />
              <h3 className="mt-4 font-display text-lg text-paper">{title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      <FieldsGrid />
      <Testimonials />

      {/* Closing CTA */}
      <section className="mx-auto max-w-3xl px-6 py-20 text-center">
        <h2 className="font-display text-3xl text-paper">Ready to stop guessing what to revise?</h2>
        <p className="mt-3 text-slate">Create an account — your first 2 mock exams and AI tutor sessions are free.</p>
        <Link
          to="/register"
          className="mt-6 inline-block rounded-md bg-gold px-6 py-3 font-medium text-ink hover:bg-gold/90"
        >
          Get started free
        </Link>
      </section>
    </div>
  );
}
