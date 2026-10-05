import math


def dcg_at_k(gains, k):
    """DCG de las k primeras ganancias: suma g / log2(posición + 1), con posiciones desde 1."""
    # TODO
    raise NotImplementedError("Completa dcg_at_k")


def ndcg_at_k(ranked_ids, relevance, k=10):
    """nDCG@k = DCG del ranking / DCG ideal.

    relevance: dict id -> ganancia (lo que no aparece vale 0).
    El IDCG usa todas las ganancias de `relevance` ordenadas de mayor a menor.
    Si el IDCG es 0, devuelve 0.0.
    """
    # TODO
    raise NotImplementedError("Completa ndcg_at_k")


def rerank(query, candidates, score_fn, top_k=None):
    """Ids de `candidates` ordenados por score_fn(query, text) de mayor a menor.

    candidates: lista de dicts con 'id' y 'text'. Los empates conservan el orden original.
    Si top_k no es None, recorta el resultado.
    """
    # TODO
    raise NotImplementedError("Completa rerank")


def two_stage_search(query, first_stage, docs_by_id, score_fn, n_candidates=20, top_k=3):
    """Primera etapa barata (ids) y reranking de los n_candidates primeros.

    first_stage(query) -> lista de ids. Ignora los ids que no estén en docs_by_id.
    """
    # TODO
    raise NotImplementedError("Completa two_stage_search")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    try:
        print(round(ndcg_at_k(["c", "a", "b"], {"a": 3, "b": 2, "c": 1}, k=3), 4))  # ≈ 0.8175
    except NotImplementedError as e:
        print("Aún por completar:", e)
