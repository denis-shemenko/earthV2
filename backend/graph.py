import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

if not all([NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD]):
    raise ValueError("NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD must be set in environment variables.")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

def save_question_path(session_id: str, prev_answer: str, new_question: str, correct_answer: str):
    with driver.session() as session:
        session.execute_write(_create_or_link, session_id, prev_answer, new_question, correct_answer)

def _create_or_link(tx, session_id, prev_answer, new_question, correct_answer):
    query = """
    MERGE (s:Session {id: $session_id})
    MERGE (prev:Answer {text: $prev_answer})
    MERGE (q:Question {text: $new_question, correct: $correct_answer})
    MERGE (s)-[:SELECTED]->(prev)
    MERGE (prev)-[:NEXT]->(q)
    MERGE (q)-[:HAS_TOPIC]->(:Topic {name: $prev_answer})
    """
    tx.run(query, session_id=session_id, prev_answer=prev_answer, new_question=new_question, correct_answer=correct_answer)
