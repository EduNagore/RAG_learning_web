"""Agentic RAG como grafo de estados: decidir -> recuperar -> evaluar -> (reformular | responder)."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    question: str
    query: str
    evidence: list[dict]
    steps: int
    answer: str
    stop_reason: str


def decide(state: State) -> dict:
    """TODO: pregunta al modelo si hace falta recuperar (saludos y preguntas triviales no lo necesitan)."""
    raise NotImplementedError("Implementa el nodo decidir")


def retrieve(state: State) -> dict:
    """TODO: llama a tu recuperador (por ejemplo el del proyecto 1) con state['query'] y suma un paso."""
    raise NotImplementedError("Implementa el nodo recuperar")


def grade(state: State) -> dict:
    """TODO: valora si la evidencia basta para responder (sí / no / parcial) y guarda el veredicto."""
    raise NotImplementedError("Implementa el nodo evaluar")


def rewrite(state: State) -> dict:
    """TODO: reformula la consulta usando lo que falta según `grade`."""
    raise NotImplementedError("Implementa el nodo reformular")


def generate(state: State) -> dict:
    """TODO: responde con citas, o con NO_LO_SE si la evidencia sigue sin bastar."""
    raise NotImplementedError("Implementa el nodo responder")


def route_after_decide(state: State) -> str:
    """TODO: devuelve 'retrieve' o 'generate' según la decisión."""
    raise NotImplementedError


def route_after_grade(state: State) -> str:
    """TODO: devuelve 'generate' si la evidencia basta o se agotaron los pasos; si no, 'rewrite'.

    Respeta MAX_STEPS y deja en `stop_reason` por qué se paró (guardas del módulo de fiabilidad).
    """
    raise NotImplementedError


def build():
    builder = StateGraph(State)
    for name, fn in [
        ("decide", decide),
        ("retrieve", retrieve),
        ("grade", grade),
        ("rewrite", rewrite),
        ("generate", generate),
    ]:
        builder.add_node(name, fn)
    builder.add_edge(START, "decide")
    builder.add_conditional_edges("decide", route_after_decide, ["retrieve", "generate"])
    builder.add_edge("retrieve", "grade")
    builder.add_conditional_edges("grade", route_after_grade, ["generate", "rewrite"])
    builder.add_edge("rewrite", "retrieve")
    builder.add_edge("generate", END)
    return builder.compile()


if __name__ == "__main__":
    graph = build()
    result = graph.invoke({"question": "¿Cuál es el plazo de devolución?", "steps": 0})
    print(result)
