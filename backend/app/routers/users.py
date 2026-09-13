from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models import MockTest, User
from app.schemas import MockTestResultOut, UserOut

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/dashboard/summary")
async def dashboard_summary(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Student Workspace: recent mock-test history + running average —
    the weak-point analytics view is a natural next iteration on top of
    MockTestAnswer once there's enough data per subject."""
    result = await db.execute(
        select(MockTest).where(MockTest.user_id == current_user.id, MockTest.completed_at.is_not(None))
    )
    tests = result.scalars().all()
    avg = round(sum((t.score or 0) / t.total_questions for t in tests) / len(tests) * 100, 1) if tests else 0.0

    return {
        "user": UserOut.model_validate(current_user),
        "free_uses_remaining": current_user.free_uses_remaining,
        "tests_completed": len(tests),
        "average_score_pct": avg,
        "recent_tests": [
            MockTestResultOut(
                mock_test_id=t.id,
                score=t.score or 0,
                total_questions=t.total_questions,
                percentage=round(((t.score or 0) / t.total_questions) * 100, 1) if t.total_questions else 0.0,
                breakdown=[],
            )
            for t in tests[-5:]
        ],
    }
