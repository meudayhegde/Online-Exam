from pydantic import BaseModel, Field

class Auth(BaseModel):
    roll_number: str
    uic: str
    
class Answer(BaseModel):
    question_id: str
    choice: int
    
class ExamSubmission(BaseModel):
    session_id: str
    answers: list[Answer]
    
class Aspirant(BaseModel):
    roll_number: str
    uic: str
    year: int
    exam_code: str = Field(default="CAT2025")
    region_code: str = Field(default="IN")
    session_id: str