from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models import (
    MockTest, MockTestAnswer, Question, Subscription, SubscriptionStatus, User,
)
from app.schemas import (
    MockTestOut, MockTestResultOut, QuestionOut, StartMockTestRequest, SubmitMockTestRequest,
)
from app.services.myquest_service import get_questions

router = APIRouter(prefix="/api/mock-tests", tags=["mock-tests"])


async def _has_active_subscription(db: AsyncSession, user: User) -> bool:
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == user.id,
            Subscription.status == SubscriptionStatus.active,
        )
    )
    subs = result.scalars().all()
    now = datetime.now(timezone.utc)
    return any(s.expires_at and s.expires_at > now for s in subs)


@router.post("/start", response_model=MockTestOut)
async def start_mock_test(
    payload: StartMockTestRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # --- Access control: free pass (2 uses) OR an active paid subscription ---
    if current_user.free_uses_remaining <= 0 and not await _has_active_subscription(db, current_user):
        raise HTTPException(
            status_code=402,
            detail="You've used your 2 free mock exams. Subscribe to a plan to continue.",
        )

    questions = await get_questions(db, payload.exam_type, payload.subject, payload.num_questions)
    if not questions:
        raise HTTPException(
            status_code=404,
            detail=f"No questions available yet for {payload.subject} ({payload.exam_type.value}).",
        )

    mock_test = MockTest(
        user_id=current_user.id,
        exam_type=payload.exam_type,
        subject=payload.subject,
        total_questions=len(questions),
    )
    db.add(mock_test)

    if not await _has_active_subscription(db, current_user):
        current_user.free_uses_remaining -= 1

    await db.commit()
    await db.refresh(mock_test)

    return MockTestOut(
        id=mock_test.id,
        exam_type=mock_test.exam_type,
        subject=mock_test.subject,
        total_questions=mock_test.total_questions,
        questions=[QuestionOut.model_validate(q) for q in questions],
    )


@router.post("/{mock_test_id}/submit", response_model=MockTestResultOut)
async def submit_mock_test(
    mock_test_id: str,
    payload: SubmitMockTestRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(MockTest).where(MockTest.id == mock_test_id))
    mock_test = result.scalar_one_or_none()
    if not mock_test or mock_test.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Mock test not found")
    if mock_test.completed_at:
        raise HTTPException(status_code=409, detail="This mock test was already submitted")

    breakdown = []
    correct_count = 0
    for item in payload.answers:
        q_result = await db.execute(select(Question).where(Question.id == item.question_id))
        question = q_result.scalar_one_or_none()
        if not question:
            continue
        is_correct = question.correct_option.upper() == item.selected_option.upper()
        correct_count += int(is_correct)

        db.add(MockTestAnswer(
            mock_test_id=mock_test.id,
            question_id=question.id,
            selected_option=item.selected_option,
            is_correct=is_correct,
        ))
        breakdown.append({
            "question_id": question.id,
            "correct_option": question.correct_option,
            "selected_option": item.selected_option,
            "is_correct": is_correct,
            "explanation": question.explanation,
        })

    mock_test.score = correct_count
    mock_test.completed_at = datetime.now(timezone.utc)
    await db.commit()

    total = mock_test.total_questions
    return MockTestResultOut(
        mock_test_id=mock_test.id,
        score=correct_count,
        total_questions=total,
        percentage=round((correct_count / total) * 100, 1) if total else 0.0,
        breakdown=breakdown,
    )


@router.get("/history", response_model=list[MockTestResultOut])
async def mock_test_history(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MockTest).where(MockTest.user_id == current_user.id, MockTest.completed_at.is_not(None))
    )
    tests = result.scalars().all()
    return [
        MockTestResultOut(
            mock_test_id=t.id,
            score=t.score or 0,
            total_questions=t.total_questions,
            percentage=round(((t.score or 0) / t.total_questions) * 100, 1) if t.total_questions else 0.0,
            breakdown=[],
        )
        for t in tests
    ]
