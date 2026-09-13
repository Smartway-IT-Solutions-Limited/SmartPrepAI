from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models import BillingCycle, ExamType, SubscriptionPlan, SubscriptionStatus, UserRole


# ---------- Auth ----------
class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    phone: str | None = None
    password: str = Field(min_length=8)
    role: UserRole = UserRole.student


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    role: UserRole
    free_uses_remaining: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Subscriptions / Paystack ----------
class InitPaymentRequest(BaseModel):
    plan: SubscriptionPlan
    billing_cycle: BillingCycle = BillingCycle.monthly


class InitPaymentResponse(BaseModel):
    authorization_url: str
    access_code: str
    reference: str
    public_key: str


class SubscriptionOut(BaseModel):
    id: str
    plan: SubscriptionPlan
    billing_cycle: BillingCycle
    status: SubscriptionStatus
    started_at: datetime | None
    expires_at: datetime | None

    class Config:
        from_attributes = True


# ---------- Questions / Mock tests ----------
class QuestionOut(BaseModel):
    id: str
    exam_type: ExamType
    subject: str
    year: int | None
    question_text: str
    options: dict

    class Config:
        from_attributes = True


class StartMockTestRequest(BaseModel):
    exam_type: ExamType
    subject: str
    num_questions: int = 20


class MockTestOut(BaseModel):
    id: str
    exam_type: ExamType
    subject: str
    total_questions: int
    questions: list[QuestionOut]


class SubmitAnswerItem(BaseModel):
    question_id: str
    selected_option: str


class SubmitMockTestRequest(BaseModel):
    answers: list[SubmitAnswerItem]


class MockTestResultOut(BaseModel):
    mock_test_id: str
    score: int
    total_questions: int
    percentage: float
    breakdown: list[dict]


# ---------- AI Tutor (RAG) ----------
class TutorAskRequest(BaseModel):
    question: str = Field(min_length=3)
    subject: str | None = None
    mode: str = Field(default="simplify", pattern="^(simplify|deep_dive)$")


class Citation(BaseModel):
    book: str
    chapter: str | None = None
    page: int | None = None
    snippet: str


class TutorAskResponse(BaseModel):
    answer: str
    citations: list[Citation]
