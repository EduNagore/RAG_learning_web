import re

from ragkit.llm import Message


def parse_subtasks(text, max_subtasks):
    """Subtareas de una lista de texto: una por línea, sin numeración ni viñetas, sin duplicados
    (sin distinguir mayúsculas) y como máximo `max_subtasks`.
    """
    seen, subtasks = set(), []
    for line in (text or "").splitlines():
        clean = re.sub(r"^\s*(?:\d+[.)]|[-*•])\s*", "", line).strip()
        if clean and clean.lower() not in seen:
            seen.add(clean.lower())
            subtasks.append(clean)
    return subtasks[:max_subtasks]


def run_orchestrator(task, orchestrator, worker, synthesizer, max_subtasks=5):
    """Orquestador-workers: descompone, delega y sintetiza.

    1. Una llamada a `orchestrator.generate` pidiendo descomponer `task` en como mucho
       `max_subtasks` subtareas (el prompt incluye la tarea y el número).
    2. `worker(subtarea)` para cada subtarea, en orden. Si un worker lanza una excepción, su
       resultado es "error: <Tipo>: <mensaje>" y se continúa con las demás.
    3. `synthesizer(task, [(subtarea, resultado), ...])` produce la respuesta final.

    Devuelve {"subtasks": [...], "results": [...], "final": ...}. Sin subtareas no se llama
    a ningún worker y se sintetiza con una lista vacía.
    """
    prompt = (
        f"Descompón la tarea en como máximo {max_subtasks} subtareas independientes, "
        f"una por línea:\n{task}"
    )
    text = orchestrator.generate([Message("user", prompt)]).text
    subtasks = parse_subtasks(text, max_subtasks)
    results = []
    for subtask in subtasks:
        try:
            results.append(worker(subtask))
        except Exception as e:  # noqa: BLE001 - un worker caído no debe tumbar el resto
            results.append(f"error: {type(e).__name__}: {e}")
    final = synthesizer(task, list(zip(subtasks, results, strict=True)))
    return {"subtasks": subtasks, "results": results, "final": final}


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    from ragkit.llm import MockLLM

    orquestador = MockLLM(script=["1. plazo de devolución\n2. coste del envío"])
    salida = run_orchestrator(
        "Resume la política de devoluciones",
        orquestador,
        worker=lambda s: f"datos sobre {s}",
        synthesizer=lambda t, pares: " | ".join(r for _, r in pares),
    )
    print(salida)
