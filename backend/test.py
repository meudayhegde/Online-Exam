import asyncio
import httpx
import random
from faker import Faker

fake = Faker()
API_BASE_URL = "http://localhost:8000/api"
exam_code = "CAT2025"

async def fetch_questions():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/questions", params={"exam_code": exam_code})
        if response.status_code == 200:
            return response.json()
        return []

async def register_aspirant(session_id):
    aspirant = {
        "roll_number": fake.unique.uuid4(),
        "uic": fake.unique.uuid4(),
        "year": random.randint(2023, 2025),
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
    questions = await fetch_questions()
    if not questions:
        print("No questions found.")
        return
    
    tasks = []
    for _ in range(10000):
        session_id = fake.uuid4()
        tasks.append(register_aspirant(session_id))
    aspirants = await asyncio.gather(*tasks)
    
    tasks = [submit_exam(a["session_id"], questions) for a in aspirants]
    await asyncio.gather(*tasks)

asyncio.run(main())
