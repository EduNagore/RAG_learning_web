# Proyecto 5: Harness de evaluación de agentes

Guía completa en la web del curso: `/proyectos/05-harness-evaluacion/`.

## Objetivo

Construir un harness que ejecute un dataset de tareas varias veces en entornos limpios, compruebe el resultado en el entorno y las restricciones de trayectoria, calcule pass@k y pass^k y ayude a analizar los fallos.

## Puesta en marcha

```bash
uv sync
cp .env.example .env
```

Empieza con el agente de juguete de `src/toy_agent.py` (no necesita claves) y, cuando el harness funcione, conecta un agente real (extensión `agent`).

## Qué hay que completar

`src/harness.py`: las métricas, el entorno limpio por intento, la ejecución de tareas y el informe. Copia `data/tasks.example.json` a `data/tasks.json` y amplíalo hasta 20 tareas.

## Criterios de evaluación

- pass@k y pass^k correctos (comprueba a mano: con n=5 y c=2, pass@3 es 0,9 y pass^2 es 0,1).
- Cada intento parte de un entorno nuevo; demuestra con un experimento qué pasa si se comparte.
- El resultado se comprueba en el entorno y se detectan herramientas prohibidas.
- Un análisis de al menos 10 fallos leídos en las trazas, clasificados por causa.

## Extensiones

Grader de modelo calibrado con muestras humanas, ejecución en CI con un conjunto de regresión, y evaluación de trayectorias frente a una referencia (recall, precisión y orden).
