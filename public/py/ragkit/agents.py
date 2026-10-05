"""Tipos mínimos para los laboratorios de agentes, para centrarse en la lógica."""

from dataclasses import dataclass, field

from .llm import LLMResponse, Message, MockLLM, ToolCall  # noqa: F401  (reexportados)


@dataclass
class ToolSpec:
    """Descripción de una herramienta tal y como se le presenta al modelo."""

    name: str
    description: str
    parameters: dict = field(default_factory=dict)  # JSON Schema de los argumentos


@dataclass
class AgentResult:
    """Resultado de ejecutar un agente.

    answer: texto final, o None si no llegó a darlo.
    steps: número de llamadas al modelo realizadas.
    stopped: "final" si el modelo respondió; "max_steps" si se alcanzó el límite.
    trace: lista de eventos (diccionarios) con lo ocurrido, en orden.
    """

    answer: str | None
    steps: int
    stopped: str
    trace: list[dict] = field(default_factory=list)
