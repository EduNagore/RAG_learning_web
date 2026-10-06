import math


def dcg_at_k(gains, k):
    """DCG de las k primeras ganancias: suma g / log2(posición + 1)."""
    return sum(g / math.log2(i + 2) for i, g in enumerate(gains[:k]))


def ndcg_at_k(ranked_ids, relevance, k=10):
    """nDCG@k. El IDCG usa todas las ganancias de `relevance`; si es 0 devuelve 0.0."""
    ideal = dcg_at_k(sorted(relevance.values(), reverse=True), k)
    if ideal == 0:
        return 0.0
    return dcg_at_k([relevance.get(d, 0) for d in ranked_ids], k) / ideal


def rerank(query, candidates, score_fn, top_k=None):
    """Ids de `candidates` por score_fn(query, text) de mayor a menor (empate: orden original)."""
    ordered = sorted(candidates, key=lambda doc: -score_fn(query, doc["text"]))
    ids = [doc["id"] for doc in ordered]
    return ids if top_k is None else ids[:top_k]


def two_stage_search(query, first_stage, docs_by_id, score_fn, n_candidates=20, top_k=3):
    """Primera etapa barata (ids) y reranking de los n_candidates primeros."""
    candidates = [docs_by_id[i] for i in list(first_stage(query))[:n_candidates] if i in docs_by_id]
    return rerank(query, candidates, score_fn, top_k=top_k)


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    print(round(ndcg_at_k(["c", "a", "b"], {"a": 3, "b": 2, "c": 1}, k=3), 4))  # ≈ 0.8175
