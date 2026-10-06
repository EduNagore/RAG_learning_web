from ragkit.testing import expect_equal


def guion(*nombres):
    """Supervisor que devuelve los nombres en orden y luego FINISH."""
    it = iter(nombres)
    return lambda state: next(it, "FINISH")


def test_el_supervisor_reparte_y_termina(student):
    """Dos agentes en orden y FINISH; el estado compartido acumula historial y datos"""
    agentes = {
        "buscador": lambda s: {"message": "buscado", "data": {"hecho": "14 días"}},
        "redactor": lambda s: {"message": f"redacto con {s['data']['hecho']}"},
    }
    out = student.run_supervisor("t", guion("buscador", "redactor"), agentes)
    expect_equal(out["stopped"], "finish", what="motivo")
    expect_equal(out["trace"], ["buscador", "redactor"], what="agentes ejecutados")
    expect_equal(out["turns"], 2, what="turnos")
    expect_equal(out["state"]["data"], {"hecho": "14 días"}, what="datos")
    expect_equal(
        out["state"]["history"],
        [
            {"agent": "buscador", "message": "buscado"},
            {"agent": "redactor", "message": "redacto con 14 días"},
        ],
        what="historial",
    )
    expect_equal(out["state"]["task"], "t", what="tarea")


def test_el_supervisor_ve_el_estado_actualizado(student):
    """Cada decisión del supervisor se toma con el estado tras el turno anterior"""
    vistos = []

    def supervisor(state):
        vistos.append(len(state["history"]))
        return "a" if len(state["history"]) < 2 else "FINISH"

    student.run_supervisor("t", supervisor, {"a": lambda s: {"message": "x"}})
    expect_equal(vistos, [0, 1, 2], what="longitud del historial en cada decisión")


def test_un_handoff_pasa_el_control_sin_consultar_al_supervisor(student):
    """El agente que devuelve handoff cede el turno siguiente a otro agente"""
    consultas = []

    def supervisor(state):
        consultas.append(1)
        return "triaje" if len(consultas) == 1 else "FINISH"

    agentes = {
        "triaje": lambda s: {"message": "es de facturas", "handoff": "facturas"},
        "facturas": lambda s: {"message": "resuelto", "data": {"resuelto": True}},
    }
    out = student.run_supervisor("t", supervisor, agentes)
    expect_equal(out["trace"], ["triaje", "facturas"], what="agentes ejecutados")
    expect_equal(len(consultas), 2, what="consultas al supervisor (la del handoff no cuenta)")
    expect_equal(out["state"]["data"], {"resuelto": True}, what="datos")


def test_un_nombre_desconocido_detiene_el_bucle(student):
    """invalid_agent si el supervisor (o un handoff) elige un agente inexistente"""
    out = student.run_supervisor("t", lambda s: "fantasma", {"a": lambda s: {}})
    expect_equal((out["stopped"], out["turns"]), ("invalid_agent", 0), what="supervisor")
    agentes = {"a": lambda s: {"handoff": "zzz"}}
    out = student.run_supervisor("t", guion("a"), agentes)
    expect_equal((out["stopped"], out["trace"]), ("invalid_agent", ["a"]), what="handoff")


def test_agotar_los_turnos(student):
    """max_turns cuando el supervisor alterna sin terminar"""
    alternar = iter(["a", "b"] * 10)
    out = student.run_supervisor(
        "t",
        lambda s: next(alternar),
        {"a": lambda s: {"message": "a"}, "b": lambda s: {"message": "b"}},
        max_turns=4,
    )
    expect_equal(out["stopped"], "max_turns", what="motivo")
    expect_equal(out["trace"], ["a", "b", "a", "b"], what="agentes")


def test_hidden_deteccion_de_bucle_con_el_mismo_agente(student):
    """Caso adicional: el mismo agente elegido 3 veces seguidas detiene el bucle antes de ejecutarlo"""
    out = student.run_supervisor("t", lambda s: "a", {"a": lambda s: {"message": "otra vez"}})
    expect_equal(out["stopped"], "stuck", what="motivo")
    expect_equal(out["trace"], ["a", "a"], what="se ejecutó dos veces")
    mas_margen = student.run_supervisor(
        "t", lambda s: "a", {"a": lambda s: None}, max_turns=10, max_repeats=5
    )
    expect_equal(len(mas_margen["trace"]), 4, what="con max_repeats=5 se ejecuta 4 veces")


def test_hidden_un_agente_que_falla_queda_en_el_historial(student):
    """Caso adicional: la excepción se registra y el bucle continúa; None cuenta como {}"""

    def roto(state):
        raise ValueError("sin datos")

    agentes = {"roto": roto, "mudo": lambda s: None}
    out = student.run_supervisor("t", guion("roto", "mudo"), agentes)
    expect_equal(out["stopped"], "finish", what="motivo")
    expect_equal(
        out["state"]["history"],
        [
            {"agent": "roto", "message": "error: ValueError: sin datos"},
            {"agent": "mudo", "message": ""},
        ],
        what="historial",
    )
