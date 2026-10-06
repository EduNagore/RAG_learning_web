from ragkit.testing import expect_close, expect_equal, expect_raises


def llamada(tool, **args):
    return {"tool": tool, "args": args}


def test_pass_at_k_y_pass_hat_k_basicos(student):
    """Valores calculados a mano con n=5 intentos y c=2 éxitos"""
    expect_close(student.pass_at_k(5, 2, 1), 0.4, what="pass@1")
    expect_close(student.pass_at_k(5, 2, 3), 0.9, what="pass@3 = 1 - C(3,3)/C(5,3)")
    expect_close(student.pass_hat_k(5, 2, 2), 0.1, what="pass^2 = C(2,2)/C(5,2)")
    expect_close(student.pass_hat_k(5, 2, 1), 0.4, what="pass^1 = pass@1")


def test_casos_extremos_de_las_metricas(student):
    """Sin éxitos, todo éxitos y k = n"""
    expect_close(student.pass_at_k(4, 0, 2), 0.0, what="pass@k sin éxitos")
    expect_close(student.pass_hat_k(4, 0, 2), 0.0, what="pass^k sin éxitos")
    expect_close(student.pass_at_k(4, 4, 2), 1.0, what="pass@k con todo éxitos")
    expect_close(student.pass_hat_k(4, 4, 2), 1.0, what="pass^k con todo éxitos")
    expect_close(student.pass_at_k(4, 1, 4), 1.0, what="si n-c < k el resultado es 1")
    expect_close(student.pass_hat_k(4, 3, 4), 0.0, what="si c < k el resultado es 0")


def test_la_fiabilidad_cae_y_la_capacidad_sube_con_k(student):
    """pass@k crece con k; pass^k decrece con k (misma tarea con 3 éxitos de 5)"""
    arriba = [student.pass_at_k(5, 3, k) for k in (1, 2, 3)]
    abajo = [student.pass_hat_k(5, 3, k) for k in (1, 2, 3)]
    expect_equal(arriba == sorted(arriba) and arriba[0] < arriba[-1], True, what="pass@k crece")
    expect_equal(
        abajo == sorted(abajo, reverse=True) and abajo[0] > abajo[-1], True, what="pass^k decrece"
    )


def test_valores_invalidos(student):
    """k fuera de rango o c mayor que n lanzan ValueError"""
    expect_raises(ValueError, student.pass_at_k, 3, 1, 4, what="k > n")
    expect_raises(ValueError, student.pass_hat_k, 3, 1, 0, what="k = 0")
    expect_raises(ValueError, student.pass_at_k, 3, 4, 1, what="c > n")
    expect_raises(ValueError, student.pass_hat_k, 3, -1, 1, what="c < 0")


def test_aggregate_promedia_sobre_tareas(student):
    """Dos tareas: una siempre acierta y otra acierta 2 de 4"""
    runs = {"a": [True, True, True, True], "b": [True, False, True, False]}
    out = student.aggregate(runs, 2)
    expect_close(out["pass_at_1"], (1.0 + 0.5) / 2, what="pass@1 medio")
    expect_close(out["pass_at_k"], (1.0 + (1 - 1 / 6)) / 2, what="pass@2 medio")
    expect_close(out["pass_hat_k"], (1.0 + 1 / 6) / 2, what="pass^2 medio")


def test_grade_trajectory_perfecta_y_con_pasos_extra(student):
    """Todas las esperadas cumplidas en orden; un paso de más baja la precisión pero no el recall"""
    esperado = [llamada("buscar_pedido", id=7), llamada("reembolsar", id=7)]
    pasos = [llamada("buscar_pedido", id=7), llamada("saludar"), llamada("reembolsar", id=7)]
    out = student.grade_trajectory(pasos, esperado)
    expect_equal(out["matched"], 2, what="esperadas cumplidas")
    expect_close(out["recall"], 1.0, what="recall")
    expect_close(out["precision"], 2 / 3, what="precision")
    expect_equal(out["in_order"], True, what="orden")


def test_grade_trajectory_con_argumentos_incorrectos(student):
    """Una llamada con el argumento equivocado no cuenta como cumplida"""
    esperado = [llamada("reembolsar", id=7)]
    out = student.grade_trajectory([llamada("reembolsar", id=8)], esperado)
    expect_equal(out["matched"], 0, what="esperadas cumplidas")
    expect_close(out["recall"], 0.0, what="recall")
    expect_close(out["precision"], 0.0, what="precision")


def test_hidden_argumentos_de_mas_y_cada_paso_se_usa_una_vez(student):
    """Caso adicional: un paso con argumentos extra cumple; un mismo paso no cumple dos esperadas"""
    esperado = [llamada("buscar", q="x"), llamada("buscar", q="x")]
    out = student.grade_trajectory([llamada("buscar", q="x", limite=3)], esperado)
    expect_equal(out["matched"], 1, what="un solo paso solo cumple una esperada")
    expect_close(out["recall"], 0.5, what="recall")
    expect_close(out["precision"], 1.0, what="precision")


def test_hidden_orden_incorrecto(student):
    """Caso adicional: las esperadas se cumplen pero en otro orden"""
    esperado = [llamada("a"), llamada("b")]
    out = student.grade_trajectory([llamada("b"), llamada("a")], esperado)
    expect_equal(out["matched"], 2, what="esperadas cumplidas")
    expect_equal(out["in_order"], False, what="orden")
    expect_equal(
        student.grade_trajectory([llamada("a"), llamada("b")], esperado)["in_order"],
        True,
        what="orden correcto",
    )


def test_hidden_listas_vacias(student):
    """Caso adicional: sin esperadas el recall es 1.0; sin pasos la precisión es 1.0"""
    out = student.grade_trajectory([llamada("a")], [])
    expect_close(out["recall"], 1.0, what="recall sin esperadas")
    expect_close(out["precision"], 0.0, what="precision con pasos y sin aciertos")
    vacio = student.grade_trajectory([], [llamada("a")])
    expect_close(vacio["precision"], 1.0, what="precision sin pasos")
    expect_close(vacio["recall"], 0.0, what="recall sin pasos")
