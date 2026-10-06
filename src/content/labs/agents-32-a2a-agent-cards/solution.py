import re

TRANSITIONS = {
    "submitted": {"working", "rejected", "canceled"},
    "working": {"completed", "failed", "input_required", "canceled"},
    "input_required": {"working", "canceled"},
    "completed": set(),
    "failed": set(),
    "canceled": set(),
    "rejected": set(),
}


def parse_agent_card(data):
    """Valida y normaliza una Agent Card simplificada. Lanza ValueError con estos mensajes:

    - "la tarjeta debe ser un objeto"
    - "falta el campo obligatorio: name" (también si es texto vacío)
    - "skills debe ser una lista no vacía"
    - "la skill <i> necesita id y name" (i empieza en 1)
    """
    if not isinstance(data, dict):
        raise ValueError("la tarjeta debe ser un objeto")  # noqa: TRY004 - el enunciado pide ValueError
    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("falta el campo obligatorio: name")
    skills = data.get("skills")
    if not isinstance(skills, list) or not skills:
        raise ValueError("skills debe ser una lista no vacía")
    normalized = []
    for i, skill in enumerate(skills, start=1):
        if not isinstance(skill, dict) or not skill.get("id") or not skill.get("name"):
            raise ValueError(f"la skill {i} necesita id y name")
        normalized.append(
            {
                "id": skill["id"],
                "name": skill["name"],
                "description": skill.get("description", ""),
                "tags": list(skill.get("tags", [])),
            }
        )
    capabilities = data.get("capabilities") or {}
    return {
        "name": name,
        "description": data.get("description", ""),
        "skills": normalized,
        "capabilities": {"streaming": bool(capabilities.get("streaming", False))},
    }


def _words(text):
    return {w for w in re.findall(r"\w+", text.lower()) if len(w) >= 3}


def _skill_words(skill):
    return _words(" ".join([skill["name"], skill["description"], *skill["tags"]]))


def find_agent(cards, request):
    """(tarjeta, skill) con más palabras de la petición (de 3 o más letras) en el nombre, la
    descripción y las etiquetas. Empates: la primera tarjeta y la primera skill. None si ninguna
    coincide.
    """
    wanted = _words(request)
    best, best_score = None, 0
    for card in cards:
        for skill in card["skills"]:
            score = len(wanted & _skill_words(skill))
            if score > best_score:
                best, best_score = (card, skill), score
    return best


def transition(state, new_state):
    """Devuelve new_state si la transición está permitida; si no, lanza ValueError."""
    if new_state not in TRANSITIONS.get(state, set()):
        raise ValueError(f"transición no permitida: {state} -> {new_state}")
    return new_state


def delegate(cards, request, executors, task_id="task-1"):
    """Delega una petición al agente con la skill adecuada y devuelve la tarea resultante."""
    task = {
        "id": task_id,
        "state": "submitted",
        "agent": None,
        "skill": None,
        "history": ["submitted"],
        "artifacts": [],
        "message": None,
        "error": None,
    }

    def move(new_state):
        task["state"] = transition(task["state"], new_state)
        task["history"].append(new_state)

    match = find_agent(cards, request)
    if match is None:
        move("rejected")
        return task
    card, skill = match
    task["agent"], task["skill"] = card["name"], skill["id"]
    move("working")
    executor = executors.get(card["name"])
    if executor is None:
        task["error"] = f"sin ejecutor para {card['name']}"
        move("failed")
        return task
    try:
        outcome = executor(request, skill)
    except Exception as e:  # noqa: BLE001 - un agente remoto puede fallar
        task["error"] = f"{type(e).__name__}: {e}"
        move("failed")
        return task
    move(outcome["state"])
    if outcome["state"] == "completed":
        task["artifacts"].append({"name": "resultado", "parts": [{"text": outcome["text"]}]})
    elif outcome["state"] == "input_required":
        task["message"] = outcome["text"]
    else:
        task["error"] = outcome["text"]
    return task


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    tarjeta = parse_agent_card(
        {
            "name": "agente-devoluciones",
            "skills": [{"id": "plazos", "name": "Plazos de devolución", "tags": ["reembolso"]}],
        }
    )
    print(find_agent([tarjeta], "¿Cuánto tarda el reembolso de una devolución?")[1]["id"])
