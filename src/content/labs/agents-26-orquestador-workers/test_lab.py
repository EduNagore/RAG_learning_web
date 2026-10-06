from ragkit.llm import LLMResponse, MockLLM
from ragkit.testing import expect_equal, expect_true


def sintetizar(tarea, pares):
    return f"{tarea}: " + "; ".join(f"{s}={r}" for s, r in pares)


def test_parse_subtasks_limpia_y_recorta(student):
    """Numeración, viñetas, vacías, duplicados y límite"""
    texto = "1. uno\n2) Dos\n- tres\n\n  * UNO\ncuatro"
    expect_equal(
        student.parse_subtasks(texto, 10), ["uno", "Dos", "tres", "cuatro"], what="limpias"
    )
    expect_equal(student.parse_subtasks(texto, 2), ["uno", "Dos"], what="recortadas")
    expect_equal(student.parse_subtasks(None, 3), [], what="texto None")


def test_el_orquestador_descompone_delega_y_sintetiza(student):
    """Flujo completo con una sola llamada al orquestador"""
    orq = MockLLM(script=["1. plazo\n2. coste"])
    out = student.run_orchestrator(
        "Resume la política", orq, worker=lambda s: s.upper(), synthesizer=sintetizar
    )
    expect_equal(out["subtasks"], ["plazo", "coste"], what="subtareas")
    expect_equal(out["results"], ["PLAZO", "COSTE"], what="resultados de los workers")
    expect_equal(out["final"], "Resume la política: plazo=PLAZO; coste=COSTE", what="síntesis")
    expect_equal(len(orq.calls), 1, what="llamadas al orquestador")


def test_el_prompt_incluye_la_tarea_y_el_maximo(student):
    """El orquestador recibe la tarea y cuántas subtareas como máximo"""
    orq = MockLLM(script=["a"])
    student.run_orchestrator("Compara A y B", orq, lambda s: s, sintetizar, max_subtasks=3)
    contenido = orq.calls[0]["messages"][0].content
    expect_true("Compara A y B" in contenido, "El prompt debe incluir la tarea.")
    expect_true("3" in contenido, "El prompt debe indicar el máximo de subtareas.")


def test_respeta_max_subtasks(student):
    """Aunque el modelo proponga más, solo se ejecutan max_subtasks workers"""
    vistas = []
    orq = MockLLM(script=["a\nb\nc\nd\ne"])
    student.run_orchestrator("t", orq, lambda s: vistas.append(s) or s, sintetizar, max_subtasks=2)
    expect_equal(vistas, ["a", "b"], what="workers ejecutados")


def test_un_worker_que_falla_no_tumba_a_los_demas(student):
    """La excepción se convierte en un resultado de error y se continúa"""

    def worker(s):
        if s == "malo":
            raise ValueError("sin datos")
        return "ok"

    out = student.run_orchestrator("t", MockLLM(script=["bueno\nmalo\notro"]), worker, sintetizar)
    expect_equal(out["results"], ["ok", "error: ValueError: sin datos", "ok"], what="resultados")


def test_hidden_sin_subtareas_no_se_llama_a_los_workers(student):
    """Caso adicional: respuesta vacía del orquestador"""
    llamadas = []
    out = student.run_orchestrator(
        "t",
        MockLLM(script=[LLMResponse(text="  \n")]),
        lambda s: llamadas.append(s),
        lambda tarea, pares: f"{tarea}:{len(pares)}",
    )
    expect_equal(llamadas, [], what="workers")
    expect_equal(out, {"subtasks": [], "results": [], "final": "t:0"}, what="resultado")


def test_hidden_el_sintetizador_recibe_los_pares_en_orden(student):
    """Caso adicional: pares (subtarea, resultado) en orden de ejecución"""
    recibido = []
    student.run_orchestrator(
        "t",
        MockLLM(script=["x\ny"]),
        lambda s: s * 2,
        lambda tarea, pares: recibido.append((tarea, pares)),
    )
    expect_equal(recibido, [("t", [("x", "xx"), ("y", "yy")])], what="argumentos del sintetizador")
