from ragkit.llm import approx_tokens


def edges_order(ranking):
    """Recibe una lista del mejor al peor y la reordena: el mejor al principio, el segundo
    al final, el tercero en la segunda posición, el cuarto en la penúltima... Los peores
    quedan en el centro. No modifica la lista original.
    """
    # TODO
    raise NotImplementedError("Completa edges_order")


def insert_evidence(distractors, evidence_id, position):
    """Lista NUEVA con los distractores en su orden y evidence_id insertado en `position`.

    Una posición negativa se trata como 0 y una mayor que la longitud, como el final.
    """
    # TODO
    raise NotImplementedError("Completa insert_evidence")


def fit_to_budget(docs, budget_tokens):
    """Ids de los documentos que caben en el presupuesto de tokens.

    docs: lista de dicts con 'id' y 'text', ordenados por relevancia. Se recorren en orden,
    se suma approx_tokens(doc["text"]) y un documento se conserva solo si, con él, no se
    supera el presupuesto; los que no caben se saltan y se sigue con los siguientes.
    """
    # TODO
    raise NotImplementedError("Completa fit_to_budget")


def position_zone(order, doc_id):
    """'inicio', 'medio' o 'final' según dónde esté doc_id en order.

    Con i = índice y n = longitud: inicio si i < n / 3, final si i >= 2 * n / 3, medio si no.
    Si doc_id no está en order, lanza ValueError.
    """
    # TODO
    raise NotImplementedError("Completa position_zone")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    try:
        orden = edges_order(["d1", "d2", "d3", "d4", "d5"])
        print(orden, position_zone(orden, "d2"))
    except NotImplementedError as e:
        print("Aún por completar:", e)
