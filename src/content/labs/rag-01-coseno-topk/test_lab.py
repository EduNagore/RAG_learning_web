import numpy as np
from ragkit.testing import expect_close, expect_equal, expect_true

DOCS = np.array([[0.80, 0.20, 0.10], [0.10, 0.90, 0.30], [0.85, 0.05, 0.25]])
QUERY = np.array([0.90, 0.10, 0.20])


def test_similitud_de_vectores_conocidos(student):
    """cosine_similarity da 1 para vectores paralelos, 0 para ortogonales y -1 para opuestos"""
    expect_close(student.cosine_similarity([1, 2, 3], [2, 4, 6]), 1.0, what="vectores paralelos")
    expect_close(student.cosine_similarity([1, 0], [0, 1]), 0.0, what="vectores ortogonales")
    expect_close(student.cosine_similarity([1, 2], [-1, -2]), -1.0, what="vectores opuestos")


def test_similitud_ignora_la_longitud(student):
    """cosine_similarity no depende de la magnitud de los vectores"""
    base = student.cosine_similarity([1, 1], [1, 0])
    expect_close(student.cosine_similarity([10, 10], [3, 0]), base, what="vectores escalados")


def test_similitud_con_vector_cero(student):
    """cosine_similarity devuelve 0.0 con un vector cero, sin lanzar excepciones"""
    result = student.cosine_similarity([0, 0, 0], [1, 2, 3])
    expect_equal(result, 0.0, what="similitud con el vector cero")
    expect_equal(
        student.cosine_similarity([1, 2], [0, 0]), 0.0, what="similitud con el vector cero"
    )


def test_top_k_devuelve_los_mejores_en_orden(student):
    """cosine_top_k devuelve los índices y las puntuaciones más altas, de mayor a menor"""
    indices, scores = student.cosine_top_k(QUERY, DOCS, k=2)
    expect_equal([int(i) for i in indices], [2, 0], what="índices")
    expect_close(scores[0], 0.99641291, tol=1e-6, what="mejor puntuación")
    expect_close(scores[1], 0.98659707, tol=1e-6, what="segunda puntuación")


def test_top_k_devuelve_arrays_de_numpy(student):
    """cosine_top_k devuelve dos arrays de NumPy de longitud k"""
    indices, scores = student.cosine_top_k(QUERY, DOCS, k=3)
    expect_true(isinstance(indices, np.ndarray), "`indices` debe ser un array de NumPy.")
    expect_true(isinstance(scores, np.ndarray), "`scores` debe ser un array de NumPy.")
    expect_equal((len(indices), len(scores)), (3, 3), what="longitud de los resultados")


def test_top_k_mayor_que_n(student):
    """Si k es mayor que el número de filas, devuelve todas las que hay"""
    indices, scores = student.cosine_top_k(QUERY, DOCS, k=10)
    expect_equal(len(indices), 3, what="número de resultados con k > n")
    expect_equal(len(scores), 3, what="número de puntuaciones con k > n")


def test_top_k_desempata_por_indice_menor(student):
    """Ante un empate de puntuación, va primero el índice menor"""
    matrix = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 0.0]])
    indices, _ = student.cosine_top_k(np.array([1.0, 0.0]), matrix, k=3)
    expect_equal([int(i) for i in indices], [0, 2, 3], what="orden con empates")


def test_hidden_fila_de_ceros_no_da_nan(student):
    """Caso adicional: filas de ceros"""
    matrix = np.array([[0.0, 0.0], [1.0, 1.0]])
    indices, scores = student.cosine_top_k(np.array([1.0, 1.0]), matrix, k=2)
    expect_true(not np.isnan(scores).any(), "Una fila de ceros no debe producir NaN.")
    expect_equal([int(i) for i in indices], [1, 0], what="orden con una fila de ceros")
    expect_close(scores[1], 0.0, what="similitud de la fila de ceros")


def test_hidden_no_modifica_las_entradas(student):
    """Caso adicional: entradas intactas"""
    matrix = np.array([[3.0, 4.0], [1.0, 0.0]])
    query = np.array([3.0, 4.0])
    matrix_before, query_before = matrix.copy(), query.copy()
    student.cosine_top_k(query, matrix, k=2)
    expect_true(np.array_equal(matrix, matrix_before), "Tu función ha modificado `matrix`.")
    expect_true(np.array_equal(query, query_before), "Tu función ha modificado `query`.")


def test_hidden_coincide_con_una_referencia_en_datos_aleatorios(student):
    """Caso adicional: datos aleatorios"""
    rng = np.random.default_rng(7)
    matrix = rng.normal(size=(200, 16))
    query = rng.normal(size=16)
    reference = (matrix / np.linalg.norm(matrix, axis=1, keepdims=True)) @ (
        query / np.linalg.norm(query)
    )
    expected = np.argsort(-reference, kind="stable")[:5]
    indices, scores = student.cosine_top_k(query, matrix, k=5)
    expect_equal(
        [int(i) for i in indices], [int(i) for i in expected], what="índices con datos aleatorios"
    )
    expect_true(
        np.allclose(scores, reference[expected]), "Las puntuaciones no coinciden con la referencia."
    )
