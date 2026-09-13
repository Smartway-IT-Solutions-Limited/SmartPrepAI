from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import auth, questions, subscriptions, tutor, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()  # for production, switch to `alembic upgrade head` in your deploy step
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

# Locked to the actual frontend origin — never use "*" once Paystack/auth cookies are live.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(subscriptions.router)
app.include_router(questions.router)
app.include_router(tutor.router)
app.include_router(users.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}
