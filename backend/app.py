from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse

from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv 
from motor.motor_asyncio import AsyncIOMotorClient
import os
import asyncio
import certifi
from models import *
from uuid import uuid4
from datetime import datetime, UTC
from collections import defaultdict
from pymongo import UpdateOne

load_dotenv()

mongo_client = AsyncIOMotorClient(os.environ.get('MONGO_CONNECTION_URI'), tlsCAFile=certifi.where())
db = mongo_client["online-test"]  # Database
candidate_collection = db['candidates']
question_colection = db['questions']
answer_collection = db['answers']
evaluation_collection = db['evaluation']
exam_collection = db['exams']
    
# async def insert_document():
#     # Sample document to insert
#     document = {"name": "John Doe", "age": 30, "city": "New York"}

#     # Insert document
#     result = await collection.insert_one(document)
#     print(f"Inserted document ID: {result.inserted_id}")
# asyncio.run(insert_document())
question_bank = {}

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to the specific frontend URL for security
    allow_credentials=True,
    allow_methods=["*"],  # Allows POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)


@app.post('/api/register')
async def register(aspirant: Aspirant):
    await candidate_collection.insert_one(aspirant.model_dump())

@app.post('/api/auth')
async def auth(auth: Auth):
    result = await candidate_collection.find_one({'roll_number': auth.roll_number, 'uic': auth.uic})
    if not result:
        raise HTTPException(status_code=401, detail="Invalid roll number or UIC")

    session_id = uuid4().hex
    
    await candidate_collection.update_one(
        {'_id': result['_id']}, 
        update={'$set': {'session_id': session_id}}
    )
    
    
    
    return {'session_id': session_id}
    # I should set a timer for this session id to expire

@app.get('/api/questions')
async def get_questions(session_id: str):
    result = await candidate_collection.find_one({'session_id': session_id})
    if not result:
        raise HTTPException(status_code=401, detail="Invalid/expired session ID")
    
    exam = await exam_collection.find_one({'exam_code': result['exam_code']})
    
    start = datetime.fromisoformat(exam['exam_start'].replace("Z", "+00:00"))
    end = datetime.fromisoformat(exam['exam_end'].replace("Z", "+00:00"))
    
    now = datetime.now(UTC)
    
    if now < start:
        raise HTTPException(status_code=403, detail="Exam not started yet!")
    elif end < now:
        raise HTTPException(status_code=403, detail="Exam over!")
    
    questions, _ = await get_question_answers(result['exam_code'])
    
    return {
        'questions': questions,
        'exam_start': exam['exam_start'],
        'exam_end': exam['exam_end'],
        'remaining_time': min(
            int((end - now).total_seconds()),
            exam['exam_duration']
        )
    }


async def get_question_answers(exam_code):
    if exam_code not in question_bank:
        questions = await question_colection.find({
            "exam_code": exam_code,
        }).to_list()
        question_bank[exam_code] = {
            'questions': [{k:(str(v) if k == '_id' else v) for k, v in question.items() if k != 'correct_answer'} for question in questions],
            'answers': {str(question['_id']): {'choice': question['correct_answer'], 'subject_code': question['subject_code']} for question in questions}
        }
    return question_bank[exam_code]['questions'], question_bank[exam_code]['answers']
    
@app.post('/api/submit')
async def submit_exam(submission: ExamSubmission, background_tasks: BackgroundTasks):
    result = await candidate_collection.find_one({'session_id': submission.session_id})
    if not result:
        raise HTTPException(status_code=401, detail="Invalid/expired session ID")
    
    submission = submission.model_dump()
    await answer_collection.insert_one({
        'session_id': submission['session_id'],
        'uic': result['uic'],
        'exam_code': result['exam_code'],
        'candidate_id': str(result['_id']),
        'answers': submission['answers']
    })
    
    background_tasks.add_task(evaluate_submission, {
        'session_id': submission['session_id'],
        'candidate_id': str(result['_id']),
        'exam_code': result['exam_code']
    })
    
    return {
        'status': 'complete'
    }


async def evaluate_submission(kwargs):
    _, answers = await get_question_answers(kwargs['exam_code'])
    answer_submission = await answer_collection.find_one({'session_id': kwargs['session_id']}, projection=['answers'])
    
    score = 0
    subwise_score = defaultdict(int)
    
    for user_answer in answer_submission['answers']:
        question_id = user_answer['question_id']
        choice = user_answer['choice']
        if choice == answers[question_id]['choice']:
            score += 5
            subwise_score[answers[question_id]['subject_code']] += 5
        else:
            score -= 1
            subwise_score[answers[question_id]['subject_code']] -= 1
    
    await evaluation_collection.insert_one({
        'candidate_id': kwargs['candidate_id'],
        'session_id': kwargs['session_id'],
        'score': score,
        'exam_code': kwargs['exam_code'],
        'subjectwise_score': subwise_score
    })


@app.post('/api/calculate-results')
async def calculate_results(exam_code: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(calculate_rank_and_percentile, exam_code)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Rank Calculation Task Triggered"}
    )

async def calculate_rank_and_percentile(exam_code):
    cursor = evaluation_collection.find({"exam_code": exam_code}).sort("score", -1)
    
    total_participants = await evaluation_collection.count_documents({"exam_code": exam_code})
    
    rank = 0
    previous_score = None
    candidates_with_same_score = 0
    cumulative_count = 0
    bulk_updates = []

    async for user in cursor:
        if user["score"] != previous_score:
            # New score detected, assign new rank
            rank += candidates_with_same_score
            candidates_with_same_score = 1
        else:
            # Same score as previous, share the same rank
            candidates_with_same_score += 1

        cumulative_count += 1
        percentile = 100 * (cumulative_count / total_participants)

        bulk_updates.append(
            UpdateOne(
                {"_id": user["_id"]},
                {"$set": {"rank": rank + 1, "percentile": 100 - percentile}}
            )
        )

        if len(bulk_updates) >= 1000:
            await evaluation_collection.bulk_write(bulk_updates)
            bulk_updates = []

        previous_score = user["score"]

    if bulk_updates:
        await evaluation_collection.bulk_write(bulk_updates)
    
    print('Evaluation Complete')

async def calculate_rank_and_percentile_with_pipeline(exam_code):
    overall_rank_pipeline = [
        {"$match": {"exam_code": exam_code}},
        {"$setWindowFields": {
            "partitionBy": None,
            "sortBy": {"score": -1},
            "output": {
                "rank": {"$rank": {}},
                "total_count": {"$count": {}}
            }
        }},
        {"$set": {
            "percentile": {"$multiply": [{"$divide": [{"$subtract": ["$total_count", "$rank"]}, "$total_count"]}, 100]}
        }},
        {"$unset": "total_count"}
    ]
    
    bulk_updates = []
    async for doc in evaluation_collection.aggregate(overall_rank_pipeline):
        bulk_updates.append(UpdateOne(
            {"_id": doc["_id"]},
            {"$set": {"rank": doc["rank"], "percentile": doc["percentile"]}}
        ))
        if len(bulk_updates) >= 500:
            await evaluation_collection.bulk_write(bulk_updates)
            bulk_updates = []

    if bulk_updates:
        await evaluation_collection.bulk_write(bulk_updates)
    
    # 2️⃣ Pipeline for Subject-wise Rank & Percentile Calculation
    subject_rank_pipeline = [
        {"$match": {"exam_code": exam_code}},
        {"$unwind": "$subjectwise_score"},  # Convert subjectwise_score map into separate docs
        {"$setWindowFields": {
            "partitionBy": "$subjectwise_score.k",
            "sortBy": {"subjectwise_score.v": -1},
            "output": {
                "subject_rank": {"$rank": {}},
                "total_subject_count": {"$count": {}}
            }
        }},
        {"$set": {
            "subject_percentile": {"$multiply": [{"$divide": [{"$subtract": ["$total_subject_count", "$subject_rank"]}, "$total_subject_count"]}, 100]}
        }},
        {"$group": {
            "_id": "$_id",
            "subjectwise_rank": {"$push": {"k": "$subjectwise_score.k", "v": "$subject_rank"}},
            "subjectwise_percentile": {"$push": {"k": "$subjectwise_score.k", "v": "$subject_percentile"}}
        }},
        {"$set": {
            "subjectwise_rank": {"$arrayToObject": "$subjectwise_rank"},
            "subjectwise_percentile": {"$arrayToObject": "$subjectwise_percentile"}
        }}
    ]

    bulk_updates = []
    async for doc in evaluation_collection.aggregate(subject_rank_pipeline):
        bulk_updates.append(UpdateOne(
            {"_id": doc["_id"]},
            {"$set": {
                "subjectwise_rank": doc["subjectwise_rank"],
                "subjectwise_percentile": doc["subjectwise_percentile"]
            }}
        ))
        if len(bulk_updates) >= 500:
            await evaluation_collection.bulk_write(bulk_updates)
            bulk_updates = []

    if bulk_updates:
        await evaluation_collection.bulk_write(bulk_updates)
    
    print('Evaluation Complete')
    
if __name__ == '__main__':
    uvicorn.run(app)