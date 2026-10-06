from ragkit.testing import expect_equal


def test_post_devuelve_la_secuencia_y_contributions_el_orden(student):
    """Las contribuciones se numeran y se leen en orden de publicación"""
    b = student.Blackboard()
    expect_equal(b.post("a", "plazo", "14 días"), 1, what="primera secuencia")
    expect_equal(b.post("b", "coste", "9,95"), 2, what="segunda secuencia")
    b.post("c", "plazo", "7 días")
    expect_equal(
        [i["author"] for i in b.contributions("plazo")], ["a", "c"], what="autores de plazo"
    )
    expect_equal(b.count(), 3, what="total")


def test_read_devuelve_la_de_mayor_confianza(student):
    """Gana la mayor confianza; sin contribuciones, None"""
    b = student.Blackboard()
    expect_equal(b.read("plazo"), None, what="clave vacía")
    b.post("a", "plazo", "14 días", confidence=0.6)
    b.post("b", "plazo", "7 días", confidence=0.9)
    b.post("c", "plazo", "30 días", confidence=0.4)
    expect_equal(b.read("plazo"), "7 días", what="mayor confianza")


def test_read_a_igualdad_de_confianza_gana_la_mas_reciente(student):
    """Con la misma confianza (por defecto 1.0) prevalece la última publicada"""
    b = student.Blackboard()
    b.post("a", "estado", "borrador")
    b.post("b", "estado", "revisado")
    expect_equal(b.read("estado"), "revisado", what="más reciente")


def test_consenso_por_quorum_de_autores_distintos(student):
    """Cada autor cuenta una vez, con su última contribución"""
    b = student.Blackboard()
    b.post("a", "plazo", "14 días")
    b.post("b", "plazo", "14 días")
    b.post("c", "plazo", "7 días")
    expect_equal(b.has_consensus("plazo", 2), "14 días", what="quórum de 2")
    expect_equal(b.has_consensus("plazo", 3), None, what="quórum de 3")
    b.post("a", "plazo", "7 días")  # a cambia de opinión
    expect_equal(b.has_consensus("plazo", 2), "7 días", what="tras el cambio de a")


def test_un_mismo_autor_no_forma_quorum_por_si_solo(student):
    """Publicar lo mismo varias veces no es consenso"""
    b = student.Blackboard()
    for _ in range(3):
        b.post("a", "plazo", "14 días")
    expect_equal(b.has_consensus("plazo", 2), None, what="un solo autor")


def test_run_blackboard_termina_cuando_done_es_verdadero(student):
    """Los agentes colaboran hasta que done(board) se cumple"""
    b = student.Blackboard()

    def investigador(board):
        if board.read("plazo") is None:
            board.post("investigador", "plazo", "14 días")

    def revisor(board):
        if board.read("plazo") and board.read("revisado") is None:
            board.post("revisor", "revisado", True)

    out = student.run_blackboard(
        [investigador, revisor], b, done=lambda board: board.read("revisado") is True
    )
    expect_equal(out, {"rounds": 1, "stopped": "done"}, what="resultado")


def test_hidden_quiescent_si_nadie_publica_y_max_rounds(student):
    """Caso adicional: una ronda sin contribuciones detiene el bucle; si siempre hay, max_rounds"""
    out = student.run_blackboard([lambda b: None], student.Blackboard())
    expect_equal(out, {"rounds": 1, "stopped": "quiescent"}, what="quiescent")

    contador = {"n": 0}

    def charlatan(board):
        contador["n"] += 1
        board.post("c", "ruido", contador["n"])

    out = student.run_blackboard([charlatan], student.Blackboard(), max_rounds=3)
    expect_equal(out, {"rounds": 3, "stopped": "max_rounds"}, what="max_rounds")


def test_hidden_done_se_comprueba_antes_que_la_quiescencia(student):
    """Caso adicional: si done se cumple en una ronda sin novedades, el motivo es done"""
    b = student.Blackboard()
    b.post("a", "x", 1)
    out = student.run_blackboard([lambda board: None], b, done=lambda board: True)
    expect_equal(out, {"rounds": 1, "stopped": "done"}, what="prioridad de done")
