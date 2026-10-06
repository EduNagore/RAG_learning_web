from math import comb


def pass_at_k(n, c, k):
    """Probabilidad de que AL MENOS 1 de k intentos acierte.

    Se han hecho n intentos de una tarea y c acertaron; se eligen k al azar sin reemplazo.
    Fórmula: 1 - C(n-c, k) / C(n, k). Si n - c < k, el resultado es 1.0.
    Lanza ValueError si no se cumple 1 <= k <= n o 0 <= c <= n.
    """
    # TODO
    raise NotImplementedError("Completa pass_at_k")


def pass_hat_k(n, c, k):
    """Probabilidad de que los k intentos acierten TODOS (la métrica pass^k de τ-bench).

    Fórmula: C(c, k) / C(n, k). Mismas validaciones que pass_at_k.
    """
    # TODO
    raise NotImplementedError("Completa pass_hat_k")


def aggregate(runs, k):
    """Medias sobre tareas. runs: dict tarea -> lista de booleanos (un intento cada uno).

    Devuelve {"pass_at_1": ..., "pass_at_k": ..., "pass_hat_k": ...} con la media de cada
    métrica sobre todas las tareas (n = nº de intentos de cada tarea, c = nº de éxitos).
    """
    # TODO
    raise NotImplementedError("Completa aggregate")


def grade_trajectory(steps, expected):
    """Evalúa una trayectoria (lista de llamadas a herramientas) frente a las esperadas.

    steps y expected son listas de {"tool": nombre, "args": {...}}.
    Un paso CUMPLE una llamada esperada si la herramienta coincide y todos los argumentos
    esperados están en el paso con el mismo valor (el paso puede traer argumentos de más).
    Cada llamada esperada, en orden, consume el PRIMER paso aún no usado que la cumpla.
    Devuelve {"matched": nº de esperadas cumplidas,
              "recall": matched / len(expected)  (1.0 si no se esperaba nada),
              "precision": matched / len(steps)  (1.0 si no hay pasos),
              "in_order": True si los pasos que cumplieron las esperadas aparecen en el mismo
                          orden que en `expected`}.
    """
    # TODO
    raise NotImplementedError("Completa grade_trajectory")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    try:
        print(round(pass_at_k(5, 2, 3), 2), round(pass_hat_k(5, 2, 2), 2))
    except NotImplementedError as e:
        print("Aún por completar:", e)
