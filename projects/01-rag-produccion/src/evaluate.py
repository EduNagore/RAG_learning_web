"""Evaluación sobre un conjunto de oro: recuperación y generación por separado."""

import json
from pathlib import Path


def load_golden(path: str = "data/golden.json") -> list[dict]:
    """Cada elemento: {"question": str, "relevant_ids": [int], "answerable": bool}."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def recall_at_k(retrieved: list[int], relevant: list[int], k: int) -> float:
    """TODO: fracción de `relevant` presente en los k primeros de `retrieved` (1.0 si no hay relevantes)."""
    _ = (retrieved, relevant, k)
    raise NotImplementedError("Implementa recall@k")


def reciprocal_rank(retrieved: list[int], relevant: list[int]) -> float:
    """TODO: 1 / posición del primer relevante, o 0.0 si no aparece."""
    _ = (retrieved, relevant)
    raise NotImplementedError("Implementa el rango recíproco")


if __name__ == "__main__":
    # TODO: ejecuta el sistema sobre cada pregunta, calcula recall@5 y MRR, la tasa de abstención
    # correcta (preguntas sin respuesta) y la validez de las citas. Imprime una tabla y guarda las trazas.
    raise SystemExit("Completa el bucle de evaluación")
