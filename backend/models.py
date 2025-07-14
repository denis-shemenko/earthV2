from pydantic import BaseModel
from typing import List

class QuestionRequest(BaseModel):
    topic: str

class AnswerRequest(BaseModel):
    session_id: str
    chosen_answer: str

class QuestionOption(BaseModel):
    text: str
    isCorrect: bool

class QuestionResponse(BaseModel):
    question: str
    options: List[QuestionOption]
    #correct_answer: str
    session_id: str
