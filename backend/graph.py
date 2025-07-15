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

def store_first_question(session_id: str, question_text: str, answers: List[QuestionOption]):
    with driver.session() as session:
        session.execute_write(_store_first_question, session_id, question_text, answers)

def _store_first_question(tx, session_id, question_text, answers):
    tx.run("""
        MERGE (s:Session {id: $session_id})
        MERGE (q:Question {text: $question})
        MERGE (s)-[:NEXT]->(q)
        FOREACH (opt IN $answers |
            MERGE (a:Answer {text: opt.text})
            SET a.correct = opt.isCorrect
            MERGE (q)-[:HAS_OPTION]->(a)
        )
    """, session_id=session_id, question=question_text, answers=answers)

def store_selected_answer_and_next(question_text: str, selected_answer_text: str, next_question_text: str, answer_options: List[QuestionOption]):
    with driver.session() as session:
        session.execute_write(
            _store_selected_answer_and_next, 
            question_text,
            selected_answer_text, 
            next_question_text, 
            answer_options)

def _store_selected_answer_and_next(tx, question_text, selected_answer_text, next_question_text, next_answers):
    tx.run("""
        MATCH (q1:Question {text: $question_text})
        MATCH (a:Answer {text: $selected_answer})
        MERGE (q1)-[:SELECTED]->(a)

        MERGE (q2:Question {text: $next_question})
        MERGE (a)-[:NEXT]->(q2)

        FOREACH (opt IN $answers |
            MERGE (ans:Answer {text: opt.text})
            SET ans.correct = opt.isCorrect
            MERGE (q2)-[:HAS_OPTION]->(ans)
        )
    """, question_text=question_text,
         selected_answer=selected_answer_text,
         next_question=next_question_text,
         answers=next_answers)


def save_user_answer(session_id: str, answer_text: str, next_question_text: str, next_answers: List[QuestionOption]):
    with driver.session() as session:
        session.execute_write(_store_user_answer, session_id, answer_text, next_question_text, next_answers)

def _store_user_answer(tx, session_id, answer_text, next_question_text, next_answers):
    tx.run("""
        MATCH (s:Session {id: $session_id})
        MATCH (a:Answer {text: $answer_text})
        MERGE (s)-[:SELECTED]->(a)
        MERGE (q:Question {text: $next_question})
        MERGE (a)-[:NEXT]->(q)
        FOREACH (opt IN $next_options |
            MERGE (ans:Answer {text: opt.text})
            SET ans.correct = opt.isCorrect
            MERGE (q)-[:HAS_OPTION]->(ans)
        )
    """, session_id=session_id, answer_text=answer_text, next_question=next_question_text, next_options=next_answers)

# LATEST WAY. With Options!
def get_graph_with_options(session_id: str) -> dict:
    with driver.session() as session:
        return session.execute_read(_build_graph_with_options, session_id)

def _build_graph_with_options(tx, session_id: str):
    query = """
    MATCH (s:Session {id: $session_id})-[:NEXT]->(q1:Question)
    OPTIONAL MATCH path=(q1)-[:SELECTED|NEXT*0..]->(q:Question)
    WITH COLLECT(DISTINCT q) AS questions
    UNWIND questions AS q
    OPTIONAL MATCH (q)-[:HAS_OPTION]->(a:Answer)
    OPTIONAL MATCH (q)-[:SELECTED]->(sa:Answer)
    OPTIONAL MATCH (a)-[:NEXT]->(next_q:Question)
    RETURN q, a, sa, next_q
    """

    result = tx.run(query, session_id=session_id)

    nodes = {}
    links = []

    for record in result:
        q = record["q"]
        a = record["a"]
        sa = record["sa"]
        next_q = record["next_q"]

        if q and q.id not in nodes:
            nodes[q.id] = {
                "id": q.id,
                "label": q.get("text")[:50] + "...",
                "type": "question"
            }

        if a:
            if a.id not in nodes:
                nodes[a.id] = {
                    "id": a.id,
                    "label": a.get("text"),
                    "type": "answer",
                    "selected": sa and a.id == sa.id,
                    "question": q.get("text")
                }
            links.append({
                "source": q.id,
                "target": a.id,
                "label": "HAS_OPTION"
            })

        if sa:
            links.append({
                "source": q.id,
                "target": sa.id,
                "label": "SELECTED",
                "style": "bold"
            })

        if a and next_q:
            if next_q.id not in nodes:
                nodes[next_q.id] = {
                    "id": next_q.id,
                    "label": next_q.get("text")[:50] + "...",
                    "type": "question"
                }
            links.append({
                "source": a.id,
                "target": next_q.id,
                "label": "NEXT"
            })

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
