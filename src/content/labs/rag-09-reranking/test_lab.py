from ragkit.testing import expect_close, expect_equal, expect_true

GANANCIAS = [3, 2, 3, 0, 1, 2]


def test_dcg_descuenta_las_posiciones_bajas(student):
    """dcg_at_k suma ganancia / log2(posición + 1)"""
    expect_close(student.dcg_at_k(GANANCIAS, 6), 6.86113, tol=1e-4, what="DCG@6")
    expect_close(student.dcg_at_k(GANANCIAS, 3), 5.76186, tol=1e-4, what="DCG@3")


def test_dcg_con_menos_elementos_que_k(student):
    """Si hay menos ganancias que k se usan todas"""
    expect_close(student.dcg_at_k([1], 5), 1.0, what="DCG con una sola ganancia")
    expect_equal(student.dcg_at_k([], 5), 0, what="DCG de lista vacía")


def test_ndcg_de_un_ranking_imperfecto(student):
    """nDCG compara con el mejor orden posible"""
    rel = {"a": 3, "b": 2, "c": 1}
    expect_close(student.ndcg_at_k(["c", "a", "b"], rel, k=3), 0.8175, tol=1e-3, what="nDCG@3")


def test_ndcg_del_ranking_ideal_es_uno(student):
    """Un ranking ordenado por relevancia da nDCG = 1"""
    rel = {"a": 3, "b": 2, "c": 1}
    expect_close(student.ndcg_at_k(["a", "b", "c"], rel, k=3), 1.0, what="nDCG del orden ideal")


def test_ndcg_los_no_valorados_valen_cero(student):
    """Un documento ausente de relevance aporta ganancia 0 y el IDCG usa todos los relevantes"""
    rel = {"a": 3, "b": 2}
    valor = student.ndcg_at_k(["z", "a"], rel, k=2)
    expect_close(valor, (3 / 1.58496) / (3 + 2 / 1.58496), tol=1e-3, what="nDCG con un intruso")


def test_ndcg_el_ideal_tambien_se_corta_en_k(student):
    """El DCG ideal usa solo las k mejores ganancias"""
    rel = {"a": 1, "b": 1, "c": 1}
    expect_close(student.ndcg_at_k(["a"], rel, k=1), 1.0, what="nDCG@1")


def test_rerank_ordena_por_puntuacion_y_respeta_top_k(student):
    """rerank devuelve ids de mayor a menor puntuación"""
    docs = [{"id": "x", "text": "aa"}, {"id": "y", "text": "aaaa"}, {"id": "z", "text": "a"}]
    largo = lambda q, texto: len(texto)
    expect_equal(student.rerank("q", docs, largo), ["y", "x", "z"], what="orden")
    expect_equal(student.rerank("q", docs, largo, top_k=2), ["y", "x"], what="con top_k=2")


def test_rerank_conserva_el_orden_original_en_empates(student):
    """Los empates no se reordenan"""
    docs = [{"id": "p", "text": "a"}, {"id": "q", "text": "b"}, {"id": "r", "text": "c"}]
    expect_equal(student.rerank("q", docs, lambda q, t: 1), ["p", "q", "r"], what="empate total")


def test_two_stage_search_reordena_los_candidatos(student):
    """La segunda etapa cambia el orden de la primera"""
    docs = {
        "d1": {"id": "d1", "text": "poco"},
        "d2": {"id": "d2", "text": "devolucion reembolso plazo"},
        "d3": {"id": "d3", "text": "devolucion"},
    }
    primera = lambda q: ["d1", "d3", "d2"]
    cuenta = lambda q, t: sum(p in t for p in q.split())
    out = student.two_stage_search("devolucion reembolso", primera, docs, cuenta, top_k=2)
    expect_equal(out, ["d2", "d3"], what="top 2 tras reordenar")


def test_hidden_el_reranker_no_ve_mas_alla_de_n_candidates(student):
    """Caso adicional: el reranker solo considera los n_candidates primeros"""
    docs = {f"d{i}": {"id": f"d{i}", "text": "x" * i} for i in range(10)}
    primera = lambda q: [f"d{i}" for i in range(10)]
    out = student.two_stage_search(
        "q", primera, docs, lambda q, t: len(t), n_candidates=4, top_k=10
    )
    expect_equal(out, ["d3", "d2", "d1", "d0"], what="candidatos considerados")


def test_hidden_ignora_ids_desconocidos_y_ndcg_sin_relevantes(student):
    """Caso adicional: ids ausentes del corpus y consultas sin documentos relevantes"""
    docs = {"a": {"id": "a", "text": "uno"}}
    out = student.two_stage_search("q", lambda q: ["fantasma", "a"], docs, lambda q, t: 1)
    expect_equal(out, ["a"], what="ids desconocidos")
    expect_true(student.ndcg_at_k(["a"], {}, k=3) == 0.0, "Sin relevantes el nDCG es 0.0.")
