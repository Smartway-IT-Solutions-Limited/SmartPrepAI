import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean, DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text, func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class UserRole(str, enum.Enum):
    student = "student"
    guardian = "guardian"
    tutorial_center_admin = "tutorial_center_admin"
    platform_admin = "platform_admin"


class SubscriptionPlan(str, enum.Enum):
    free_pass = "free_pass"
    # Secondary / exam-prep (WAEC, JAMB, NECO, GCE)
    secondary_standard = "secondary_standard"
    secondary_pro = "secondary_pro"
    secondary_guardian = "secondary_guardian"
    # Tertiary / university & polytechnic — spans Maths, Medicine, Accounting,
    # Engineering and any other course once its textbooks are ingested into
    # the RAG knowledge base; the plan tiers below differ by tutoring depth
    # and group size, not by field of study.
    tertiary_standard = "tertiary_standard"
    tertiary_pro = "tertiary_pro"
    tertiary_group = "tertiary_group"


class BillingCycle(str, enum.Enum):
    monthly = "monthly"
    semester = "semester"


class SubscriptionStatus(str, enum.Enum):
    active = "active"
    expired = "expired"
    cancelled = "cancelled"
    pending = "pending"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    success = "success"
    failed = "failed"


class ExamType(str, enum.Enum):
    WAEC = "WAEC"
    JAMB = "JAMB"
    NECO = "NECO"
    GCE = "GCE"
    UNIVERSITY = "UNIVERSITY"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.student)
    free_uses_remaining: Mapped[int] = mapped_column(Integer, default=2)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    tutorial_center_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("tutorial_centers.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user")
    mock_tests: Mapped[list["MockTest"]] = relationship(back_populates="user")


class GuardianStudentLink(Base):
    """Lets a Guardian-plan account cover up to 3 student profiles."""
    __tablename__ = "guardian_student_links"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    guardian_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"))
    student_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TutorialCenter(Base):
    __tablename__ = "tutorial_centers"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(150))
    admin_user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    bulk_license_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"))
    plan: Mapped[SubscriptionPlan] = mapped_column(Enum(SubscriptionPlan))
    billing_cycle: Mapped[BillingCycle] = mapped_column(Enum(BillingCycle), default=BillingCycle.monthly)
    status: Mapped[SubscriptionStatus] = mapped_column(Enum(SubscriptionStatus), default=SubscriptionStatus.pending)
    paystack_customer_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="subscriptions")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"))
    subscription_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("subscriptions.id"), nullable=True)
    paystack_reference: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    plan: Mapped[SubscriptionPlan] = mapped_column(Enum(SubscriptionPlan))
    billing_cycle: Mapped[BillingCycle] = mapped_column(Enum(BillingCycle), default=BillingCycle.monthly)
    amount_kobo: Mapped[int] = mapped_column(Integer)  # Paystack works in kobo
    currency: Mapped[str] = mapped_column(String(10), default="NGN")
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.pending)
    raw_webhook_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Question(Base):
    """Local cache/fallback of past questions. When MYQUEST_API_KEY is set,
    questions.py first tries MyQuest live, and writes-through into this table
    so repeated requests don't re-hit the external API (per the BRD's
    'local PostgreSQL write-through cache' requirement)."""
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    external_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(20), default="local")  # "myquest" | "local"
    exam_type: Mapped[ExamType] = mapped_column(Enum(ExamType))
    subject: Mapped[str] = mapped_column(String(80), index=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    question_text: Mapped[str] = mapped_column(Text)
    options: Mapped[dict] = mapped_column(JSON)  # {"A": "...", "B": "...", ...}
    correct_option: Mapped[str] = mapped_column(String(5))
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MockTest(Base):
    __tablename__ = "mock_tests"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"))
    exam_type: Mapped[ExamType] = mapped_column(Enum(ExamType))
    subject: Mapped[str] = mapped_column(String(80))
    total_questions: Mapped[int] = mapped_column(Integer)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="mock_tests")
    answers: Mapped[list["MockTestAnswer"]] = relationship(back_populates="mock_test")


class MockTestAnswer(Base):
    __tablename__ = "mock_test_answers"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    mock_test_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("mock_tests.id"))
    question_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("questions.id"))
    selected_option: Mapped[str | None] = mapped_column(String(5), nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    mock_test: Mapped["MockTest"] = relationship(back_populates="answers")


class TutorMessage(Base):
    """One turn of the RAG-backed AI tutor (question in, cited answer out)."""
    __tablename__ = "tutor_messages"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"))
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    citations: Mapped[list] = mapped_column(JSON, default=list)  # [{book, chapter, page, snippet}, ...]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
