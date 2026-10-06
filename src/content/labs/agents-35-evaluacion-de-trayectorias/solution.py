from math import comb


def _comprobar(n, c, k):
    if not 1 <= k <= n or not 0 <= c <= n:
        raise ValueError(f"valores inválidos: n={n}, c={c}, k={k}")


def pass_at_k(n, c, k):
    """Probabilidad de que al menos 1 de k intentos (elegidos de n, con c éxitos) acierte."""
    _comprobar(n, c, k)
    if n - c < k:
        return 1.0
    return 1 - comb(n - c, k) / comb(n, k)


def pass_hat_k(n, c, k):
    """Probabilidad de que los k intentos (elegidos de n, con c éxitos) acierten TODOS."""
    _comprobar(n, c, k)
    return comb(c, k) / comb(n, k)


def aggregate(runs, k):
    """Métricas medias sobre tareas. runs: dict tarea -> lista de booleanos (un intento cada uno)."""
    resumen = {"pass_at_1": 0.0, "pass_at_k": 0.0, "pass_hat_k": 0.0}
    for trials in runs.values():
        n, c = len(trials), sum(trials)
        resumen["pass_at_1"] += pass_at_k(n, c, 1)
        resumen["pass_at_k"] += pass_at_k(n, c, k)
        resumen["pass_hat_k"] += pass_hat_k(n, c, k)
    total = len(runs)
    return {nombre: valor / total for nombre, valor in resumen.items()}


def _coincide(paso, esperado):
    return paso["tool"] == esperado["tool"] and all(
        paso.get("args", {}).get(clave) == valor
        for clave, valor in esperado.get("args", {}).items()
    )


def grade_trajectory(steps, expected):
    """Evalúa una trayectoria frente a las llamadas esperadas."""
    usados = set()
    indices = []
    for esperado in expected:
        for i, paso in enumerate(steps):
            if i not in usados and _coincide(paso, esperado):
                usados.add(i)
                indices.append(i)
                break
    matched = len(indices)
    return {
        "matched": matched,
        "recall": matched / len(expected) if expected else 1.0,
        "precision": matched / len(steps) if steps else 1.0,
        "in_order": indices == sorted(indices),
    }
