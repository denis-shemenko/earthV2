import logging
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from models import AnswerRequest, QuestionResponse, QuestionOption, FirstQuestionRequest
from quiz_engine import generate_next_topics, generate_question_for_topic, generate_first_question
from sessions import create_session
from graph import start_session_with_topics, store_first_question, store_selected_answer_and_next, get_graph_with_options, get_last_N_answers
from ship_logic import apply_answer_result, ship_status, init_ship_state
from typing import List

app = FastAPI()

# Allow all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL: ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ship_states = {}  # session_id -> ShipState

@app.post("/start-session", response_model=QuestionResponse)
def start_session():
    session_id = create_session()
    topics = ["Физика", "История", "География", "Животные", "Кино", "Искусство"]
    start_session_with_topics(session_id, topics)

    return QuestionResponse(
        question="Выбор темы", 
        options=[QuestionOption(text=topic, isCorrect=False) for topic in topics], 
        session_id=session_id,
        ship_event=None,
        ship_status=None
    )

@app.post("/first-question", response_model=QuestionResponse)
def create_first_question(req: FirstQuestionRequest):
    session_id = create_session()
    q = generate_first_question(req.topic)

    store_first_question(
        session_id=session_id,
        question_text=q["question"],
        answers=q["options"]
    )

    return {
        "session_id": session_id,
        "ship_event": None,
        "ship_status": None,
        "question": q["question"],
        "options": q["options"]
    }

@app.post("/answer")
def answer(req: AnswerRequest):
    # 1. Получить или создать состояние корабля
    ship_state = ship_states.get(req.session_id)
    if not ship_state:
        ship_state = init_ship_state()
        ship_states[req.session_id] = ship_state

    # 2. Применить результат к кораблю
    result = apply_answer_result(ship_state, req.is_correct)

    # 3. Generate 1-4 new topics instead of a question
    next_topic = req.chosen_answer
    prev_answers = get_last_N_answers(req.session_id)["answers"]    
    possible_topics = ["Физика", "История", "Музыка", "Математика", "Биология", "Спорт", "Кино", "Животные", "Литература", "Технологии", "Природа", "Философия"]
    new_topics = generate_next_topics(
        previous_answer=next_topic,
        possible_topics=possible_topics,
        previous_answers=prev_answers
    )

    # 4. Store the answer (but not the next question yet)
    store_selected_answer_and_next_topics(
        question_text=req.question_text,
        selected_answer_text=req.chosen_answer,
        next_question_text="",  # Will be filled when topic is selected
        answer_options=[]
    )

    return {
        "session_id": req.session_id,
        "ship_event": result,
        "ship_status": ship_status(ship_state),
        "topics": new_topics  # Return the generated topics instead of a question
    }

@app.post("/topic", response_model=QuestionResponse)
def generate_question_for_chosen_topic(req: dict):
    """
    Generate a question for the chosen topic.
    Expected request body: {"session_id": "string", "chosen_topic": "string"}
    """
    session_id = req.get("session_id")
    chosen_topic = req.get("chosen_topic")
    
    if not session_id or not chosen_topic:
        return JSONResponse(
            status_code=400, 
            content={"error": "session_id and chosen_topic are required"}
        )

    # Get previous answers to avoid repetition
    prev_answers = get_last_N_answers(session_id)["answers"]
    
    # Generate question for the chosen topic
    q = generate_question_for_topic(
        chosen_topic=chosen_topic,
        previous_answers=prev_answers
    )

    # Update the stored next question with the generated question
    store_selected_answer_and_next(
        question_text="",  # This was already stored in /answer
        selected_answer_text=chosen_topic,
        next_question_text=q["question"],
        answer_options=q["options"]
    )

    return {
        "session_id": session_id,
        "ship_event": None,
        "ship_status": None,
        "question": q["question"],
        "options": q["options"]
    }

@app.get("/graph/{session_id}")
def get_graph_with_answers(session_id: str):
    try:
        data = get_graph_with_options(session_id)
        return JSONResponse(content=data)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
