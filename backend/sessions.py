import uuid

sessions = {}

def create_session(topic: str) -> str:
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "path": [{"topic": topic}]
    }
    return session_id

def update_session(session_id: str, topic: str, answer: str):
    if session_id in sessions:
        sessions[session_id]["path"].append({
            "topic": topic,
            "chosen_answer": answer
        })

def get_session(session_id: str):
    return sessions.get(session_id)
