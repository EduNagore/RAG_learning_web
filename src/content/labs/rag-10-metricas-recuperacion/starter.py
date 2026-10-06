import math


def hit_at_k(ranked, relevant, k):
    """1.0 si algún relevante está entre los k primeros; 0.0 si no."""
    # TODO
    raise NotImplementedError("Completa hit_at_k")


def recall_at_k(ranked, relevant, k):
    """Fracción de los relevantes que aparecen entre los k primeros. None si no hay relevantes."""
    # TODO
    raise NotImplementedError("Completa recall_at_k")


def precision_at_k(ranked, relevant, k):
    """Relevantes entre los k primeros dividido por k (aunque haya menos de k resultados)."""
    # TODO
    raise NotImplementedError("Completa precision_at_k")


def reciprocal_rank(ranked, relevant, k=None):
    """1 / posición del primer relevante dentro de los k primeros (todos si k es None); 0.0 si no."""
    # TODO
    raise NotImplementedError("Completa reciprocal_rank")


def ndcg_at_k(ranked, relevant, k):
    """nDCG con relevancia binaria: DCG = suma 1/log2(i + 2) por cada relevante en la posición i.

    El DCG ideal usa min(len(relevant), k) posiciones consecutivas. 0.0 si no hay relevantes.
    """
    # TODO
    raise NotImplementedError("Completa ndcg_at_k")


def evaluate(run, golden, k=3):
    """Medias de las métricas sobre las preguntas que tienen documentos relevantes.

    run: dict id_pregunta -> ranking (lista de ids). golden: lista de dicts con id y relevant_ids.
    Devuelve {"n", "hit", "recall", "precision", "mrr", "ndcg"} (n = preguntas evaluadas).
    Si falta el ranking de una pregunta, se trata como una lista vacía.
    """
    # TODO
    raise NotImplementedError("Completa evaluate")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    ranking = ["d3", "d1", "d9", "d2"]
    relevantes = {"d1", "d2"}
    try:
        print(hit_at_k(ranking, relevantes, 1), recall_at_k(ranking, relevantes, 2))
        print(round(ndcg_at_k(ranking, relevantes, 4), 4))
    except NotImplementedError as e:
        print("Aún por completar:", e)
