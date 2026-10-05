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
    """Como máximo n reformulaciones: una por línea, sin numeración ni viñetas, sin duplicados."""
    variantes, vistas = [], set()
    for linea in (text or "").splitlines():
        limpia = re.sub(r"^\s*(?:\d+[.)]|[-*•])\s*", "", linea).strip()
        if not limpia or limpia.lower() in vistas:
            continue
        vistas.add(limpia.lower())
        variantes.append(limpia)
    return variantes[:n]


def expand_queries(llm, question, n=3):
    """[pregunta original, *variantes] con una sola llamada al modelo."""
    prompt = f"Escribe {n} reformulaciones distintas de esta pregunta, una por línea: {question}"
    respuesta = llm.generate([Message("user", prompt)])
    consultas = [question]
    for variante in parse_variants(respuesta.text, n):
        if variante.lower() != question.lower():
            consultas.append(variante)
    return consultas


def multi_query_search(question, llm, retriever, n=3, top_k=3, k=60):
    """Expande la pregunta, busca con cada consulta y fusiona con RRF."""
    rankings = [retriever(consulta) for consulta in expand_queries(llm, question, n)]
    return rrf_ids(rankings, k=k)[:top_k]


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    print(
        parse_variants("1. plazo de reembolso\n2) Plazo de reembolso\n- tiempo de devolución\n", 3)
    )
