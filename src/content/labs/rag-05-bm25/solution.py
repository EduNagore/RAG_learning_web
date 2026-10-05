import math

from ragkit.data import load_corpus
from ragkit.text import tokenize


def bm25_scores(query_tokens, docs_tokens, k1=1.5, b=0.75):
    """Puntuación BM25 de cada documento para la consulta.

    query_tokens: lista de tokens de la consulta (los repetidos cuentan una sola vez).
    docs_tokens:  lista de documentos, cada uno una lista de tokens.
    Devuelve una lista de floats, uno por documento y en el mismo orden.
    Si no hay documentos o todos están vacíos, devuelve ceros.
    """
    n_docs = len(docs_tokens)
    if n_docs == 0:
        return []
    avgdl = sum(len(d) for d in docs_tokens) / n_docs
    if avgdl == 0:
        return [0.0] * n_docs

    scores = [0.0] * n_docs
    for term in set(query_tokens):
        # n: en cuántos documentos aparece el término (no cuántas veces en total).
        n = sum(1 for doc in docs_tokens if term in doc)
        if n == 0:
            continue
        idf = math.log(1 + (n_docs - n + 0.5) / (n + 0.5))
        for i, doc in enumerate(docs_tokens):
            f = doc.count(term)
            if f == 0:
                continue
            norm = f + k1 * (1 - b + b * len(doc) / avgdl)
            scores[i] += idf * f * (k1 + 1) / norm
    return scores


def bm25_search(query, corpus, top_k=3):
    """Busca en el corpus y devuelve [(id, puntuación), ...] de mayor a menor.

    query:  texto de la consulta.
    corpus: lista de diccionarios con 'id', 'title' y 'text'.
    - Tokeniza con ragkit.text.tokenize, usando título y texto de cada documento.
    - Solo incluye documentos con puntuación mayor que 0.
    - Ante un empate gana el documento que aparece antes en el corpus.
    """
    docs_tokens = [tokenize(d["title"] + " " + d["text"]) for d in corpus]
    scores = bm25_scores(tokenize(query), docs_tokens)
    ranked = sorted(
        ((doc["id"], score, position) for position, (doc, score) in enumerate(zip(corpus, scores))),
        key=lambda item: (-item[1], item[2]),
    )
    return [(doc_id, score) for doc_id, score, _ in ranked if score > 0][:top_k]


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    docs = [["a", "b", "a"], ["b", "c"], ["c", "c", "d", "e"]]
    print(bm25_scores(["a"], docs))  # aproximadamente [1.40118, 0.0, 0.0]
    for doc_id, score in bm25_search("¿Cuánto tarda el reembolso?", load_corpus()):
        print(doc_id, round(score, 3))
