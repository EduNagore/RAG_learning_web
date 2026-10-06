def rrf_fuse(rankings, k=60, weights=None):
    """Reciprocal Rank Fusion con pesos. Devuelve [(id, puntuación)] de mayor a menor.

    - weights: un peso por ranking (por defecto 1). ValueError si la longitud no coincide.
    - k negativo: ValueError.
    - Un id repetido dentro de un ranking solo cuenta su primera posición.
    - Empate: gana el id que apareció antes recorriendo los rankings en orden.
    """
    if k < 0:
        raise ValueError("k no puede ser negativo")
    if weights is None:
        weights = [1.0] * len(rankings)
    if len(weights) != len(rankings):
        raise ValueError("Debe haber un peso por ranking")

    puntos = {}
    orden = {}
    for ranking, peso in zip(rankings, weights, strict=True):
        vistos = set()
        for posicion, doc_id in enumerate(ranking, start=1):
            orden.setdefault(doc_id, len(orden))
            if doc_id in vistos:
                continue
            vistos.add(doc_id)
            puntos[doc_id] = puntos.get(doc_id, 0.0) + peso / (k + posicion)
    return sorted(puntos.items(), key=lambda par: (-par[1], orden[par[0]]))


def hybrid_search(query, retrievers, top_k=3, k=60, candidates=20):
    """Ejecuta cada retriever, recorta a `candidates`, fusiona con RRF y devuelve los top_k ids."""
    rankings = [list(retriever(query))[:candidates] for retriever in retrievers]
    return [doc_id for doc_id, _ in rrf_fuse(rankings, k=k)[:top_k]]


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    print(rrf_fuse([["a", "b", "c"], ["c", "a", "d"]]))
    print(rrf_fuse([["A", "B", "D"], ["C", "E", "B"]], k=0)[:2])
    print(rrf_fuse([["A", "B", "D"], ["C", "E", "B"]], k=60)[:2])
