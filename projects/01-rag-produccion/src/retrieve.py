"""Recuperación híbrida: léxica (BM25) + densa (Qdrant) fusionadas con RRF, más reordenación opcional."""

import os

from ingest import COLLECTION
from qdrant_client import QdrantClient
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer


def rrf(rankings: list[list[int]], k: int = 60) -> list[int]:
    """Fusión por rango recíproco: suma 1/(k + posición) por cada lista donde aparece el id."""
    scores: dict[int, float] = {}
    for ranking in rankings:
        for pos, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + pos)
    return sorted(scores, key=lambda d: (-scores[d], d))


def dense_search(client: QdrantClient, query: str, limit: int = 20) -> list[int]:
    model = SentenceTransformer(os.environ["EMBEDDING_MODEL"])
    vector = model.encode(query, normalize_embeddings=True).tolist()
    hits = client.query_points(COLLECTION, query=vector, limit=limit).points
    return [int(h.id) for h in hits]


def lexical_search(bm25: BM25Okapi, query: str, limit: int = 20) -> list[int]:
    """TODO: puntúa con bm25.get_scores(tokens) y devuelve los ids de los `limit` mejores."""
    _ = (bm25, query, limit)
    raise NotImplementedError("Implementa la búsqueda léxica")


def retrieve(
    client: QdrantClient, bm25: BM25Okapi, query: str, user_groups: set[str], top_k: int = 5
):
    """TODO 1: fusiona la búsqueda densa y la léxica con `rrf`.
    TODO 2: FILTRA POR PERMISOS durante la búsqueda (payload `groups`), no después de generar.
    TODO 3 (extensión): reordena los 30 mejores con un reranker y mide el cambio en recall@k.
    """
    _ = (client, bm25, query, user_groups, top_k)
    raise NotImplementedError("Implementa la recuperación híbrida con permisos")
