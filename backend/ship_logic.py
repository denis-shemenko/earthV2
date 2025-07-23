# 📁 backend/ship_logic.py
import random

RESOURCE_TYPES = ["iron", "crystal", "artifact"]

DEFAULT_SHIP_STATE = {
    "fuel": 100,
    "resources": {"iron": 0, "crystal": 0, "artifact": 0},
    "score": 0
}

def init_ship_state():
    return DEFAULT_SHIP_STATE.copy()

def apply_answer_result(ship_state, correct):
    if correct:
        # Найдено 1–3 ресурса
        found_count = random.randint(1, 3)
        found = random.choices(RESOURCE_TYPES, k=found_count)
        for res in found:
            ship_state["resources"][res] += 1
        ship_state["score"] += 100  # базовое очко за правильный ответ
        return {"event": "resources_found", "found": found}
    else:
        ship_state["fuel"] = max(0, ship_state["fuel"] - 10)
        ship_state["score"] += 10  # утешительные очки за попытку
        found = random.choices(RESOURCE_TYPES, k=1) if random.random() < 0.1 else []
        for res in found:
            ship_state["resources"][res] += 1
        return {"event": "fuel_lost", "found": found}

def ship_status(ship_state):
    return {
        "fuel": ship_state["fuel"],
        "score": ship_state["score"],
        "resources": ship_state["resources"]
    }
