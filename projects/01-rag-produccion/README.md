# Proyecto 1: RAG de producción sobre documentación

Guía completa en la web del curso: `/proyectos/01-rag-produccion/`.

## Objetivo

Construir un RAG sobre una carpeta de documentación real: ingesta con Docling, índice en Qdrant, búsqueda híbrida con fusión RRF, filtrado por permisos, respuestas con citas validadas y abstención, y evaluación sobre un conjunto de oro.

## Puesta en marcha

```bash
uv sync
cp .env.example .env   # y rellena ANTHROPIC_API_KEY
```

Dependencias comprobadas en PyPI el 2026-10-06 (`docling` 2.134, `qdrant-client` 1.19, `sentence-transformers` 6.1, `anthropic` 1.11). Revisa la documentación vigente antes de actualizarlas.

## Qué hay que completar

Busca los `TODO` en `src/`:

1. `ingest.py`: troceado por secciones con contexto.
2. `retrieve.py`: búsqueda léxica, recuperación híbrida con permisos y reranker opcional.
3. `answer.py`: validación de citas.
4. `evaluate.py`: recall@k, MRR y el bucle de evaluación (copia `data/golden.example.json` a `data/golden.json` y amplíalo).

## Criterios de evaluación

- Recall@5 y MRR medidos sobre al menos 30 preguntas reales, con el tamaño de la muestra reportado.
- Ninguna fuga de permisos en las pruebas con dos perfiles distintos.
- Todas las citas existen; las preguntas sin respuesta se abstienen.
- Un informe de fallos clasificados por etapa (recuperación, ranking, generación).

## Extensiones

Reranker, evaluación con RAGAS (extensión `eval`), trazas con Langfuse (extensión `tracing`), actualización incremental del índice y caché de respuestas.
