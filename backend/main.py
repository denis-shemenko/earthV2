import logging
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from models import AnswerRequest, QuestionResponse, QuestionOption, FirstQuestionRequest
from quiz_engine import generate_question, generate_first_question
from sessions import create_session
from graph import start_session_with_topics, store_first_question, store_selected_answer_and_next, get_graph_with_options, get_last_N_answers

app = FastAPI()

# Allow all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL: ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/start-session", response_model=QuestionResponse)
def start_session():
    session_id = create_session()
    topics = ["Физика", "История", "География", "Животные", "Кино", "Искусство"]
    start_session_with_topics(session_id, topics)

    return QuestionResponse(
        question="Выбор темы", 
        options=[QuestionOption(text=topic, isCorrect=False) for topic in topics], 
        session_id=session_id
    )

@app.post("/first-question", response_model=QuestionResponse)
def create_first_question(req: FirstQuestionRequest):
    q = generate_first_question(req.topic)
    store_first_question(
        session_id=req.session_id,
        question_text=q["question"],
        answers=q["options"]
    )
    return QuestionResponse(**q, session_id=req.session_id)

@app.post("/answer", response_model=QuestionResponse)
def answer(req: AnswerRequest):
    user_id = "user-001"

    # last_topic = "История"  # позже: достаём из сессии    
    # update_session(req.session_id, last_topic, req.chosen_answer)

    next_topic = req.chosen_answer
    prev_answers = get_last_N_answers(req.session_id)["answers"]

    #print(f'prev answers were: {prev_answers}')

    q = generate_question(next_topic, previous_answers=prev_answers)

    #print(f'Got question from LLM: {q}')

    store_selected_answer_and_next(
        question_text=req.question_text,
        selected_answer_text=req.chosen_answer,
        next_question_text=q["question"],
        answer_options=q["options"]
    )

    return QuestionResponse(**q, session_id=req.session_id)

@app.get("/graph/{session_id}")
def get_graph_with_answers(session_id: str):
    try:
        data = get_graph_with_options(session_id)
        return JSONResponse(content=data)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
