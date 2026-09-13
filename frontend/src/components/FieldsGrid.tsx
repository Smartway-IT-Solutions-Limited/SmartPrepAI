import {
  Stethoscope, Calculator, Cog, Code2, Scale, Landmark, FlaskConical, Building2,
} from "lucide-react";

const FIELDS = [
  { icon: Stethoscope, label: "Medicine & Health Sciences" },
  { icon: Cog, label: "Engineering" },
  { icon: Calculator, label: "Mathematics & Statistics" },
  { icon: Landmark, label: "Accounting & Finance" },
  { icon: Code2, label: "Computer Science" },
  { icon: Scale, label: "Law" },
  { icon: FlaskConical, label: "Pure & Applied Sciences" },
  { icon: Building2, label: "Business Administration" },
];

export default function FieldsGrid() {
  return (
    <section className="mx-auto max-w-5xl px-6 py-20">
      <p className="text-xs uppercase tracking-wide text-gold">Built for every stage</p>
      <h2 className="mt-3 max-w-2xl font-display text-3xl text-paper">
        From your first WAEC mock to your final year project defence.
      </h2>
      <p className="mt-3 max-w-2xl text-slate">
        SmartPrepAI isn't just for secondary school. University and polytechnic
        students across every discipline use it to revise past questions,
        get Socratic AI explanations grounded in their own course textbooks,
        and track progress course by course.
      </p>

      <div className="mt-10 grid grid-cols-2 gap-4 sm:grid-cols-4">
        {FIELDS.map(({ icon: Icon, label }) => (
          <div
            key={label}
            className="flex flex-col items-start gap-3 border border-white/10 p-5 transition-colors hover:border-gold/50"
          >
            <Icon className="h-6 w-6 text-gold" strokeWidth={1.75} />
            <span className="text-sm text-paper">{label}</span>
          </div>
        ))}
      </div>
      <p className="mt-4 text-xs text-slate">…and more added as courses are ingested into the tutor's knowledge base.</p>
    </section>
  );
}
