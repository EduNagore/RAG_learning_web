"""LLM simulado y tipos de mensaje para practicar sin red ni claves de API.

`MockLLM` devuelve respuestas guionizadas: una lista que se consume en orden (`script`) o
reglas por patrón (`rules`). Las respuestas pueden ser texto o llamadas a herramientas, en un
formato parecido al de las APIs reales. Cuenta tokens aproximados y un coste FICTICIO.
"""

import json
import re
from dataclasses import dataclass, field


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass
class LLMResponse:
    text: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)

    @property
    def stop_reason(self) -> str:
        """'tool_use' si el modelo pide herramientas; 'end_turn' si ya ha terminado."""
        return "tool_use" if self.tool_calls else "end_turn"


@dataclass
class Message:
    """Mensaje de la conversación. `role` es system, user, assistant o tool."""

    role: str
    content: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_call_id: str | None = None


def approx_tokens(text: str | None) -> int:
    """Aproximación de 1 token por cada 4 caracteres (solo para estimar en los ejercicios)."""
    return (len(text) + 3) // 4 if text else 0


class MockLLMExhausted(Exception):
    """El guion del MockLLM se agotó: tu código llamó al modelo más veces de las previstas."""


class MockLLM:
    # Precios ficticios en USD por millón de tokens, solo para practicar el cálculo de coste.
    PRICE_IN_PER_M = 1.0
    PRICE_OUT_PER_M = 5.0

    def __init__(self, script=None, rules=None, default=None):
        self._counter = 0
        self._script = [self._coerce(item) for item in (script or [])]
        self._rules = [(re.compile(p, re.IGNORECASE), self._coerce(r)) for p, r in (rules or [])]
        self._default = None if default is None else self._coerce(default)
        self.calls: list[dict] = []
        self.input_tokens = 0
        self.output_tokens = 0

    def _next_id(self) -> str:
        self._counter += 1
        return f"call_{self._counter}"

    def _coerce(self, item) -> LLMResponse:
        """Acepta LLMResponse, texto, {"tool": nombre, "args": {...}} o una lista de ellos."""
        if isinstance(item, LLMResponse):
            return item
        if isinstance(item, str):
            return LLMResponse(text=item)
        specs = item if isinstance(item, list) else [item]
        calls = [ToolCall(self._next_id(), s["tool"], dict(s.get("args", {}))) for s in specs]
        return LLMResponse(tool_calls=calls)

    def generate(self, messages: list[Message], tools: list | None = None) -> LLMResponse:
        self.calls.append({"messages": list(messages), "tools": tools})
        self.input_tokens += sum(approx_tokens(m.content) for m in messages)

        if self._script:
            response = self._script.pop(0)
        else:
            last = next((m.content for m in reversed(messages) if m.content), "") or ""
            response = next(
                (r for pattern, r in self._rules if pattern.search(last)), self._default
            )
            if response is None:
                raise MockLLMExhausted(
                    "El guion del MockLLM se agotó: tu código lo llamó más veces de las previstas."
                )

        self.output_tokens += approx_tokens(response.text) + sum(
            approx_tokens(json.dumps(c.arguments)) for c in response.tool_calls
        )
        return response

    @property
    def cost_usd(self) -> float:
        return (
            self.input_tokens * self.PRICE_IN_PER_M + self.output_tokens * self.PRICE_OUT_PER_M
        ) / 1_000_000
