from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks

from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv 
from motor.motor_asyncio import AsyncIOMotorClient
import os
import asyncio
import certifi
from models import *
from uuid import uuid4

load_dotenv()

mongo_client = AsyncIOMotorClient(os.environ.get('MONGO_CONNECTION_URI'), tlsCAFile=certifi.where())
db = mongo_client["online-test"]  # Database
candidate_collection = db['candidates']
question_colection = db['questions']
answer_collection = db['answers']
    
# async def insert_document():
#     # Sample document to insert
#     document = {"name": "John Doe", "age": 30, "city": "New York"}

#     # Insert document
#     result = await collection.insert_one(document)
#     print(f"Inserted document ID: {result.inserted_id}")
# asyncio.run(insert_document())


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to the specific frontend URL for security
    allow_credentials=True,
    allow_methods=["*"],  # Allows POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)


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
    
    questions = await question_colection.find({
        "year": result['year'],
        "exam_code": result['exam_code'],
        "region_code": result['region_code']
    }, projection={'correct_answer': False}).to_list()
    questions = [{k:(str(v) if k == '_id' else v) for k, v in question.items()} for question in questions]
    print(questions)
    return {'questions': questions}

@app.post('/api/submit')
async def submit_exam(submission: ExamSubmission):
    result = await candidate_collection.find_one({'session_id': submission.session_id})
    if not result:
        raise HTTPException(status_code=401, detail="Invalid/expired session ID")
    
    await answer_collection.insert_one({
        'session_id': submission.session_id,
        'uic': result['uic'],
        'exam_code': result['exam_code'],
        'candidate_id': str(result['_id']),
        'answers': submission.answers
    })
    
    return {
        'status': 'complete'
    }
    

if __name__ == '__main__':
    uvicorn.run(app)