# Proyecto 3: Sistema multiagente de investigación

Guía completa en la web del curso: `/proyectos/03-investigacion-multiagente/`.

## Objetivo

Un orquestador descompone una pregunta abierta, lanza sub-agentes de búsqueda en paralelo con contextos aislados y un sintetizador redacta un informe con citas verificadas. El proyecto usa la API del modelo directamente (`asyncio` y el SDK de Anthropic) para que veas cada pieza; después puedes reimplementarlo con LangGraph, el SDK de Agentes de OpenAI o el SDK de Agentes de Claude, comprobando su documentación vigente.

## Puesta en marcha

```bash
uv sync
cp .env.example .env
```

Dependencias comprobadas en PyPI el 2026-10-06. Necesitas una herramienta de búsqueda y de lectura de páginas (la elección es tuya: una API de búsqueda o un servidor MCP; el proyecto 4 puede aportar uno).

## Qué hay que completar

`src/orchestrator.py` (plan, sub-agente, cobertura) y `src/synthesize.py` (síntesis y verificación).

## Criterios de evaluación

- Cada encargo incluye objetivo, formato de salida, herramientas y límites.
- Guardas por sub-agente (pasos, tokens, bucle) y por informe, con motivos de parada.
- Comparación con una línea base de un único agente sobre 10 preguntas: calidad (rúbrica), exactitud de citas, tokens y tiempo.
- Ningún sub-agente tiene a la vez datos privados y un canal de salida.

## Extensiones

Segunda ronda de cobertura, puntuación de fiabilidad de fuentes, compactación del plan y trazas completas por agente.
