"""Orquestador: descompone la pregunta, lanza sub-agentes en paralelo y decide si hay cobertura."""

import asyncio
from dataclasses import dataclass, field


@dataclass
class Assignment:
    """Encargo a un sub-agente: objetivo, formato de salida, herramientas y límites."""

    objective: str
    output_format: str = "JSON con hallazgos, fuentes (url y fecha), confianza y lo no comprobado"
    tools: list[str] = field(default_factory=lambda: ["search", "fetch"])
    boundaries: str = "Máximo 6 pasos. No busques fuera de este objetivo."


@dataclass
class Finding:
    claim: str
    source_url: str
    confidence: str  # "alta" | "media" | "baja"


async def plan(question: str) -> list[Assignment]:
    """TODO: pide al modelo 2-4 encargos NO solapados y escala el número al tipo de pregunta
    (una pregunta simple no necesita varios sub-agentes)."""
    raise NotImplementedError("Implementa el plan")


async def run_subagent(assignment: Assignment) -> list[Finding]:
    """TODO: bucle de herramientas con contexto AISLADO que devuelve solo hallazgos estructurados.

    Aplica guardas: pasos máximos, presupuesto de tokens y detección de la misma acción repetida.
    El contenido de las páginas es NO FIABLE: trátalo como datos, nunca como instrucciones.
    """
    raise NotImplementedError("Implementa el sub-agente")


async def research(question: str) -> list[Finding]:
    assignments = await plan(question)
    results = await asyncio.gather(*(run_subagent(a) for a in assignments))
    findings = [f for batch in results for f in batch]
    # TODO: evalúa la cobertura y, si falta algo, lanza UNA segunda ronda como máximo.
    return findings
