from ragkit.testing import expect_close, expect_equal, expect_raises, expect_true


def test_fusiona_dos_rankings_con_sus_puntuaciones(student):
    """rrf_fuse suma 1/(k+posición) y ordena de mayor a menor"""
    out = student.rrf_fuse([["a", "b", "c"], ["c", "a", "d"]])
    expect_equal([d for d, _ in out], ["a", "c", "b", "d"], what="orden de la fusión")
    expect_close(out[0][1], 1 / 61 + 1 / 62, what="puntuación de «a»")
    expect_close(out[1][1], 1 / 63 + 1 / 61, what="puntuación de «c»")
    expect_close(out[2][1], 1 / 62, what="puntuación de «b» (solo en un ranking)")


def test_la_constante_k_cambia_el_ganador(student):
    """Con k=0 gana el primero de una lista; con k=60 gana el consenso"""
    rankings = [["A", "B", "D"], ["C", "E", "B"]]
    expect_equal(student.rrf_fuse(rankings, k=0)[0][0], "A", what="ganador con k=0")
    expect_equal(student.rrf_fuse(rankings, k=60)[0][0], "B", what="ganador con k=60")


def test_los_pesos_inclinan_la_balanza(student):
    """Un ranking con más peso aporta más a la puntuación"""
    out = student.rrf_fuse([["a"], ["b"]], weights=[1, 3])
    expect_equal(out[0][0], "b", what="documento con más peso")
    expect_close(out[0][1], 3 / 61, what="puntuación de «b»")


def test_los_empates_se_resuelven_por_primera_aparicion(student):
    """Ante un empate de puntuación gana el que apareció antes"""
    out = student.rrf_fuse([["x", "y"], ["y", "x"]])
    expect_equal([d for d, _ in out], ["x", "y"], what="orden con empate")


def test_sin_rankings_devuelve_lista_vacia(student):
    """Sin rankings (o vacíos) el resultado es una lista vacía"""
    expect_equal(student.rrf_fuse([]), [], what="sin rankings")
    expect_equal(student.rrf_fuse([[], []]), [], what="rankings vacíos")


def test_hybrid_search_devuelve_solo_ids_y_respeta_top_k(student):
    """hybrid_search devuelve los ids de los top_k mejores fusionados"""
    lexico = lambda q: ["d1", "d2", "d3", "d4"]
    denso = lambda q: ["d3", "d1", "d5", "d2"]
    out = student.hybrid_search("consulta", [lexico, denso], top_k=2)
    expect_equal(out, ["d1", "d3"], what="top 2 fusionado")


def test_hybrid_search_propaga_la_constante_k(student):
    """hybrid_search pasa k a la fusión"""
    r1, r2 = (lambda q: ["A", "B", "D"]), (lambda q: ["C", "E", "B"])
    expect_equal(student.hybrid_search("q", [r1, r2], top_k=1, k=60), ["B"], what="con k=60")
    expect_equal(student.hybrid_search("q", [r1, r2], top_k=1, k=0), ["A"], what="con k=0")


def test_hidden_los_ids_repetidos_en_un_ranking_cuentan_una_vez(student):
    """Caso adicional: un id duplicado en el mismo ranking no suma dos veces"""
    out = student.rrf_fuse([["a", "a", "b"]])
    expect_close(out[0][1], 1 / 61, what="puntuación de «a» repetido")
    expect_equal(out[0][0], "a", what="primero")
    expect_close(dict(out)["b"], 1 / 63, what="«b» conserva su posición real (3)")


def test_hidden_valida_los_argumentos(student):
    """Caso adicional: k negativo y número de pesos incorrecto lanzan ValueError"""
    expect_raises(ValueError, student.rrf_fuse, [["a"]], k=-1, what="k negativo")
    expect_raises(ValueError, student.rrf_fuse, [["a"], ["b"]], weights=[1], what="pesos de menos")


def test_hidden_candidates_recorta_cada_lista_antes_de_fusionar(student):
    """Caso adicional: lo que queda más allá de `candidates` no participa"""
    largo = [f"x{i}" for i in range(30)] + ["objetivo"]
    out = student.hybrid_search("q", [lambda q: largo, lambda q: largo], top_k=40, candidates=5)
    expect_true("objetivo" not in out, "Un documento fuera de los candidatos no debe aparecer.")
    expect_equal(len(out), 5, what="número de resultados")
