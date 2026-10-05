import re

from ragkit.llm import Message


def rrf_ids(rankings, k=60):
    """Fusión RRF ya resuelta: devuelve los ids ordenados (empate: primera aparición)."""
    puntos, orden = {}, {}
    for ranking in rankings:
        for posicion, doc_id in enumerate(ranking, start=1):
            orden.setdefault(doc_id, len(orden))
            puntos[doc_id] = puntos.get(doc_id, 0.0) + 1 / (k + posicion)
    return sorted(puntos, key=lambda d: (-puntos[d], orden[d]))


def parse_variants(text, n):
    """Como máximo n reformulaciones: una por línea, sin numeración ni viñetas, sin duplicados.

    - Quita prefijos como "1.", "2)", "-", "*", "•" y los espacios sobrantes.
    - Ignora las líneas vacías.
    - Descarta duplicados sin distinguir mayúsculas (se queda la primera aparición).
    """
    # TODO
    raise NotImplementedError("Completa parse_variants")


def expand_queries(llm, question, n=3):
    """[pregunta original, *variantes] con UNA sola llamada a llm.generate.

    - El mensaje de usuario debe contener la pregunta y el número n.
    - La pregunta original va primera.
    - Una variante igual a la original (sin distinguir mayúsculas) se descarta.
    """
    # TODO: llm.generate([Message("user", prompt)]).text es el texto del modelo.
    raise NotImplementedError("Completa expand_queries")


def multi_query_search(question, llm, retriever, n=3, top_k=3, k=60):
    """Expande la pregunta, busca con cada consulta (retriever(consulta) -> ids) y fusiona."""
    # TODO
    raise NotImplementedError("Completa multi_query_search")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    try:
        print(parse_variants("1. plazo de reembolso\n2) Plazo de reembolso\n- tiempo de devolución\n", 3))
    except NotImplementedError as e:
        print("Aún por completar:", e)
