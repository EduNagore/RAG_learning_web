from ragkit.testing import expect_close, expect_equal

RANKING = ["d3", "d1", "d9", "d2"]
RELEVANTES = {"d1", "d2"}


def test_hit_rate_depende_de_k(student):
    """hit_at_k mira solo los k primeros"""
    expect_equal(student.hit_at_k(RANKING, RELEVANTES, 1), 0.0, what="hit@1")
    expect_equal(student.hit_at_k(RANKING, RELEVANTES, 2), 1.0, what="hit@2")


def test_recall_es_la_fraccion_de_relevantes_recuperados(student):
    """recall_at_k divide entre el número de relevantes"""
    expect_close(student.recall_at_k(RANKING, RELEVANTES, 2), 0.5, what="recall@2")
    expect_close(student.recall_at_k(RANKING, RELEVANTES, 4), 1.0, what="recall@4")
    expect_equal(student.recall_at_k(RANKING, set(), 3), None, what="sin relevantes")


def test_precision_divide_siempre_entre_k(student):
    """precision_at_k penaliza los resultados que faltan"""
    expect_close(student.precision_at_k(RANKING, RELEVANTES, 2), 0.5, what="precision@2")
    expect_close(student.precision_at_k(["a"], {"a"}, 3), 1 / 3, what="menos resultados que k")


def test_rango_reciproco(student):
    """reciprocal_rank usa la posición del primer relevante"""
    expect_close(student.reciprocal_rank(RANKING, RELEVANTES), 0.5, what="MRR de la pregunta")
    expect_equal(student.reciprocal_rank(RANKING, {"zzz"}), 0.0, what="sin relevantes")
    expect_equal(student.reciprocal_rank(RANKING, {"d2"}, k=3), 0.0, what="fuera de los k primeros")


def test_ndcg_binario(student):
    """nDCG compara el DCG con el mejor orden posible"""
    expect_close(student.ndcg_at_k(RANKING, RELEVANTES, 4), 0.65092, tol=1e-4, what="nDCG@4")
    expect_close(student.ndcg_at_k(RANKING, RELEVANTES, 2), 0.38685, tol=1e-4, what="nDCG@2")
    expect_close(student.ndcg_at_k(["d1", "d2"], RELEVANTES, 2), 1.0, what="orden ideal")
    expect_equal(student.ndcg_at_k(RANKING, set(), 3), 0.0, what="sin relevantes")
    expect_close(
        student.ndcg_at_k(["a"], {"a", "b", "c"}, 1), 1.0, what="más relevantes que k posiciones"
    )


def test_evaluate_promedia_las_metricas(student):
    """evaluate devuelve las medias y cuenta solo preguntas con relevantes"""
    golden = [
        {"id": "q1", "relevant_ids": ["d1", "d2"]},
        {"id": "q2", "relevant_ids": ["x"]},
        {"id": "q3", "relevant_ids": []},
    ]
    run = {"q1": RANKING, "q2": ["x", "y"]}
    out = student.evaluate(run, golden, k=2)
    expect_equal(out["n"], 2, what="preguntas evaluadas")
    expect_close(out["hit"], 1.0, what="hit")
    expect_close(out["recall"], 0.75, what="recall")
    expect_close(out["precision"], 0.5, what="precision")
    expect_close(out["mrr"], 0.75, what="MRR")
    expect_close(out["ndcg"], 0.69343, tol=1e-4, what="nDCG")


def test_hidden_pregunta_sin_ranking_cuenta_como_fallo(student):
    """Caso adicional: si falta el ranking de una pregunta, se trata como vacío"""
    golden = [{"id": "q1", "relevant_ids": ["a"]}, {"id": "q2", "relevant_ids": ["b"]}]
    out = student.evaluate({"q1": ["a"]}, golden, k=1)
    expect_close(out["hit"], 0.5, what="hit con un ranking ausente")
    expect_equal(out["n"], 2, what="preguntas evaluadas")


def test_hidden_sin_preguntas_con_relevantes(student):
    """Caso adicional: sin preguntas evaluables todo vale 0 y n es 0"""
    out = student.evaluate({}, [{"id": "q1", "relevant_ids": []}], k=3)
    expect_equal(out["n"], 0, what="n")
    expect_equal(out["hit"], 0.0, what="hit")
