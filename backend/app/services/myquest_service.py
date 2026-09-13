"""
=====================================================================
 INTEGRATION POINT — MyQuest API (past-questions provider)
=====================================================================
This is the ONLY file you should need to touch to wire in the real
MyQuest API. Everything else (routers, caching, mock-test engine)
already calls `get_questions()` below and doesn't care where the
data came from.

1. Set MYQUEST_API_KEY and MYQUEST_BASE_URL in your .env / Railway vars.
2. Adjust `_call_myquest()` below to match MyQuest's actual request/
   response shape once you have their API docs (endpoint path, auth
   header name, and field names will likely differ from the placeholder
   below — search for "TODO" markers).
3. Nothing else needs to change: questions.py's write-through cache and
   the mock-test engine already consume whatever `get_questions()` returns.

Until step 1 is done, `get_questions()` transparently falls back to the
local Postgres `questions` table (seeded via `python -m app.seed`), so
the whole app works end-to-end in development without a MyQuest key.
"""
import random

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import ExamType, Question


async def _call_myquest(exam_type: str, subject: str, count: int) -> list[dict] | None:
    """Raw call to the MyQuest API. Returns None on any failure so callers
    can gracefully fall back to the local cache instead of erroring out."""
    if not settings.MYQUEST_API_KEY:
        return None

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                # TODO: confirm real path once MyQuest's docs are available.
                f"{settings.MYQUEST_BASE_URL}/v1/questions",
                params={"exam": exam_type, "subject": subject, "limit": count},
                headers={"Authorization": f"Bearer {settings.MYQUEST_API_KEY}"},
            )
            resp.raise_for_status()
            data = resp.json()
            # TODO: adjust field mapping below to MyQuest's real response shape.
            return [
                {
                    "external_id": item.get("id"),
                    "question_text": item.get("question"),
                    "options": item.get("options"),
                    "correct_option": item.get("answer"),
                    "explanation": item.get("explanation"),
                    "year": item.get("year"),
                }
                for item in data.get("results", [])
            ]
    except (httpx.HTTPError, KeyError, ValueError):
        # Network hiccup, bad response shape, etc. — fail soft to local cache.
        return None


async def get_questions(
    db: AsyncSession, exam_type: ExamType, subject: str, count: int = 20
) -> list[Question]:
    """Primary entry point used by the mock-test engine.

    Order of operations (matches the BRD's 'write-through cache' requirement):
      1. Try MyQuest live.
      2. On success, upsert into the local `questions` table (source='myquest')
         so future requests for the same exam/subject are served from
         Postgres instead of hitting MyQuest again.
      3. If MyQuest is not configured or the call fails, serve straight from
         the local cache (source='local' seed data, or previously-cached
         MyQuest rows).
    """
    live = await _call_myquest(exam_type.value, subject, count)

    if live:
        cached: list[Question] = []
        for item in live:
            q = Question(
                external_id=item.get("external_id"),
                source="myquest",
                exam_type=exam_type,
                subject=subject,
                year=item.get("year"),
                question_text=item["question_text"],
                options=item["options"],
                correct_option=item["correct_option"],
                explanation=item.get("explanation"),
            )
            db.add(q)
            cached.append(q)
        await db.commit()
        return cached

    # --- Fallback: local Postgres cache / seed data ---
    result = await db.execute(
        select(Question).where(Question.exam_type == exam_type, Question.subject == subject)
    )
    pool = result.scalars().all()
    if not pool:
        return []
    random.shuffle(pool)
    return pool[:count]
