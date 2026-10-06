from ragkit.llm import approx_tokens


def refine(generate, evaluate, task, max_iters=3, target=0.9, patience=None, budget_tokens=None):
    """Bucle evaluador-optimizador.

    generate(task, feedback) -> borrador (feedback es None en la primera iteración).
    evaluate(borrador) -> (puntuación, feedback).

    En cada iteración: genera, evalúa, registra {"iteration", "score"} en `history`, acumula los
    tokens aproximados (approx_tokens del borrador + del feedback) y conserva el mejor borrador
    (el primero que alcance la mejor puntuación). Después comprueba, por este orden, si debe parar:
      - score >= target                                   -> stopped = "target"
      - patience no es None y llevamos `patience`
        iteraciones seguidas sin mejorar la mejor puntuación -> stopped = "no_improvement"
      - budget_tokens no es None y tokens >= budget_tokens -> stopped = "budget"
    Si completa max_iters iteraciones sin parar antes: stopped = "max_iters".

    El feedback de una iteración es el que recibe `generate` en la siguiente.
    Devuelve {"best", "score", "iterations", "history", "stopped", "tokens"}.
    """
    # TODO
    raise NotImplementedError("Completa refine")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    borradores = iter(["corto", "algo más largo", "un borrador bastante más largo y completo"])
    try:
        salida = refine(
            generate=lambda tarea, feedback: next(borradores),
            evaluate=lambda d: (min(1.0, len(d) / 40), "alarga el texto"),
            task="Describe el reembolso",
        )
        print(salida["stopped"], salida["iterations"], round(salida["score"], 2))
    except NotImplementedError as e:
        print("Aún por completar:", e)
