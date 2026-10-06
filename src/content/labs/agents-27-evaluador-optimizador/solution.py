from ragkit.llm import approx_tokens


def refine(generate, evaluate, task, max_iters=3, target=0.9, patience=None, budget_tokens=None):
    """Bucle evaluador-optimizador.

    generate(task, feedback) -> borrador (feedback es None en la primera iteración).
    evaluate(borrador) -> (puntuación, feedback).

    En cada iteración: se genera, se evalúa, se registra {"iteration", "score"} y se conserva el
    mejor borrador (el primero que alcanza la mejor puntuación). Se detiene, por este orden, si:
      - score >= target                         -> "target"
      - patience no es None y llevamos `patience` iteraciones seguidas sin mejorar el mejor
        score                                   -> "no_improvement"
      - budget_tokens no es None y los tokens aproximados (borradores + feedback) acumulados
        son >= budget_tokens                    -> "budget"
    Si se completan max_iters iteraciones sin parar antes: "max_iters".

    Devuelve {"best", "score", "iterations", "history", "stopped", "tokens"}.
    """
    history = []
    best, best_score = None, float("-inf")
    feedback = None
    stale = 0
    tokens = 0
    stopped = "max_iters"
    for iteration in range(1, max_iters + 1):
        draft = generate(task, feedback)
        score, feedback = evaluate(draft)
        tokens += approx_tokens(draft) + approx_tokens(feedback)
        history.append({"iteration": iteration, "score": score})
        if score > best_score:
            best, best_score, stale = draft, score, 0
        else:
            stale += 1
        if score >= target:
            stopped = "target"
            break
        if patience is not None and stale >= patience:
            stopped = "no_improvement"
            break
        if budget_tokens is not None and tokens >= budget_tokens:
            stopped = "budget"
            break
    return {
        "best": best,
        "score": best_score,
        "iterations": len(history),
        "history": history,
        "stopped": stopped,
        "tokens": tokens,
    }


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    borradores = iter(["corto", "algo más largo", "un borrador bastante más largo y completo"])
    salida = refine(
        generate=lambda tarea, feedback: next(borradores),
        evaluate=lambda d: (min(1.0, len(d) / 40), "alarga el texto"),
        task="Describe el reembolso",
    )
    print(salida["stopped"], salida["iterations"], round(salida["score"], 2))
