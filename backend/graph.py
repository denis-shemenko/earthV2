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

def start_session_with_topics(session_id: str, topics: List[str]):
    with driver.session() as session:
        session.execute_write(_start_session_with_topics, session_id, topics)

def _start_session_with_topics(tx, session_id: str, topics: List[str]):
    for i, name in enumerate(topics):
        answer_id = f"{session_id}_topic_{i}"
        tx.run("""
            MERGE (s:Session {id: $session_id})
            MERGE (a:Answer {text: $name, id: $answer_id})
            SET a.topic = true
            MERGE (s)-[:HAS_OPTION]->(a)
        """, session_id=session_id, name=name, answer_id=answer_id)

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

# LATEST WAY. With Options!
def get_graph_with_options(session_id: str) -> dict:
    with driver.session() as session:
        return session.execute_read(_build_graph_with_options, session_id)

def _build_graph_with_options(tx, session_id: str):
    # First query: Get session and topic nodes
    topic_query = """
    MATCH (s:Session {id: $session_id})
    OPTIONAL MATCH (s)-[:HAS_OPTION]->(topic_answer:Answer)
    WHERE topic_answer.topic = true
    RETURN s, topic_answer
    """
    
    # Second query: Get questions and their answers (only if they exist)
    question_query = """
    MATCH (s:Session {id: $session_id})
    OPTIONAL MATCH (s)-[:NEXT]->(q1:Question)
    OPTIONAL MATCH path=(q1)-[:SELECTED|NEXT*0..]->(q:Question)
    WITH COLLECT(DISTINCT q) AS questions
    UNWIND questions AS q
    OPTIONAL MATCH (q)-[:HAS_OPTION]->(a:Answer)
    OPTIONAL MATCH (q)-[:SELECTED]->(sa:Answer)
    OPTIONAL MATCH (a)-[:NEXT]->(next_q:Question)
    RETURN q, a, sa, next_q
    """
    
    print(f"DEBUG: Query executed for session_id: {session_id}")
    
    # Execute topic query
    topic_result = tx.run(topic_query, session_id=session_id)
    print(f"DEBUG: Topic query returned {len(list(topic_result))} records")
    topic_result = tx.run(topic_query, session_id=session_id)  # Reset iterator
    
    # Execute question query
    question_result = tx.run(question_query, session_id=session_id)
    print(f"DEBUG: Question query returned {len(list(question_result))} records")
    question_result = tx.run(question_query, session_id=session_id)  # Reset iterator

    nodes = {}
    links = []

    # Process topic results
    for record in topic_result:
        s = record["s"]
        topic_answer = record["topic_answer"]

        print(f"DEBUG: Processing topic record - s: {s}, topic_answer: {topic_answer}")

        # Add session node (home node)
        if s and s.id not in nodes:
            print(f"DEBUG: Adding session node: {s.id}")
            nodes[s.id] = {
                "id": s.id,
                "label": "ЗЕМЛЯ",
                "type": "home",
                "question": "",
                "selected": False
            }

        # Add topic answer nodes
        if topic_answer and topic_answer.id not in nodes:
            print(f"DEBUG: Adding topic answer node: {topic_answer.id} with text: {topic_answer.get('text')}")
            nodes[topic_answer.id] = {
                "id": topic_answer.id,
                "label": topic_answer.get("text"),
                "type": "answer",
                "selected": False,
                "question": "Выбор темы",
                "topic": True  # Add topic property
            }
            links.append({
                "source": s.id,
                "target": topic_answer.id,
                "label": "HAS_OPTION"
            })

    # Process question results
    for record in question_result:
        q = record["q"]
        a = record["a"]
        sa = record["sa"]
        next_q = record["next_q"]

        print(f"DEBUG: Processing question record - q: {q}, a: {a}")

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
