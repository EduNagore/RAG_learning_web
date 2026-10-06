from ragkit.testing import expect_close, expect_equal


def secuencia(*valores):
    it = iter(valores)
    return lambda *args: next(it)


def evaluador(puntuaciones):
    """Devuelve una función evaluate que da puntuaciones fijas y feedback 'f<n>'."""
    estado = {"n": 0}

    def evaluate(borrador):
        puntuacion = puntuaciones[estado["n"]]
        estado["n"] += 1
        return puntuacion, f"f{estado['n']}"

    return evaluate


def test_para_al_alcanzar_el_objetivo(student):
    """Termina con stopped='target' en la primera iteración que supera target"""
    out = student.refine(
        secuencia("a", "b", "c"), evaluador([0.3, 0.95, 0.99]), "t", max_iters=5, target=0.9
    )
    expect_equal(out["stopped"], "target", what="motivo")
    expect_equal(out["iterations"], 2, what="iteraciones")
    expect_equal(out["best"], "b", what="mejor borrador")
    expect_close(out["score"], 0.95, what="puntuación")
    expect_equal(
        out["history"],
        [{"iteration": 1, "score": 0.3}, {"iteration": 2, "score": 0.95}],
        what="historial",
    )


def test_agota_las_iteraciones_y_devuelve_el_mejor(student):
    """Con stopped='max_iters' se devuelve el mejor borrador, no el último"""
    out = student.refine(
        secuencia("a", "b", "c"), evaluador([0.5, 0.7, 0.6]), "t", max_iters=3, target=0.9
    )
    expect_equal(out["stopped"], "max_iters", what="motivo")
    expect_equal(out["best"], "b", what="el mejor, no el último")
    expect_equal(out["iterations"], 3, what="iteraciones")


def test_el_feedback_de_una_iteracion_llega_a_la_siguiente(student):
    """generate recibe None la primera vez y el feedback anterior después"""
    recibido = []

    def generate(task, feedback):
        recibido.append(feedback)
        return "borrador"

    student.refine(generate, evaluador([0.1, 0.2, 0.3]), "t", max_iters=3, target=0.9)
    expect_equal(recibido, [None, "f1", "f2"], what="feedback recibido")


def test_si_hay_empate_se_conserva_el_primero(student):
    """Una puntuación igual a la mejor no sustituye al borrador anterior"""
    out = student.refine(
        secuencia("primero", "segundo"), evaluador([0.5, 0.5]), "t", max_iters=2, target=0.9
    )
    expect_equal(out["best"], "primero", what="empate")


def test_para_por_falta_de_mejora(student):
    """Con patience=2 se detiene tras dos iteraciones seguidas sin mejorar la mejor puntuación"""
    out = student.refine(
        secuencia("a", "b", "c", "d"),
        evaluador([0.6, 0.5, 0.55, 0.9]),
        "t",
        max_iters=4,
        target=0.9,
        patience=2,
    )
    expect_equal(out["stopped"], "no_improvement", what="motivo")
    expect_equal(out["iterations"], 3, what="iteraciones")
    expect_equal(out["best"], "a", what="mejor")


def test_para_por_presupuesto_de_tokens(student):
    """Se detiene cuando los tokens acumulados alcanzan el presupuesto"""
    out = student.refine(
        lambda t, f: "x" * 40,  # 10 tokens
        evaluador([0.1, 0.1, 0.1, 0.1]),
        "t",
        max_iters=4,
        target=0.9,
        budget_tokens=25,
    )
    # cada iteración suma 10 (borrador) + 1 ("f1": 2 caracteres) = 11 tokens
    expect_equal(out["stopped"], "budget", what="motivo")
    expect_equal(out["iterations"], 3, what="iteraciones")
    expect_equal(out["tokens"], 33, what="tokens acumulados")


def test_los_limites_son_inclusivos(student):
    """score == target, tokens == budget_tokens y mejora que reinicia la paciencia"""
    out = student.refine(secuencia("a"), evaluador([0.9]), "t", max_iters=3, target=0.9)
    expect_equal((out["stopped"], out["iterations"]), ("target", 1), what="score == target")

    out = student.refine(
        lambda t, f: "x" * 40,
        evaluador([0.1, 0.1, 0.1, 0.1]),
        "t",
        max_iters=4,
        target=0.9,
        budget_tokens=33,
    )
    expect_equal((out["stopped"], out["iterations"]), ("budget", 3), what="tokens == presupuesto")

    out = student.refine(
        secuencia("a", "b", "c", "d"),
        evaluador([0.2, 0.1, 0.3, 0.1]),
        "t",
        max_iters=4,
        target=0.9,
        patience=2,
    )
    expect_equal(
        (out["stopped"], out["iterations"]), ("max_iters", 4), what="mejorar reinicia la paciencia"
    )


def test_hidden_el_objetivo_tiene_prioridad_sobre_el_presupuesto(student):
    """Caso adicional: si se alcanza el objetivo y el presupuesto a la vez, el motivo es target"""
    out = student.refine(
        lambda t, f: "x" * 40, evaluador([0.95]), "t", max_iters=3, target=0.9, budget_tokens=1
    )
    expect_equal(out["stopped"], "target", what="motivo")


def test_hidden_con_patience_uno_una_mejora_reinicia_la_cuenta(student):
    """Caso adicional: mejorar reinicia el contador de iteraciones sin mejora"""
    out = student.refine(
        secuencia("a", "b", "c"),
        evaluador([0.2, 0.3, 0.4]),
        "t",
        max_iters=3,
        target=0.9,
        patience=1,
    )
    expect_equal(out["stopped"], "max_iters", what="motivo")
    expect_equal(out["iterations"], 3, what="iteraciones")
