import asyncio
import httpx
import random
from faker import Faker
from app import get_question_answers

fake = Faker()
API_BASE_URL = "http://localhost:8000/api"
exam_code = "CAT2025"


async def register_aspirant(session_id):
    aspirant = {
        "roll_number": fake.unique.uuid4(),
        "uic": fake.unique.uuid4(),
        "year": 2025,
        "exam_code": exam_code,
        "region_code": "IN",
        "session_id": session_id,
    }
    async with httpx.AsyncClient() as client:
        await client.post(f"{API_BASE_URL}/register", json=aspirant)
    return aspirant

async def submit_exam(session_id, questions):
    num_answers = random.randint(1, 30)
    answers = [
        {"question_id": q["_id"], "choice": random.randint(0, 3)}
        for q in random.sample(questions, num_answers)
    ]
    submission = {"session_id": session_id, "answers": answers}
    async with httpx.AsyncClient() as client:
        await client.post(f"{API_BASE_URL}/submit", json=submission)

async def main():
    questions, _ = await get_question_answers(exam_code)
    if not questions:
        print("No questions found.")
        return
    
    tasks = []
    for i in range(10000):
        print(f'aspirant {i}')
        session_id = fake.uuid4()
        aspirant = await register_aspirant(session_id)
        await submit_exam(aspirant["session_id"], questions)

asyncio.run(main())
