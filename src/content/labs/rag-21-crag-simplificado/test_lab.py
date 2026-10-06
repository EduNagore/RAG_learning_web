from ragkit.testing import expect_close, expect_equal, expect_true

DOCS_REEMBOLSO = [{"text": "El reembolso se realiza por el mismo medio de pago"}]
DOCS_OTRO_TEMA = [{"text": "El horario del chat de atención es de lunes a viernes"}]


def test_la_cobertura_cuenta_raices_de_cinco_letras(student):
    """coverage compara las raíces de 5 letras de la pregunta con las de los documentos"""
    expect_close(
        student.coverage("¿Cuánto tarda el reembolso del pago?", DOCS_REEMBOLSO),
        0.5,
        what="cobertura",
    )


def test_la_cobertura_tolera_variantes_de_la_misma_palabra(student):
    """«reembolsan» y «reembolso» comparten la raíz «reemb»"""
    expect_close(
        student.coverage("reembolsan pago", DOCS_REEMBOLSO), 1.0, what="cobertura con variante"
    )


def test_la_raiz_tiene_exactamente_cinco_letras(student):
    """Palabras que solo comparten las 4 primeras letras no cuentan como la misma"""
    expect_equal(student.coverage("tarifa", [{"text": "tarima"}]), 0.0, what="solo 4 letras")


def test_los_umbrales_de_crag_answer_se_propagan_al_evaluador(student):
    """Con high=0.5 una cobertura de 0.5 ya es suficiente para responder"""
    out = student.crag_answer(
        "reembolso pago horario envio",
        retrieve=lambda q: DOCS_REEMBOLSO,
        answer_fn=lambda q, docs: "ok",
        rewrite_fn=lambda q: q,
        high=0.5,
    )
    expect_equal(out["action"], "answer", what="acción")
    expect_equal(len(out["trace"]), 1, what="intentos")


def test_cobertura_vacia_o_sin_palabras_utiles(student):
    """Una pregunta sin palabras útiles o sin documentos da 0.0"""
    expect_equal(student.coverage("¿Y el de la?", DOCS_REEMBOLSO), 0.0, what="solo palabras vacías")
    expect_equal(student.coverage("reembolso", []), 0.0, what="sin documentos")


def test_los_tres_veredictos(student):
    """correcto, ambiguo e incorrecto según los umbrales"""
    q = "reembolso pago horario envio"  # 2 de 4 raíces en DOCS_REEMBOLSO = 0.5
    expect_equal(student.evaluate_retrieval(q, DOCS_REEMBOLSO), "ambiguo", what="cobertura 0.5")
    expect_equal(
        student.evaluate_retrieval("reembolso pago", DOCS_REEMBOLSO), "correcto", what="cobertura 1"
    )
    expect_equal(
        student.evaluate_retrieval("tienda fisica valencia", DOCS_REEMBOLSO),
        "incorrecto",
        what="cobertura 0",
    )


def test_los_umbrales_son_configurables_y_el_limite_es_inclusivo(student):
    """>= high es correcto y < low es incorrecto"""
    q = "reembolso pago horario envio"  # cobertura 0.5
    expect_equal(
        student.evaluate_retrieval(q, DOCS_REEMBOLSO, high=0.5), "correcto", what="high=0.5"
    )
    expect_equal(student.evaluate_retrieval(q, DOCS_REEMBOLSO, low=0.5), "ambiguo", what="low=0.5")
    expect_equal(
        student.evaluate_retrieval(q, DOCS_REEMBOLSO, low=0.51), "incorrecto", what="low=0.51"
    )


def test_si_la_recuperacion_es_correcta_responde_sin_reformular(student):
    """Un veredicto correcto responde en el primer intento"""
    llamadas = []
    out = student.crag_answer(
        "reembolso pago",
        retrieve=lambda q: DOCS_REEMBOLSO,
        answer_fn=lambda q, docs: "respuesta",
        rewrite_fn=lambda q: llamadas.append(q) or q,
    )
    expect_equal(out["action"], "answer", what="acción")
    expect_equal(out["answer"], "respuesta", what="respuesta")
    expect_equal(out["trace"], [("reembolso pago", "correcto")], what="traza")
    expect_equal(llamadas, [], what="no debe reformular")


def test_si_es_ambigua_reformula_y_responde(student):
    """Un veredicto ambiguo reformula una vez y reintenta"""
    out = student.crag_answer(
        "reembolso pago horario envio",  # cobertura 0.5: ambigua
        retrieve=lambda q: DOCS_REEMBOLSO,
        answer_fn=lambda q, docs: f"respuesta a {q}",
        rewrite_fn=lambda q: "reembolso pago",
    )
    expect_equal(out["action"], "answer", what="acción")
    expect_equal(out["question"], "reembolso pago", what="pregunta final")
    expect_equal(
        out["answer"], "respuesta a reembolso pago", what="respuesta con la pregunta final"
    )
    expect_equal(len(out["trace"]), 2, what="intentos")
    expect_equal(out["trace"][1], ("reembolso pago", "correcto"), what="segundo intento")


def test_hidden_si_es_incorrecta_se_abstiene_sin_reintentar(student):
    """Caso adicional: incorrecto abstiene de inmediato"""
    llamadas = []
    out = student.crag_answer(
        "tienda fisica valencia",
        retrieve=lambda q: DOCS_REEMBOLSO,
        answer_fn=lambda q, docs: "no debería llamarse",
        rewrite_fn=lambda q: llamadas.append(q) or q,
    )
    expect_equal(out["action"], "abstain", what="acción")
    expect_equal(out["answer"], None, what="respuesta")
    expect_equal(llamadas, [], what="no debe reformular")
    expect_equal(out["trace"], [("tienda fisica valencia", "incorrecto")], what="traza")


def test_hidden_se_agotan_los_reintentos(student):
    """Caso adicional: si sigue ambiguo tras max_retries, se abstiene"""
    n = {"reformulaciones": 0}

    def rewrite(q):
        n["reformulaciones"] += 1
        return q + " mas"

    out = student.crag_answer(
        "reembolso pago horario envio",
        retrieve=lambda q: DOCS_REEMBOLSO,
        answer_fn=lambda q, docs: "x",
        rewrite_fn=rewrite,
        max_retries=2,
    )
    expect_equal(out["action"], "abstain", what="acción")
    expect_equal(n["reformulaciones"], 2, what="reformulaciones")
    expect_equal(out["question"], "reembolso pago horario envio mas mas", what="última pregunta")
    expect_equal(len(out["trace"]), 3, what="intentos")
    expect_true(all(v == "ambiguo" for _, v in out["trace"]), "Todos los intentos fueron ambiguos.")
