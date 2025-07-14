from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import QuestionRequest, AnswerRequest, QuestionResponse
from quiz_engine import generate_question
from sessions import create_session, update_session
from graph import save_question_path

app = FastAPI()

# Allow all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL: ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/start", response_model=QuestionResponse)
def start_game():
    topic = "История"  # или случайный выбор
    session_id = create_session(topic)
    q = generate_question(topic)
    return QuestionResponse(**q, session_id=session_id)

@app.post("/answer", response_model=QuestionResponse)
def answer(req: AnswerRequest):
    last_topic = "История"  # позже: достаём из сессии
    update_session(req.session_id, last_topic, req.chosen_answer)
    next_topic = req.chosen_answer
    q = generate_question(next_topic)

    # Сохраняем в графовую БД Neo4j
    save_question_path(
        session_id=req.session_id,
        prev_answer=req.chosen_answer,
        new_question=q["question"],
        correct_answer=q["correct_answer"]
    )

    return QuestionResponse(**q, session_id=req.session_id)