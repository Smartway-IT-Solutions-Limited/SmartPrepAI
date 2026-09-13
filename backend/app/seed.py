"""
Seeds a handful of sample WAEC/JAMB questions so the mock-test engine works
end-to-end in development before MYQUEST_API_KEY is configured.

Run with:  python -m app.seed
"""
import asyncio

from app.database import AsyncSessionLocal, init_db
from app.models import ExamType, Question

SAMPLE_QUESTIONS = [
    {
        "exam_type": ExamType.JAMB, "subject": "Mathematics", "year": 2023,
        "question_text": "Simplify: 3(x - 2) + 2(x + 5)",
        "options": {"A": "5x + 4", "B": "5x - 4", "C": "x + 4", "D": "5x + 16"},
        "correct_option": "A",
        "explanation": "3(x-2)+2(x+5) = 3x-6+2x+10 = 5x+4.",
    },
    {
        "exam_type": ExamType.JAMB, "subject": "Mathematics", "year": 2022,
        "question_text": "Find the value of x if 2x + 5 = 17",
        "options": {"A": "5", "B": "6", "C": "7", "D": "8"},
        "correct_option": "B",
        "explanation": "2x = 12, so x = 6.",
    },
    {
        "exam_type": ExamType.WAEC, "subject": "English Language", "year": 2023,
        "question_text": "Choose the option that best completes the sentence: 'She has been "
                          "living here ___ five years.'",
        "options": {"A": "since", "B": "for", "C": "from", "D": "during"},
        "correct_option": "B",
        "explanation": "'For' is used with a duration of time; 'since' is used with a starting point.",
    },
    {
        "exam_type": ExamType.WAEC, "subject": "Physics", "year": 2022,
        "question_text": "The SI unit of electric current is the",
        "options": {"A": "Volt", "B": "Ohm", "C": "Ampere", "D": "Watt"},
        "correct_option": "C",
        "explanation": "Electric current is measured in Amperes (A).",
    },
    {
        "exam_type": ExamType.NECO, "subject": "Chemistry", "year": 2023,
        "question_text": "Which of the following is an example of a chemical change?",
        "options": {"A": "Melting of ice", "B": "Rusting of iron", "C": "Boiling of water", "D": "Dissolving sugar"},
        "correct_option": "B",
        "explanation": "Rusting forms a new substance (iron oxide) — a chemical, not physical, change.",
    },
]


async def seed():
    await init_db()
    async with AsyncSessionLocal() as db:
        for q in SAMPLE_QUESTIONS:
            db.add(Question(source="local", **q))
        await db.commit()
    print(f"Seeded {len(SAMPLE_QUESTIONS)} sample questions.")


if __name__ == "__main__":
    asyncio.run(seed())
