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
    """Valida y normaliza una Agent Card simplificada.

    Entrada: {"name", "description"?, "skills": [{"id", "name", "description"?, "tags"?}],
              "capabilities"?: {"streaming"?}}.
    Devuelve {"name", "description" (por defecto ""), "skills": [{"id", "name", "description"
    (por defecto ""), "tags" (por defecto [])}], "capabilities": {"streaming": bool (por defecto False)}}.

    Lanza ValueError con estos mensajes exactos:
      - "la tarjeta debe ser un objeto"
      - "falta el campo obligatorio: name"   (también si es texto vacío o solo espacios)
      - "skills debe ser una lista no vacía"
      - "la skill <i> necesita id y name"     (i empieza en 1)
    """
    # TODO
    raise NotImplementedError("Completa parse_agent_card")


def find_agent(cards, request):
    """Devuelve (tarjeta, skill) con más coincidencias, o None si ninguna coincide.

    Palabras = minúsculas, con re.findall(r"\\w+"), y solo las de 3 o más letras. Para cada
    skill, la puntuación es cuántas palabras DISTINTAS de la petición aparecen entre las de su
    nombre, descripción y etiquetas. Gana la puntuación más alta; ante un empate, la primera
    tarjeta y la primera skill. Con puntuación 0 en todas, devuelve None.
    """
    # TODO
    raise NotImplementedError("Completa find_agent")


def transition(state, new_state):
    """Devuelve new_state si TRANSITIONS lo permite desde state; si no, lanza
    ValueError(f"transición no permitida: {state} -> {new_state}").
    """
    # TODO
    raise NotImplementedError("Completa transition")


def delegate(cards, request, executors, task_id="task-1"):
    """Delega una petición y devuelve la tarea como diccionario.

    La tarea es {"id", "state", "agent", "skill", "history", "artifacts", "message", "error"};
    empieza en "submitted" (history = ["submitted"]) y cada cambio de estado pasa por
    `transition` y se añade a history.
      - Sin agente adecuado: estado "rejected" (agent y skill None).
      - Con agente: agent = nombre de la tarjeta, skill = id de la skill, estado "working" y se
        llama a executors[nombre](request, skill) -> {"state": "completed" | "input_required" |
        "failed", "text": ...}.
      - completed: artifacts = [{"name": "resultado", "parts": [{"text": text}]}].
      - input_required: message = text.   - failed: error = text.
      - Si no hay ejecutor para el agente: failed con error "sin ejecutor para <nombre>".
      - Si el ejecutor lanza una excepción: failed con error "<Tipo>: <mensaje>".
    """
    # TODO
    raise NotImplementedError("Completa delegate")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    try:
        tarjeta = parse_agent_card(
            {
                "name": "agente-devoluciones",
                "skills": [{"id": "plazos", "name": "Plazos de devolución", "tags": ["reembolso"]}],
            }
        )
        print(find_agent([tarjeta], "¿Cuánto tarda el reembolso de una devolución?")[1]["id"])
    except NotImplementedError as e:
        print("Aún por completar:", e)
