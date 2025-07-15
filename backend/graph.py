import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from typing import Any, List
from models import QuestionOption

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

if not all([NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD]):
    raise ValueError("NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD must be set in environment variables.")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# def save_question_path(session_id: str, user_id: str, prev_answer: str, new_question: str, correct_answer: str):
#     with driver.session() as session:
#         session.execute_write(_create_or_link, session_id, user_id, prev_answer, new_question, correct_answer)

# def _create_or_link(tx, session_id, user_id, prev_answer, new_question, correct_answer):
#     query = """
#     MERGE (u:User {id: $user_id})
#     MERGE (s:Session {id: $session_id})
#     MERGE (u)-[:HAS_SESSION]->(s)
    
#     MERGE (prev:Answer {text: $prev_answer})
#     MERGE (q:Question {text: $new_question, correct: $correct_answer})
    
#     MERGE (s)-[:SELECTED]->(prev)
#     MERGE (prev)-[:NEXT]->(q)
    
#     MERGE (t:Topic {name: $prev_answer})
#     MERGE (q)-[:HAS_TOPIC]->(t)
#     """
#     tx.run(query, session_id=session_id, user_id=user_id, prev_answer=prev_answer,
#            new_question=new_question, correct_answer=correct_answer)

def save_question_path(session_id: str, question_text: str, answer_options: List[QuestionOption]):
    with driver.session() as session:
        session.execute_write(_store_question_with_answers, session_id, question_text, answer_options)

def _store_question_with_answers(tx, session_id, question_text, answer_options):
    # 1. Найти сессию
    tx.run("""
        MERGE (s:Session {id: $session_id})
        WITH s
        MERGE (q:Question {text: $question})
        WITH s, q
        FOREACH (opt IN $options |
            MERGE (a:Answer {text: opt.text})
            SET a.correct = opt.isCorrect
            MERGE (q)-[:HAS_OPTION]->(a)
        )
    """, session_id=session_id, question=question_text, options=answer_options)

def save_user_answer(session_id: str, answer_text: str, is_correct: bool, next_question_text: str, next_answers: List[QuestionOption]):
    with driver.session() as session:
        session.execute_write(_store_user_answer, session_id, answer_text, is_correct, next_question_text, next_answers)

def _store_user_answer(tx, session_id, answer_text, is_correct, next_question_text, next_answers):
        tx.run("""
        MATCH (s:Session {id: $session_id})
        MATCH (a:Answer {text: $answer_text})
        CREATE (s)-[:SELECTED {isCorrect: $is_correct}]->(a)
        MERGE (q:Question {text: $next_question})
        MERGE (a)-[:NEXT]->(q)
        FOREACH (opt IN $next_options |
            MERGE (ans:Answer {text: opt.text})
            SET ans.correct = opt.isCorrect
            MERGE (q)-[:HAS_OPTION]->(ans)
        )
    """, session_id=session_id, answer_text=answer_text,
         next_question=next_question_text, next_options=next_answers)

# LATEST WAY. With Options!
def get_graph_with_options(session_id: str) -> dict:
    with driver.session() as session:
        return session.execute_read(_build_graph_with_options, session_id)

def _build_graph_with_options(tx, session_id: str):
    query = """
    MATCH (s:Session {id: $session_id})-[:SELECTED*0..]->(a:Answer)-[:NEXT]->(q:Question)
    OPTIONAL MATCH (q)-[:HAS_OPTION]->(opt:Answer)
    OPTIONAL MATCH (s)-[sel:SELECTED]->(opt)
    RETURN q, opt, sel.isCorrect as isCorrectSelected, opt.correct as isCorrect
    """

    result = tx.run(query, session_id=session_id)
    nodes: dict[str, dict[str, object]] = {"home": {"id": "home", "label": "🌍 Дом", "type": "home"}}
    links = []

    seen_questions = set()

    for record in result:
        q = record["q"]
        opt = record["opt"]
        is_correct = record["isCorrect"]
        is_selected = record["isCorrectSelected"] is not None
        is_correct_selected = record["isCorrectSelected"]

        qid = q.id
        if qid not in nodes:
            nodes[qid] = {
                "id": qid,
                "label": q.get("text")[:50] + "...",
                "type": "question",
                "isCurrent": True  # пока последний считается активным
            }
            if len(seen_questions) == 0:
                links.append({"source": "home", "target": qid, "label": "LAUNCH"})
            seen_questions.add(qid)

        if opt:
            oid = opt.id
            nodes[oid] = {
                "id": oid,
                "label": opt.get("text"),
                "type": "answer",
                "isCorrect": is_correct,
                "isSelected": is_selected,
                "isCorrectSelected": is_correct_selected
            }
            links.append({"source": qid, "target": oid, "label": "HAS_OPTION"})

    return {
        "nodes": list(nodes.values()),
        "links": links
    }


# First approach
def get_session_graph(session_id: str) -> dict:
    with driver.session() as session:
        return session.execute_read(_fetch_graph_data, session_id)

def _fetch_graph_data(tx, session_id: str):
    query = """
    MATCH (s:Session {id: $session_id})-[:SELECTED]->(a:Answer)-[:NEXT]->(q:Question)
    RETURN s, a, q
    """

    result = tx.run(query, session_id=session_id)

    nodes = {
        "start": {
            "id": "start",
            "label": "🌍 Земля",
            "type": "start"
        }
    }
    links = []

    for record in result:
        s = record["s"]
        a = record["a"]
        q = record["q"]

        if a:
            nodes[a.id] = {
                "id": a.id,
                "label": a.get("text"),
                "type": "answer"
            }
        if q:
            nodes[q.id] = {
                "id": q.id,
                "label": q.get("text"),
                "type": "question"
            }

        if a and q:
            links.append({"source": a.id, "target": q.id, "label": "NEXT"})

    # Стартовая точка ведёт к первому answer (если есть)
    if result.peek():
        first_a = result.peek()["a"]
        if first_a:
            links.append({"source": "start", "target": first_a.id, "label": "START"})

    return {
        "nodes": list(nodes.values()),
        "links": links
    }

# Simplified way
def get_session_graph_simplified(session_id: str) -> dict:
    with driver.session() as session:
        return session.execute_read(_fetch_simplified_graph, session_id)

def _fetch_simplified_graph(tx, session_id: str):
    query = """
    MATCH (s:Session {id: $session_id})-[:SELECTED]->(a:Answer)-[:NEXT]->(q:Question)
    WITH collect(q) AS questions
    RETURN questions
    """
    result = tx.run(query, session_id=session_id)

    questions = []
    for record in result:
        q_list = record["questions"]
        for i, q in enumerate(q_list):
            questions.append({
                "id": q.id,
                "label": q.get("text")[:40] + "...",
                "type": "question",
                "topic": q.get("correct"),
                "isCurrent": (i == len(q_list) - 1)  # последний — текущий
            })

    nodes = [{
        "id": "home",
        "label": "🌍 Дом",
        "type": "home"
    }] + questions

    links = []
    if questions:
        links.append({"source": "home", "target": questions[0]["id"], "label": "LAUNCH"})

        for i in range(len(questions) - 1):
            links.append({
                "source": questions[i]["id"],
                "target": questions[i+1]["id"],
                "label": "NEXT"
            })

    return {
        "nodes": nodes,
        "links": links
    }
