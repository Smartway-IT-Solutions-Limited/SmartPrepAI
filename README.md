# SmartPrepAI

AI-powered adaptive exam prep platform for WAEC/JAMB/NECO/GCE and university
students. Web app (React) + FastAPI backend + PostgreSQL, with an entirely
open-source RAG pipeline (Qdrant + BGE-M3 + Groq) for the AI tutor, and
Paystack for subscriptions.

This is the **web MVP** scaffold: auth & roles, Paystack billing with the
2-free-use pass, a CBT-style mock test engine, and the RAG-backed AI tutor
with citations. Mobile (React Native), offline sync (WatermelonDB), WhatsApp
reports, the Tutorial Center admin portal, and USSD/SMS billing from the BRD
are the natural next phases on top of this foundation — the data model
already has the hooks for them (roles, `TutorialCenter`, `GuardianStudentLink`).

---

## 1. Project layout

```
smartprepai/
  backend/     FastAPI + PostgreSQL + the RAG pipeline
  frontend/    React + Vite + Tailwind
```

## 2. Local development

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # fill in what you have; everything has a safe default/fallback
```

You need a local Postgres and (for the RAG tutor) a Qdrant instance running.
Easiest path: `docker run -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:16`
and `docker run -p 6333:6333 qdrant/qdrant`.

```bash
python -m app.seed          # loads sample WAEC/JAMB questions so mock tests work immediately
uvicorn app.main:app --reload
```

API docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
cp .env.example .env        # VITE_API_URL=http://localhost:8000
npm run dev
```

App: `http://localhost:5173`

---

## 3. Where to plug in each integration

Everything below is a **config value only** — no code changes needed unless noted.

| Integration | File | What to do |
|---|---|---|
| **MyQuest** (past questions) | `backend/.env` → `MYQUEST_API_KEY`, `MYQUEST_BASE_URL` | Get credentials from MyQuest, set the two vars. Until then, the app runs on the local seeded question bank automatically. Once you have MyQuest's real API docs, open `backend/app/services/myquest_service.py` — the request/response field mapping has `TODO` comments marking exactly what to adjust. |
| **Paystack** (payments) | `backend/.env` → `PAYSTACK_SECRET_KEY`, `PAYSTACK_PUBLIC_KEY` | Get test keys from your Paystack dashboard. Also add your webhook URL (`https://<your-railway-url>/api/subscriptions/paystack/webhook`) in Paystack's dashboard under Settings → API Keys & Webhooks. |
| **Groq** (AI tutor LLM) | `backend/.env` → `GROQ_API_KEY` | Free key at console.groq.com. |
| **Qdrant** (vector DB) | `backend/.env` → `QDRANT_URL`, `QDRANT_API_KEY` | Deploy Qdrant on Railway (1-click template), or point at a local instance for dev. |
| **Frontend → backend URL** | `frontend/.env` → `VITE_API_URL` | Your deployed Railway backend URL. |

None of these require touching more than the `.env` file, except MyQuest,
where the exact field names will need a small tweak once you have their
actual API docs (the file is small and every line that might need to change
is marked).

---

## 4. Feeding the AI tutor's knowledge base

The tutor only knows what's been ingested into Qdrant. For each textbook:

```bash
cd backend
pip install marker-pdf          # kept out of requirements.txt — this step runs offline/locally
python scripts/ingest.py --pdf calculus1.pdf --book "Calculus 1" --subject Mathematics
```

This parses the PDF with Marker (preserves LaTeX + page numbers), chunks it
with LlamaIndex, embeds with the open-source `BAAI/bge-m3` model, and upserts
into your Qdrant collection. Do this once per textbook/subject — it's a batch
job, not something that runs per request.

---

## 5. Deployment

**Recommended split:**
- **Frontend → Vercel.** Connect the repo, set root directory to `frontend`,
  set `VITE_API_URL` to your Railway backend URL in Vercel's env vars.
- **Backend + Postgres + Redis + Qdrant → Railway.** Create a new project,
  add a Postgres plugin (Railway gives you `DATABASE_URL` — just prefix it
  with `postgresql+asyncpg://` instead of `postgresql://` for the async driver),
  add Qdrant via Railway's 1-click template, deploy the `backend` folder as a
  service (it has a `Dockerfile` and `railway.json` already configured), and
  set all the `.env.example` variables as Service Variables.

Why this split and not Cloudflare Pages' serverless functions for the
backend: your backend needs persistent Postgres connections, background-safe
webhook handling, and room for AI calls that can run a few seconds — all
things Cloudflare Workers' short-lived, connectionless execution model fights
against. Railway runs your FastAPI app as a normal long-running process, which
matches what you're actually building.

**Before going live:**
1. Switch Paystack keys from `sk_test_...` to `sk_live_...`.
2. Set `FRONTEND_URL` on the backend to your real Vercel domain (CORS is
   locked to this single origin — don't widen it to `*`).
3. Re-run the Paystack webhook test from their dashboard against your live
   `/api/subscriptions/paystack/webhook` URL to confirm signature verification
   passes.
4. Switch `init_db()`'s auto-create-tables behavior for Alembic migrations
   once your schema stabilizes (`init_db()` is fine for getting started, but
   prefer explicit migrations before you have real user data to protect).

---

## 6. Pricing structure

Plans are split by audience (Secondary vs. Tertiary) and billing cycle
(Monthly vs. Semester, ~4 months). The authoritative prices live in
`backend/app/services/paystack_service.py::PRICING_NGN` — the frontend's
`frontend/src/pages/Pricing.tsx` mirrors these for display only, and the
backend re-derives the actual charge from the `plan` + `billing_cycle` sent
in the request, never from a client-supplied amount. If you change a price,
update both files so they stay in sync (there's a comment marking this in
both).

Tertiary plans (`tertiary_standard`, `tertiary_pro`, `tertiary_group`) aren't
split further by field of study — Medicine, Engineering, Accounting, Law,
etc. are all covered by the same tiers, differentiated by tutoring depth and
group size rather than subject. What subjects are actually available depends
on which textbooks have been run through `scripts/ingest.py`.

## 7. Scaling notes for "hundreds of students + CBT centres"

- Railway's shared/starter tiers comfortably handle this range; the main
  thing to watch is the embedding model (`BAAI/bge-m3`) — it's a real model
  running on your backend's CPU, so under concurrent AI-tutor load, consider
  either a larger Railway instance or swapping to `BAAI/bge-small-en-v1.5`
  (5x smaller, still strong quality) if response times climb.
- Add Redis-backed rate limiting on `/api/tutor/ask` and `/api/mock-tests/start`
  before opening this up publicly — a `REDIS_URL` is already wired into config
  for this.
- For CBT centres running many students concurrently on-site (a shared,
  patchy connection is common in Nigerian tutorial centres), the BRD's
  offline-first mobile plan (WatermelonDB) matters more than backend scaling —
  that's the next phase to prioritize once this web MVP is validated.
