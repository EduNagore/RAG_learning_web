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
    # TODO:
    #   1. N = número de documentos y avgdl = longitud media (cuidado si avgdl es 0).
    #   2. Para cada término único de la consulta: n = nº de documentos que lo contienen,
    #      idf = log(1 + (N - n + 0.5) / (n + 0.5)).
    #   3. Para cada documento, suma idf * f * (k1 + 1) / (f + k1 * (1 - b + b * len(doc) / avgdl)),
    #      donde f es cuántas veces aparece el término en el documento.
    raise NotImplementedError("Completa bm25_scores")


def bm25_search(query, corpus, top_k=3):
    """Busca en el corpus y devuelve [(id, puntuación), ...] de mayor a menor.

    query:  texto de la consulta.
    corpus: lista de diccionarios con 'id', 'title' y 'text'.
    - Tokeniza con ragkit.text.tokenize, usando título y texto de cada documento.
    - Solo incluye documentos con puntuación mayor que 0.
    - Ante un empate gana el documento que aparece antes en el corpus.
    """
    # TODO
    raise NotImplementedError("Completa bm25_search")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    docs = [["a", "b", "a"], ["b", "c"], ["c", "c", "d", "e"]]
    try:
        print(bm25_scores(["a"], docs))  # aproximadamente [1.40118, 0.0, 0.0]
        for doc_id, score in bm25_search("¿Cuánto tarda el reembolso?", load_corpus()):
            print(doc_id, round(score, 3))
    except NotImplementedError as e:
        print("Aún por completar:", e)
