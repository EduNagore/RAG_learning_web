import math


def hit_at_k(ranked, relevant, k):
    """1.0 si algún documento relevante está entre los k primeros; 0.0 si no."""
    return 1.0 if any(d in relevant for d in ranked[:k]) else 0.0


def recall_at_k(ranked, relevant, k):
    """Fracción de los relevantes que aparecen entre los k primeros. None si no hay relevantes."""
    if not relevant:
        return None
    return len(set(ranked[:k]) & set(relevant)) / len(relevant)


def precision_at_k(ranked, relevant, k):
    """Relevantes entre los k primeros dividido por k (aunque haya menos de k resultados)."""
    return len([d for d in ranked[:k] if d in relevant]) / k


def reciprocal_rank(ranked, relevant, k=None):
    """1 / posición del primer relevante (0.0 si no aparece en los k primeros)."""
    for position, doc_id in enumerate(ranked[:k], start=1):
        if doc_id in relevant:
            return 1 / position
    return 0.0


def ndcg_at_k(ranked, relevant, k):
    """nDCG con relevancia binaria. 0.0 si no hay relevantes."""
    dcg = sum(1 / math.log2(i + 2) for i, d in enumerate(ranked[:k]) if d in relevant)
    ideal = sum(1 / math.log2(i + 2) for i in range(min(len(relevant), k)))
    return dcg / ideal if ideal else 0.0


def evaluate(run, golden, k=3):
    """Medias de las métricas sobre las preguntas con documentos relevantes.

    run: dict id_pregunta -> ranking (lista de ids). golden: lista de dicts con id y relevant_ids.
    """
    rows = [q for q in golden if q["relevant_ids"]]
    if not rows:
        return {"n": 0, "hit": 0.0, "recall": 0.0, "precision": 0.0, "mrr": 0.0, "ndcg": 0.0}

    def mean(metric):
        return sum(metric(run.get(q["id"], []), set(q["relevant_ids"])) for q in rows) / len(rows)

    return {
        "n": len(rows),
        "hit": mean(lambda r, rel: hit_at_k(r, rel, k)),
        "recall": mean(lambda r, rel: recall_at_k(r, rel, k)),
        "precision": mean(lambda r, rel: precision_at_k(r, rel, k)),
        "mrr": mean(lambda r, rel: reciprocal_rank(r, rel, k)),
        "ndcg": mean(lambda r, rel: ndcg_at_k(r, rel, k)),
    }


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    ranking = ["d3", "d1", "d9", "d2"]
    relevantes = {"d1", "d2"}
    print(hit_at_k(ranking, relevantes, 1), recall_at_k(ranking, relevantes, 2))
    print(round(ndcg_at_k(ranking, relevantes, 4), 4))
