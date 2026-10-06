from ragkit.testing import expect_equal, expect_raises

DEVOLUCIONES = {
    "name": "agente-devoluciones",
    "description": "Resuelve dudas sobre devoluciones",
    "skills": [
        {
            "id": "plazos",
            "name": "Plazos de devolución",
            "description": "Cuánto tarda un reembolso",
            "tags": ["reembolso", "plazo"],
        }
    ],
    "capabilities": {"streaming": True},
}
ENVIOS = {
    "name": "agente-envios",
    "skills": [
        {"id": "coste", "name": "Coste del envío", "tags": ["tarifa"]},
        {
            "id": "seguimiento",
            "name": "Seguimiento del pedido",
            "description": "Estado y transportista",
        },
    ],
}


def tarjetas(student):
    return [student.parse_agent_card(DEVOLUCIONES), student.parse_agent_card(ENVIOS)]


def test_la_tarjeta_se_normaliza_con_valores_por_defecto(student):
    """parse_agent_card completa descripción, etiquetas y capacidades"""
    card = student.parse_agent_card(ENVIOS)
    expect_equal(card["description"], "", what="descripción por defecto")
    expect_equal(card["capabilities"], {"streaming": False}, what="capacidades por defecto")
    expect_equal(
        card["skills"][0],
        {"id": "coste", "name": "Coste del envío", "description": "", "tags": ["tarifa"]},
        what="skill",
    )
    expect_equal(
        student.parse_agent_card(DEVOLUCIONES)["capabilities"],
        {"streaming": True},
        what="streaming",
    )


def test_la_tarjeta_invalida_da_mensajes_claros(student):
    """Cada defecto de la tarjeta lanza ValueError con su mensaje"""
    casos = [
        ("texto", "la tarjeta debe ser un objeto"),
        ({"skills": [{"id": "a", "name": "A"}]}, "falta el campo obligatorio: name"),
        ({"name": "  ", "skills": [{"id": "a", "name": "A"}]}, "falta el campo obligatorio: name"),
        ({"name": "x", "skills": []}, "skills debe ser una lista no vacía"),
        ({"name": "x"}, "skills debe ser una lista no vacía"),
        (
            {"name": "x", "skills": [{"id": "a", "name": "A"}, {"name": "B"}]},
            "la skill 2 necesita id y name",
        ),
    ]
    for entrada, mensaje in casos:
        try:
            student.parse_agent_card(entrada)
        except ValueError as e:
            expect_equal(str(e), mensaje, what=f"mensaje para {entrada!r}")
        else:
            raise AssertionError(f"Se esperaba ValueError para {entrada!r}.")


def test_find_agent_elige_la_skill_con_mas_coincidencias(student):
    """La petición se compara con nombre, descripción y etiquetas de cada skill"""
    card, skill = student.find_agent(
        tarjetas(student), "¿Cuánto tarda el reembolso de mi devolución?"
    )
    expect_equal(
        (card["name"], skill["id"]), ("agente-devoluciones", "plazos"), what="agente elegido"
    )
    card, skill = student.find_agent(tarjetas(student), "quiero el seguimiento del pedido")
    expect_equal(
        (card["name"], skill["id"]), ("agente-envios", "seguimiento"), what="segunda skill"
    )
    card, skill = student.find_agent(tarjetas(student), "tarifa")
    expect_equal(
        (card["name"], skill["id"]),
        ("agente-envios", "coste"),
        what="coincidencia solo por etiqueta",
    )


def test_find_agent_sin_coincidencias_devuelve_none(student):
    """Sin ninguna palabra en común no hay agente"""
    expect_equal(
        student.find_agent(tarjetas(student), "¿Qué tiempo hará mañana?"), None, what="sin agente"
    )


def test_las_transiciones_validas_e_invalidas(student):
    """transition respeta el ciclo de vida de una tarea"""
    expect_equal(student.transition("submitted", "working"), "working", what="submitted -> working")
    expect_equal(
        student.transition("working", "input_required"), "input_required", what="pide datos"
    )
    expect_raises(
        ValueError, student.transition, "completed", "working", what="un estado final no cambia"
    )
    try:
        student.transition("submitted", "completed")
    except ValueError as e:
        expect_equal(str(e), "transición no permitida: submitted -> completed", what="mensaje")


def test_delegate_completa_la_tarea_con_un_artefacto(student):
    """Flujo feliz: submitted, working, completed y un artefacto con el texto"""
    ejecutores = {
        "agente-devoluciones": lambda peticion, skill: {
            "state": "completed",
            "text": "7 días hábiles",
        }
    }
    tarea = student.delegate(
        tarjetas(student), "¿Cuánto tarda el reembolso?", ejecutores, task_id="t-9"
    )
    expect_equal(tarea["id"], "t-9", what="id")
    expect_equal(tarea["state"], "completed", what="estado")
    expect_equal(tarea["history"], ["submitted", "working", "completed"], what="historial")
    expect_equal(
        (tarea["agent"], tarea["skill"]), ("agente-devoluciones", "plazos"), what="agente y skill"
    )
    expect_equal(
        tarea["artifacts"],
        [{"name": "resultado", "parts": [{"text": "7 días hábiles"}]}],
        what="artefactos",
    )


def test_hidden_sin_agente_adecuado_la_tarea_se_rechaza(student):
    """Caso adicional: rejected y sin llamar a ningún ejecutor"""
    tarea = student.delegate(tarjetas(student), "recita un poema", {})
    expect_equal(tarea["state"], "rejected", what="estado")
    expect_equal(tarea["history"], ["submitted", "rejected"], what="historial")
    expect_equal((tarea["agent"], tarea["skill"]), (None, None), what="agente y skill")


def test_hidden_input_required_fallos_y_ejecutor_ausente(student):
    """Caso adicional: input_required guarda el mensaje; los fallos guardan el error"""
    cards = tarjetas(student)
    pide = {"agente-envios": lambda p, s: {"state": "input_required", "text": "¿Número de pedido?"}}
    tarea = student.delegate(cards, "seguimiento del pedido", pide)
    expect_equal(
        (tarea["state"], tarea["message"]),
        ("input_required", "¿Número de pedido?"),
        what="input_required",
    )

    def roto(peticion, skill):
        raise TimeoutError("sin respuesta")

    tarea = student.delegate(cards, "seguimiento del pedido", {"agente-envios": roto})
    expect_equal(
        (tarea["state"], tarea["error"]),
        ("failed", "TimeoutError: sin respuesta"),
        what="excepción",
    )
    tarea = student.delegate(cards, "seguimiento del pedido", {})
    expect_equal(tarea["error"], "sin ejecutor para agente-envios", what="sin ejecutor")
    expect_equal(tarea["history"], ["submitted", "working", "failed"], what="historial del fallo")
