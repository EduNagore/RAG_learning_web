"""Un agente de juguete no determinista para probar el harness sin llamar a ningún modelo."""

import random


def make_agent(success_probability: float, seed: int = 0):
    rng = random.Random(seed)

    def agent(task_input: str, env: dict) -> str:
        env["calls"].append({"tool": "buscar_pedido", "args": {"id": 7}})
        if rng.random() < success_probability:
            env["calls"].append({"tool": "reembolsar", "args": {"id": 7}})
            env["refunds"].append(7)
        return "Hecho."  # el mensaje final NO es la evidencia: se mira el entorno

    return agent
