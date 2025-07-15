from logging import debug
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from models import QuestionRequest, AnswerRequest, QuestionResponse
from quiz_engine import generate_question
from sessions import create_session, update_session
from graph import save_question_path, save_user_answer, get_graph_with_options 
#get_session_graph, get_session_graph_simplified

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

    save_question_path(
        session_id=session_id,
        question_text=q["question"],
        answer_options=q["options"]
    )

    return QuestionResponse(**q, session_id=session_id)

@app.post("/answer", response_model=QuestionResponse)
def answer(req: AnswerRequest):
    user_id = "user-001"
    last_topic = "История"  # позже: достаём из сессии
    
    update_session(req.session_id, last_topic, req.chosen_answer)
    next_topic = req.chosen_answer
    q = generate_question(next_topic)

    # Сохраняем в графовую БД Neo4j
    # save_question_path(
    #     session_id=req.session_id,
    #     question_text=req.chosen_answer,
    #     answer_options=q["options"]
    # )

    #debug("RESPONSE FROM LLM: %(message)s", q)

    # найти правильный ли был выбранный ответ
    chosen_option = next(opt for opt in q["options"] if opt.text == req.chosen_answer)
    is_correct = chosen_option.isCorrect

    save_user_answer(
        session_id=req.session_id,
        answer_text=req.chosen_answer,
        is_correct=is_correct,
        next_question_text=q["question"],
        next_answers=q["options"]
    )

    return QuestionResponse(**q, session_id=req.session_id)

@app.get("/graph/{session_id}")
def get_graph_with_answers(session_id: str):
    try:
        data = get_graph_with_options(session_id)
        return JSONResponse(content=data)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# @app.get("/graph/{session_id}")
# def get_graph(session_id: str):
#     try:
#         data = get_session_graph_simplified(session_id)
#         return JSONResponse(content=data)
#     except Exception as e:
#         return JSONResponse(status_code=500, content={"error": str(e)})