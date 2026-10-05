def rrf_fuse(rankings, k=60, weights=None):
    """Reciprocal Rank Fusion con pesos. Devuelve [(id, puntuación)] de mayor a menor.

    rankings: lista de rankings; cada uno es una lista de ids, del mejor al peor.
    - weights: un peso por ranking (por defecto 1). ValueError si la longitud no coincide.
    - k negativo: ValueError.
    - Un id repetido dentro de un ranking solo cuenta su primera posición.
    - Empate: gana el id que apareció antes recorriendo los rankings en orden.
    """
    # TODO:
    #   1. Valida k y weights.
    #   2. Para cada ranking y cada posición (empezando en 1): puntos[id] += peso / (k + posicion).
    #   3. Ordena por puntuación descendente y, si empatan, por primera aparición.
    raise NotImplementedError("Completa rrf_fuse")


def hybrid_search(query, retrievers, top_k=3, k=60, candidates=20):
    """Ejecuta cada retriever, recorta a `candidates`, fusiona con RRF y devuelve los top_k ids.

    retrievers: lista de funciones f(query) -> lista de ids, del mejor al peor.
    """
    # TODO
    raise NotImplementedError("Completa hybrid_search")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    try:
        print(rrf_fuse([["a", "b", "c"], ["c", "a", "d"]]))
        print(rrf_fuse([["A", "B", "D"], ["C", "E", "B"]], k=0)[:2])
        print(rrf_fuse([["A", "B", "D"], ["C", "E", "B"]], k=60)[:2])
    except NotImplementedError as e:
        print("Aún por completar:", e)
