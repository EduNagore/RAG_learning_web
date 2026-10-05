import numpy as np
from ragkit.testing import expect_close, expect_equal, expect_raises, expect_true


def _datos(n=600, d=16, grupos=12, seed=3):
    """Vectores normalizados con grupos bien marcados."""
    rng = np.random.default_rng(seed)
    centros = rng.normal(size=(grupos, d))
    X = centros[rng.integers(0, grupos, n)] + 0.15 * rng.normal(size=(n, d))
    return X / np.linalg.norm(X, axis=1, keepdims=True)


def _exacto(X, q, k):
    return np.argsort(-(X @ q), kind="stable")[:k]


def test_kmeans_devuelve_centroides_normalizados(student):
    """kmeans devuelve n_clusters centroides de norma 1"""
    X = _datos()
    c = student.kmeans(X, 8)
    expect_equal(c.shape, (8, X.shape[1]), what="forma de los centroides")
    expect_true(
        np.allclose(np.linalg.norm(c, axis=1), 1.0), "Los centroides deben estar normalizados."
    )


def test_kmeans_es_reproducible_con_la_misma_semilla(student):
    """Con la misma semilla se obtienen los mismos centroides"""
    X = _datos()
    expect_true(
        np.allclose(student.kmeans(X, 8, seed=5), student.kmeans(X, 8, seed=5)),
        "No es reproducible.",
    )


def test_las_listas_particionan_los_vectores(student):
    """Cada vector está en exactamente una lista"""
    X = _datos()
    index = student.build_ivf(X, 10)
    todos = np.concatenate(index["lists"])
    expect_equal(len(index["lists"]), 10, what="número de listas")
    expect_equal(
        sorted(todos.tolist()), list(range(len(X))), what="vectores repartidos en las listas"
    )


def test_con_todas_las_listas_equivale_a_la_busqueda_exacta(student):
    """Con n_probe igual al número de listas el resultado coincide con la búsqueda exacta"""
    X = _datos()
    index = student.build_ivf(X, 10)
    q = X[7]
    ids, n = student.ivf_search(q, X, index, k=10, n_probe=10)
    expect_equal(ids.tolist(), _exacto(X, q, 10).tolist(), what="vecinos")
    expect_equal(n, len(X), what="vectores revisados")


def test_menos_listas_revisan_menos_vectores(student):
    """Con n_probe pequeño se revisa solo una parte de los vectores"""
    X = _datos()
    index = student.build_ivf(X, 12)
    _, n1 = student.ivf_search(X[0], X, index, n_probe=1)
    _, n3 = student.ivf_search(X[0], X, index, n_probe=3)
    expect_true(0 < n1 < n3 < len(X), f"Se esperaba 0 < {n1} < {n3} < {len(X)}.")


def test_el_recall_no_baja_al_subir_n_probe(student):
    """Más listas visitadas nunca empeoran el recall"""
    X = _datos()
    index = student.build_ivf(X, 12)
    consultas = X[::25]
    medias = []
    for n_probe in (1, 2, 4, 12):
        recalls = [
            student.recall_at_k(
                student.ivf_search(q, X, index, k=10, n_probe=n_probe)[0], _exacto(X, q, 10)
            )
            for q in consultas
        ]
        medias.append(float(np.mean(recalls)))
    expect_true(medias == sorted(medias), f"El recall debería ser no decreciente: {medias}")
    expect_close(medias[-1], 1.0, what="recall con todas las listas")
    expect_true(
        medias[0] > 0.5,
        f"Con datos agrupados, n_probe=1 debería rendir bastante mejor: {medias[0]:.2f}",
    )


def test_recall_at_k(student):
    """recall_at_k es la fracción de vecinos exactos recuperados"""
    expect_close(student.recall_at_k([1, 2, 3], [1, 2, 4, 5]), 0.5, what="recall 2/4")
    expect_close(student.recall_at_k([], [1, 2]), 0.0, what="recall sin aciertos")
    expect_close(student.recall_at_k([9], []), 1.0, what="recall con referencia vacía")


def test_hidden_resultados_ordenados_por_similitud(student):
    """Caso adicional: orden del resultado"""
    X = _datos()
    index = student.build_ivf(X, 10)
    q = X[3]
    ids, _ = student.ivf_search(q, X, index, k=8, n_probe=3)
    scores = (X[ids] @ q).tolist()
    expect_true(
        scores == sorted(scores, reverse=True), "Los ids deben ir de mayor a menor similitud."
    )


def test_hidden_k_mayor_que_los_candidatos(student):
    """Caso adicional: pocos candidatos"""
    X = _datos(n=60, grupos=6)
    index = student.build_ivf(X, 6)
    ids, n = student.ivf_search(X[0], X, index, k=1000, n_probe=1)
    expect_equal(len(ids), n, what="resultados cuando k supera los candidatos")


def test_hidden_demasiados_clusters(student):
    """Caso adicional: parámetros inválidos"""
    X = _datos(n=20)
    expect_raises(ValueError, student.kmeans, X, 21, what="n_clusters > nº de vectores")


def test_hidden_la_inicializacion_usa_la_semilla_indicada(student):
    """Caso adicional: inicialización"""
    X = _datos()
    rng = np.random.default_rng(5)
    esperado = X[rng.choice(len(X), 8, replace=False)]
    expect_true(
        np.allclose(student.kmeans(X, 8, n_iters=0, seed=5), esperado),
        "Sin iteraciones, los centroides deben ser los vectores elegidos con rng.choice y la semilla indicada.",
    )
