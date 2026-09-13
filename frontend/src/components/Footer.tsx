import { Mail, MessageCircle, Instagram, Facebook, Twitter } from "lucide-react";

const SUPPORT_EMAIL = "smartprep@smartwayitsolutions.com";
const WHATSAPP_NUMBER = "08121515138";
// wa.me needs the number in international format without leading 0 — Nigeria = +234
const WHATSAPP_LINK = `https://wa.me/234${WHATSAPP_NUMBER.replace(/^0/, "")}`;

const SOCIALS = [
  { icon: Instagram, href: "https://instagram.com/smartprepai", label: "Instagram @smartprepai" },
  { icon: Facebook, href: "https://facebook.com/smartprepai", label: "Facebook @smartprepai" },
  { icon: Twitter, href: "https://twitter.com/smartprepai", label: "Twitter/X @smartprepai" },
];

export default function Footer() {
  return (
    <footer className="border-t border-white/10 bg-surface">
      <div className="mx-auto max-w-6xl px-6 py-10">
        <div className="flex flex-col items-start justify-between gap-8 sm:flex-row">
          <div>
            <div className="flex items-center gap-2">
              <img src="/logo-icon.png" alt="SmartPrepAI logo" className="h-8 w-auto" />
              <p className="font-display text-lg text-paper">
                SmartPrep<span className="text-gold">AI</span>
              </p>
            </div>
            <p className="mt-2 max-w-xs text-sm text-slate">
              Exam-ready for secondary school and university — one AI tutor,
              every subject.
            </p>
          </div>

          <div>
            <p className="text-xs uppercase tracking-wide text-slate">Get help</p>
            <div className="mt-3 flex items-center gap-4">
              <a
                href={`mailto:${SUPPORT_EMAIL}`}
                title={SUPPORT_EMAIL}
                aria-label="Email support"
                className="flex items-center gap-2 text-sm text-slate hover:text-gold"
              >
                <Mail size={18} />
                <span className="hidden sm:inline">{SUPPORT_EMAIL}</span>
              </a>
            </div>
            <a
              href={WHATSAPP_LINK}
              target="_blank"
              rel="noopener noreferrer"
              title={`WhatsApp only: ${WHATSAPP_NUMBER}`}
              aria-label="Chat with us on WhatsApp"
              className="mt-3 flex items-center gap-2 text-sm text-slate hover:text-gold"
            >
              <MessageCircle size={18} />
              <span>{WHATSAPP_NUMBER} (WhatsApp only)</span>
            </a>
          </div>

          <div>
            <p className="text-xs uppercase tracking-wide text-slate">Follow @smartprepai</p>
            <div className="mt-3 flex items-center gap-4">
              {SOCIALS.map(({ icon: Icon, href, label }) => (
                <a
                  key={label}
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={label}
                  title={label}
                  className="text-slate hover:text-gold"
                >
                  <Icon size={20} />
                </a>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-10 border-t border-white/10 pt-6 text-xs text-slate">
          <p>© {new Date().getFullYear()} SmartPrepAI. Copyright and Powered by Smartway IT Solutions Limited.</p>
        </div>
      </div>
    </footer>
  );
}
