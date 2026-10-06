from ragkit.llm import approx_tokens


def edges_order(ranking):
    """El mejor al principio, el segundo al final y los peores en el centro."""
    return ranking[0::2] + ranking[1::2][::-1]


def insert_evidence(distractors, evidence_id, position):
    """Copia de distractors con la evidencia insertada en `position` (acotada a 0..len)."""
    result = list(distractors)
    result.insert(max(0, min(position, len(result))), evidence_id)
    return result


def fit_to_budget(docs, budget_tokens):
    """Ids de los documentos que caben en el presupuesto; los que no caben se saltan."""
    kept, used = [], 0
    for doc in docs:
        cost = approx_tokens(doc["text"])
        if used + cost <= budget_tokens:
            kept.append(doc["id"])
            used += cost
    return kept


def position_zone(order, doc_id):
    """'inicio', 'medio' o 'final' según la posición de doc_id en order."""
    i, n = order.index(doc_id), len(order)
    if i < n / 3:
        return "inicio"
    if i >= 2 * n / 3:
        return "final"
    return "medio"


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    orden = edges_order(["d1", "d2", "d3", "d4", "d5"])
    print(orden, position_zone(orden, "d2"))
