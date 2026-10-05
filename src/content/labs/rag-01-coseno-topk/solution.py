import numpy as np


def cosine_similarity(a, b):
    """Similitud coseno entre dos vectores 1-D.

    Si alguno de los dos es el vector cero, devuelve 0.0 (no lances ninguna excepción).
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(a @ b / (norm_a * norm_b))


def cosine_top_k(query, matrix, k=3):
    """Devuelve los k vectores de `matrix` más parecidos a `query`.

    query:  array de forma (d,)
    matrix: array de forma (n, d), un vector por fila
    k:      cuántos resultados devolver

    Devuelve (indices, scores): dos arrays de NumPy ordenados de mayor a menor similitud.
    - Si k > n, devuelve las n filas que haya.
    - En caso de empate, va primero el índice menor.
    - Una fila de ceros tiene similitud 0.0 (nunca NaN).
    - No modifiques `matrix` ni `query`.
    """
    q = np.asarray(query, dtype=float)
    m = np.asarray(matrix, dtype=float)

    # Producto escalar de cada fila con la consulta, y producto de las normas.
    dots = m @ q
    norms = np.linalg.norm(m, axis=1) * np.linalg.norm(q)

    # División segura: donde la norma es 0 la similitud queda en 0.0 en lugar de NaN.
    scores = np.divide(dots, norms, out=np.zeros_like(dots), where=norms > 0)

    # Orden estable de mayor a menor: ante un empate se mantiene el índice menor primero.
    order = np.argsort(-scores, kind="stable")[: max(k, 0)]
    return order, scores[order]


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    docs = np.array([[0.80, 0.20, 0.10], [0.10, 0.90, 0.30], [0.85, 0.05, 0.25]])
    consulta = np.array([0.90, 0.10, 0.20])
    print(cosine_top_k(consulta, docs, k=2))
