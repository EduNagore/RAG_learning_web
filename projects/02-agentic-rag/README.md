# Proyecto 2: Agentic RAG

Guía completa en la web del curso: `/proyectos/02-agentic-rag/`.

## Objetivo

Un agente que decide cuándo recuperar, reformula la consulta cuando la evidencia no basta y se detiene con guardas. Se implementa como un grafo de LangGraph (`StateGraph`, nodos, aristas condicionales) y se compara con un RAG de un paso.

## Puesta en marcha

```bash
uv sync
cp .env.example .env
```

Versiones mínimas comprobadas en PyPI el 2026-10-06 (`langgraph` 1.2, `anthropic` 1.11). La API de `StateGraph` usada (`add_node`, `add_edge`, `add_conditional_edges`, `compile`, `invoke`) es la de la guía de inicio rápido de LangGraph; revísala si actualizas.

## Qué hay que completar

`src/graph.py` (nodos y rutas) y `src/evaluate.py` (comparación). Reutiliza el recuperador del proyecto 1.

## Criterios de evaluación

- El agente no recupera en preguntas triviales y se abstiene si la evidencia no basta.
- Límite de pasos y presupuesto de tokens respetados, con el motivo de parada registrado.
- Comparación con el RAG de un paso sobre al menos 30 preguntas, incluidas 10 multi-salto, con exactitud, pasos y tokens.

## Extensiones

Checkpoints y aprobación humana antes de responder, memoria de conversación y trayectorias de referencia para evaluar con las métricas del módulo de evaluación de agentes.
