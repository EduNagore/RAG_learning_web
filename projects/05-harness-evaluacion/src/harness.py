"""Harness: ejecuta cada tarea varias veces en un entorno limpio y calcula las métricas."""

import json
from collections.abc import Callable
from pathlib import Path


def pass_at_k(n: int, c: int, k: int) -> float:
    """TODO: 1 - C(n-c, k) / C(n, k); valida 1 <= k <= n y 0 <= c <= n (pista: math.comb)."""
    raise NotImplementedError("Implementa pass@k")


def pass_hat_k(n: int, c: int, k: int) -> float:
    """TODO: C(c, k) / C(n, k) con las mismas validaciones."""
    raise NotImplementedError("Implementa pass^k")


def new_environment() -> dict:
    """Entorno NUEVO por intento: si se comparte estado, las métricas se contaminan."""
    return {"refunds": [], "account_active": True, "calls": []}


def run_task(agent: Callable[[str, dict], str], task: dict, attempts: int) -> list[dict]:
    """TODO: por cada intento crea un entorno limpio, ejecuta `agent(task["input"], env)`,
    comprueba el RESULTADO en el entorno (no solo el mensaje) y las herramientas prohibidas,
    y guarda la traza (env["calls"]) para poder leer los fallos."""
    raise NotImplementedError("Implementa run_task")


def report(results: dict[str, list[dict]], k: int) -> str:
    """TODO: tabla por tarea con n, c, pass@1, pass@k y pass^k, y las medias."""
    raise NotImplementedError("Implementa el informe")


def load_tasks(path: str = "data/tasks.json") -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
