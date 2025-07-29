from pydantic import BaseModel
from typing import List, Optional

class FirstQuestionRequest(BaseModel):
    session_id: str
    topic: str

class QuestionRequest(BaseModel):
    topic: str

class AnswerRequest(BaseModel):
    session_id: str
    chosen_answer: str
    question_text: str
    is_correct: bool

class QuestionOption(BaseModel):
    text: str
    isCorrect: bool

class QuestionResponse(BaseModel):
    question: str
    options: List[QuestionOption]
    #correct_answer: str
    session_id: str
    ship_event: Optional[dict]
    ship_status: Optional[dict]
