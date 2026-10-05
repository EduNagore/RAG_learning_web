from ragkit.llm import MockLLM
from ragkit.testing import expect_equal, expect_true

PLAZO = "Los particulares tienen 14 días naturales."


def buscar(consulta):
    return PLAZO


def test_responde_directamente_si_no_hay_herramientas(student):
    """Si el modelo no pide herramientas, su texto es la respuesta final"""
    llm = MockLLM(script=["Hola, ¿en qué puedo ayudarte?"])
    result = student.run_agent(llm, {"buscar": buscar}, "Hola")
    expect_equal(result.answer, "Hola, ¿en qué puedo ayudarte?", what="respuesta")
    expect_equal(result.steps, 1, what="pasos")
    expect_equal(result.stopped, "final", what="motivo de parada")


def test_llama_a_la_herramienta_y_responde(student):
    """Ejecuta la herramienta pedida y vuelve a llamar al modelo con el resultado"""
    llm = MockLLM(script=[{"tool": "buscar", "args": {"consulta": "plazo"}}, "Tienes 14 días."])
    result = student.run_agent(llm, {"buscar": buscar}, "¿Plazo de devolución?")
    expect_equal(result.answer, "Tienes 14 días.", what="respuesta final")
    expect_equal(result.steps, 2, what="llamadas al modelo")
    expect_equal(result.stopped, "final", what="motivo de parada")


def test_el_modelo_recibe_el_resultado_de_la_herramienta(student):
    """En la segunda llamada, la conversación incluye el mensaje «tool» con su resultado"""
    llm = MockLLM(script=[{"tool": "buscar", "args": {"consulta": "plazo"}}, "ok"])
    student.run_agent(llm, {"buscar": buscar}, "¿Plazo?")
    messages = llm.calls[1]["messages"]
    tool_messages = [m for m in messages if m.role == "tool"]
    expect_equal(len(tool_messages), 1, what="mensajes de herramienta en la segunda llamada")
    expect_equal(tool_messages[0].content, PLAZO, what="contenido del resultado")
    call_id = llm.calls[1]["messages"][1].tool_calls[0].id
    expect_equal(tool_messages[0].tool_call_id, call_id, what="tool_call_id del resultado")


def test_el_mensaje_del_asistente_va_antes_de_los_resultados(student):
    """El orden de roles es user, assistant, tool"""
    llm = MockLLM(script=[{"tool": "buscar", "args": {"consulta": "x"}}, "ok"])
    student.run_agent(llm, {"buscar": buscar}, "pregunta")
    roles = [m.role for m in llm.calls[1]["messages"]]
    expect_equal(roles, ["user", "assistant", "tool"], what="orden de los mensajes")


def test_herramienta_inexistente_no_rompe_el_agente(student):
    """Una herramienta que no existe produce un resultado «error:» y el bucle sigue"""
    llm = MockLLM(script=[{"tool": "no_existe", "args": {}}, "Perdón, lo intento de otra forma."])
    result = student.run_agent(llm, {"buscar": buscar}, "pregunta")
    expect_equal(result.stopped, "final", what="motivo de parada")
    tool_message = next(m for m in llm.calls[1]["messages"] if m.role == "tool")
    expect_true(
        tool_message.content.startswith("error:"),
        f"El resultado debería empezar por «error:» y es {tool_message.content!r}.",
    )


def test_excepcion_en_herramienta_se_devuelve_como_error(student):
    """Si la herramienta lanza una excepción, se convierte en un resultado «error:»"""

    def rota(consulta):
        raise ValueError("base de datos no disponible")

    llm = MockLLM(script=[{"tool": "rota", "args": {"consulta": "x"}}, "No he podido consultarlo."])
    result = student.run_agent(llm, {"rota": rota}, "pregunta")
    expect_equal(result.answer, "No he podido consultarlo.", what="respuesta tras el error")
    tool_message = next(m for m in llm.calls[1]["messages"] if m.role == "tool")
    expect_true(
        tool_message.content.startswith("error:"), "El resultado debería empezar por «error:»."
    )
    expect_true(
        "base de datos" in tool_message.content,
        "El resultado debe incluir el mensaje de la excepción.",
    )


def test_limite_de_pasos(student):
    """Si el modelo nunca termina, el agente se detiene en max_steps sin respuesta"""
    llm = MockLLM(default={"tool": "buscar", "args": {"consulta": "otra vez"}})
    result = student.run_agent(llm, {"buscar": buscar}, "pregunta", max_steps=3)
    expect_equal(result.answer, None, what="respuesta")
    expect_equal(result.stopped, "max_steps", what="motivo de parada")
    expect_equal(result.steps, 3, what="pasos")
    expect_equal(len(llm.calls), 3, what="llamadas reales al modelo")


def test_hidden_llamadas_en_paralelo_conservan_el_orden(student):
    """Caso adicional: varias herramientas en el mismo turno"""
    llm = MockLLM(
        script=[
            [
                {"tool": "buscar", "args": {"consulta": "a"}},
                {"tool": "buscar", "args": {"consulta": "b"}},
            ],
            "listo",
        ]
    )
    calls = []

    def registra(consulta):
        calls.append(consulta)
        return f"resultado {consulta}"

    result = student.run_agent(llm, {"buscar": registra}, "pregunta")
    expect_equal(calls, ["a", "b"], what="orden de ejecución")
    messages = llm.calls[1]["messages"]
    expect_equal(
        [m.role for m in messages], ["user", "assistant", "tool", "tool"], what="orden de roles"
    )
    expect_equal(
        [m.content for m in messages if m.role == "tool"],
        ["resultado a", "resultado b"],
        what="resultados",
    )
    expect_equal(result.steps, 2, what="pasos")


def test_hidden_la_traza_registra_cada_herramienta(student):
    """Caso adicional: traza"""
    llm = MockLLM(script=[{"tool": "buscar", "args": {"consulta": "plazo"}}, "ok"])
    result = student.run_agent(llm, {"buscar": buscar}, "pregunta")
    expect_equal(
        result.trace,
        [{"tool": "buscar", "arguments": {"consulta": "plazo"}, "result": PLAZO}],
        what="traza",
    )


def test_hidden_el_resultado_siempre_es_texto(student):
    """Caso adicional: resultados no textuales"""
    llm = MockLLM(script=[{"tool": "contar", "args": {}}, "ok"])
    student.run_agent(llm, {"contar": lambda: 42}, "pregunta")
    tool_message = next(m for m in llm.calls[1]["messages"] if m.role == "tool")
    expect_equal(tool_message.content, "42", what="resultado convertido a texto")
