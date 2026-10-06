import re

from ragkit.llm import Message


def parse_subtasks(text, max_subtasks):
    """Subtareas de un texto: una por línea.

    Quita prefijos como "1.", "2)", "-", "*", "•"; ignora líneas vacías; descarta duplicados
    (sin distinguir mayúsculas, conservando la primera) y devuelve como máximo `max_subtasks`.
    `text` puede ser None.
    """
    # TODO
    raise NotImplementedError("Completa parse_subtasks")


def run_orchestrator(task, orchestrator, worker, synthesizer, max_subtasks=5):
    """Orquestador-workers: descompone, delega y sintetiza.

    1. UNA llamada a `orchestrator.generate([Message("user", prompt)])` pidiendo descomponer
       `task` en como mucho `max_subtasks` subtareas (el prompt debe contener la tarea y el
       número). El texto de la respuesta es `.text`.
    2. `worker(subtarea)` para cada subtarea, en orden. Si un worker lanza una excepción, su
       resultado es "error: <Tipo>: <mensaje>" y se continúa con las demás.
    3. `synthesizer(task, [(subtarea, resultado), ...])` produce la respuesta final.

    Devuelve {"subtasks": [...], "results": [...], "final": ...}. Sin subtareas no se llama a
    ningún worker y se sintetiza con una lista vacía.
    """
    # TODO
    raise NotImplementedError("Completa run_orchestrator")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    from ragkit.llm import MockLLM

    orquestador = MockLLM(script=["1. plazo de devolución\n2. coste del envío"])
    try:
        salida = run_orchestrator(
            "Resume la política de devoluciones",
            orquestador,
            worker=lambda s: f"datos sobre {s}",
            synthesizer=lambda t, pares: " | ".join(r for _, r in pares),
        )
        print(salida)
    except NotImplementedError as e:
        print("Aún por completar:", e)
