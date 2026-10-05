import numpy as np


def cosine_similarity(a, b):
    """Similitud coseno entre dos vectores 1-D.

    Si alguno de los dos es el vector cero, devuelve 0.0 (no lances ninguna excepción).
    """
    # TODO: implementa  (a · b) / (‖a‖ ‖b‖)
    raise NotImplementedError("Completa cosine_similarity")


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
    # TODO: hazlo vectorizado, sin bucles sobre las filas
    raise NotImplementedError("Completa cosine_top_k")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    docs = np.array([[0.80, 0.20, 0.10], [0.10, 0.90, 0.30], [0.85, 0.05, 0.25]])
    consulta = np.array([0.90, 0.10, 0.20])
    try:
        print(cosine_top_k(consulta, docs, k=2))
    except NotImplementedError as e:
        print("Aún por completar:", e)
