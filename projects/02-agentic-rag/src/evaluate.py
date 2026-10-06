"""Compara el agentic RAG con un RAG de un paso sobre el mismo conjunto de oro."""


def compare(golden: list[dict]) -> dict:
    """TODO: para cada pregunta ejecuta (a) RAG de un paso y (b) el grafo; devuelve por sistema:
    exactitud, pasos medios, tokens medios y tasa de paradas por guarda.

    Pregunta clave del proyecto: ¿en qué preguntas gana el agente y cuánto cuesta esa ganancia?
    """
    raise NotImplementedError("Implementa la comparación")
