from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models import TutorMessage, User
from app.routers.questions import _has_active_subscription
from app.schemas import TutorAskRequest, TutorAskResponse
from app.services.rag_service import ask_tutor

router = APIRouter(prefix="/api/tutor", tags=["tutor"])


@router.post("/ask", response_model=TutorAskResponse)
async def ask(
    payload: TutorAskRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # AI tutoring is a paid-plan feature per the BRD (Distinction plan gets
    # "priority Socratic tutoring"); free-pass users can still try it using
    # their 2 free uses for consistency with the mock-test gating.
    if current_user.free_uses_remaining <= 0 and not await _has_active_subscription(db, current_user):
        raise HTTPException(
            status_code=402,
            detail="You've used your free uses. Subscribe to a plan to keep using the AI tutor.",
        )

    try:
        result = ask_tutor(payload.question, payload.mode, payload.subject)
    except Exception as exc:  # noqa: BLE001 - surface a clean error to the client
        raise HTTPException(status_code=503, detail=f"AI tutor is temporarily unavailable: {exc}")

    if not await _has_active_subscription(db, current_user):
        current_user.free_uses_remaining -= 1

    db.add(TutorMessage(
        user_id=current_user.id,
        question=payload.question,
        answer=result["answer"],
        citations=result["citations"],
    ))
    await db.commit()

    return TutorAskResponse(answer=result["answer"], citations=result["citations"])
