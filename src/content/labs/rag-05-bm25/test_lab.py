from ragkit.data import load_corpus
from ragkit.testing import expect_close, expect_equal, expect_true

DOCS = [["a", "b", "a"], ["b", "c"], ["c", "c", "d", "e"]]


def test_un_termino_raro_puntua_solo_donde_aparece(student):
    """bm25_scores puntúa solo los documentos que contienen el término"""
    scores = student.bm25_scores(["a"], DOCS)
    expect_equal(len(scores), 3, what="número de puntuaciones")
    expect_close(scores[0], 1.40118, tol=1e-4, what="documento que contiene «a»")
    expect_equal(scores[1], 0, what="documento sin el término")
    expect_equal(scores[2], 0, what="documento sin el término")


def test_el_idf_depende_de_cuantos_documentos_contienen_el_termino(student):
    """Un término presente en más documentos pesa menos (IDF)"""
    scores = student.bm25_scores(["b"], DOCS)
    expect_close(scores[0], 0.47000, tol=1e-4, what="documento 0 con «b»")
    expect_close(scores[1], 0.55295, tol=1e-4, what="documento 1 con «b» (es más corto)")


def test_la_longitud_del_documento_normaliza(student):
    """La puntuación combina la frecuencia del término con la longitud del documento"""
    scores = student.bm25_scores(["c"], DOCS)
    expect_close(scores[1], 0.55295, tol=1e-4, what="«c» una vez en un documento de 2 tokens")
    expect_close(scores[2], 0.60646, tol=1e-4, what="«c» dos veces en un documento de 4 tokens")


def test_varios_terminos_se_suman(student):
    """Las puntuaciones de los términos de la consulta se suman"""
    scores = student.bm25_scores(["a", "b"], DOCS)
    expect_close(scores[0], 1.87119, tol=1e-4, what="documento 0")
    expect_close(scores[1], 0.55295, tol=1e-4, what="documento 1")


def test_parametros_k1_y_b(student):
    """k1 y b modifican la puntuación"""
    scores = student.bm25_scores(["b"], DOCS, k1=1.2, b=0.5)
    expect_close(scores[1], 0.517, tol=1e-3, what="con k1=1.2 y b=0.5")


def test_busqueda_devuelve_id_y_puntuacion_ordenados(student):
    """bm25_search devuelve (id, puntuación) de mayor a menor, con el mejor primero"""
    results = student.bm25_search(
        "¿Cuánto tarda el reembolso de una devolución?", load_corpus(), top_k=3
    )
    expect_true(len(results) == 3, f"Se esperaban 3 resultados y hay {len(results)}.")
    expect_equal(results[0][0], "doc-002", what="documento más relevante")
    scores = [s for _, s in results]
    expect_true(
        scores == sorted(scores, reverse=True),
        "Los resultados deben ir de mayor a menor puntuación.",
    )


def test_busqueda_encuentra_el_documento_correcto(student):
    """bm25_search encuentra el documento sobre métodos de pago"""
    results = student.bm25_search("tarjeta PayPal transferencia", load_corpus(), top_k=1)
    expect_equal(results[0][0], "doc-016", what="documento más relevante")


def test_hidden_sin_coincidencias_devuelve_lista_vacia(student):
    """Caso adicional: consulta sin coincidencias"""
    expect_equal(
        student.bm25_search("zzzz qqqq", load_corpus()), [], what="resultados sin coincidencias"
    )


def test_hidden_respeta_top_k_y_solo_puntuaciones_positivas(student):
    """Caso adicional: límite de resultados"""
    results = student.bm25_search("teletrabajo días por semana", load_corpus(), top_k=2)
    expect_equal(len(results), 2, what="número de resultados con top_k=2")
    expect_equal(results[0][0], "doc-032", what="documento más relevante")
    expect_true(
        all(score > 0 for _, score in results), "No debe haber resultados con puntuación 0."
    )


def test_hidden_terminos_repetidos_en_la_consulta_cuentan_una_vez(student):
    """Caso adicional: términos repetidos"""
    once = student.bm25_scores(["a"], DOCS)
    twice = student.bm25_scores(["a", "a", "a"], DOCS)
    expect_close(twice[0], once[0], what="puntuación con el término repetido")


def test_hidden_casos_limite_sin_dividir_por_cero(student):
    """Caso adicional: documentos vacíos"""
    expect_equal(list(student.bm25_scores(["a"], [])), [], what="sin documentos")
    expect_equal(list(student.bm25_scores(["a"], [[], []])), [0.0, 0.0], what="documentos vacíos")
    expect_equal(list(student.bm25_scores([], DOCS)), [0.0, 0.0, 0.0], what="consulta vacía")


def test_la_busqueda_tambien_usa_el_titulo(student):
    """bm25_search indexa el título además del texto"""
    corpus = [
        {"id": "a", "title": "Reembolsos", "text": "Información sobre almacén y paquetes."},
        {"id": "b", "title": "Otro tema", "text": "Nada que ver con la consulta."},
    ]
    results = student.bm25_search("reembolsos", corpus)
    expect_equal(
        [doc_id for doc_id, _ in results], ["a"], what="documentos encontrados por el título"
    )


def test_hidden_empate_gana_el_documento_anterior_del_corpus(student):
    """Caso adicional: desempate"""
    corpus = [
        {"id": "x", "title": "Tema", "text": "envío estándar"},
        {"id": "y", "title": "Tema", "text": "envío estándar"},
        {"id": "z", "title": "Tema", "text": "envío estándar"},
    ]
    results = student.bm25_search("envío", corpus, top_k=3)
    expect_equal(
        [doc_id for doc_id, _ in results], ["x", "y", "z"], what="orden con puntuaciones idénticas"
    )
