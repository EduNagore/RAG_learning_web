"""Ingesta: documentos -> Markdown (Docling) -> fragmentos con contexto -> Qdrant."""

import os
import re
from pathlib import Path

from docling.document_converter import DocumentConverter
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

load_dotenv()
COLLECTION = "docs"


def to_markdown(path: Path) -> str:
    """Convierte un PDF, DOCX o HTML a Markdown con Docling."""
    result = DocumentConverter().convert(str(path))
    return result.document.export_to_markdown()


def chunk_markdown(markdown: str, doc_title: str, max_chars: int = 1200) -> list[dict]:
    """Trocea por secciones de Markdown y antepone título y ruta de secciones a cada fragmento.

    TODO 1: parte el texto por encabezados (líneas que empiezan por '#') y mantén la ruta
            de encabezados activa («Devoluciones > Plazos»).
    TODO 2: si una sección supera `max_chars`, divídela por párrafos.
    TODO 3: devuelve dicts con `text` (con el prefijo de contexto), `doc`, `section` y `chunk_id`.
    """
    _ = (markdown, doc_title, max_chars, re)  # quita esta línea al implementar
    raise NotImplementedError("Implementa el troceado por secciones")


def index(chunks: list[dict]) -> QdrantClient:
    """Calcula embeddings y los guarda en Qdrant con los metadatos como payload."""
    model = SentenceTransformer(os.environ["EMBEDDING_MODEL"])
    vectors = model.encode([c["text"] for c in chunks], normalize_embeddings=True)
    client = QdrantClient(os.environ.get("QDRANT_URL", ":memory:"))
    client.create_collection(
        COLLECTION,
        vectors_config=VectorParams(size=vectors.shape[1], distance=Distance.COSINE),
    )
    client.upsert(
        COLLECTION,
        points=[
            PointStruct(id=i, vector=v.tolist(), payload=c)
            for i, (c, v) in enumerate(zip(chunks, vectors, strict=True))
        ],
        wait=True,
    )
    return client


if __name__ == "__main__":
    raise SystemExit("Importa estas funciones desde answer.py o evaluate.py")
