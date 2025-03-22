from pydantic import BaseModel

class Auth(BaseModel):
    roll_number: str
    uic: str
    
class ExamSubmission(BaseModel):
    session_id: str
    answers: dict[str, int]