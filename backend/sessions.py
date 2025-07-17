import uuid

sessions = {}

def create_session() -> str:
    session_id = str(uuid.uuid4())
    return session_id
