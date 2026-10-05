from ragkit.testing import expect_close, expect_equal

CONTEXTO = ["El reembolso tarda un máximo de 7 días hábiles desde que el paquete llega."]


def test_split_claims_quita_citas_y_limpia(student):
    """Una afirmación por frase, sin citas ni espacios sobrantes"""
    texto = "El plazo es de 14 días [doc-001]. Se paga por el mismo medio [doc-002, doc-003]. ..."
    expect_equal(
        student.split_claims(texto),
        ["El plazo es de 14 días.", "Se paga por el mismo medio."],
        what="afirmaciones",
    )


def test_la_abstencion_no_tiene_afirmaciones(student):
    """NO_LO_SE no contiene afirmaciones"""
    expect_equal(student.split_claims(" NO_LO_SE "), [], what="afirmaciones de la abstención")


def test_una_afirmacion_con_sus_palabras_en_el_contexto_esta_respaldada(student):
    """Se cuentan las palabras por raíz de 5 letras"""
    expect_equal(student.claim_supported("El paquete llega", CONTEXTO), True, what="respaldada")
    expect_equal(
        student.claim_supported("Es gratis para todos los clientes", CONTEXTO),
        False,
        what="sin respaldo",
    )


def test_un_numero_inventado_invalida_la_afirmacion(student):
    """Todo número de la afirmación debe estar en el contexto, aunque el resto coincida"""
    expect_equal(
        student.claim_supported("El reembolso tarda 7 días hábiles", CONTEXTO), True, what="con 7"
    )
    expect_equal(
        student.claim_supported("El reembolso tarda 3 días hábiles", CONTEXTO), False, what="con 3"
    )


def test_el_umbral_es_configurable_y_inclusivo(student):
    """>= threshold está respaldada"""
    # «tarda», «7» y «días»: sus tres palabras útiles están en el contexto (cobertura 1.0)
    expect_equal(student.claim_supported("tarda 7 días", CONTEXTO, threshold=1.0), True, what="1.0")
    # «tarda» y «pago»: solo una de las dos está en el contexto (cobertura 0.5)
    expect_equal(student.claim_supported("tarda pago", CONTEXTO, threshold=0.5), True, what="0.5")
    expect_equal(student.claim_supported("tarda pago", CONTEXTO, threshold=0.51), False, what="0.51")


def test_faithfulness_cuenta_las_afirmaciones_respaldadas(student):
    """score = respaldadas / total y detalle por afirmación"""
    out = student.faithfulness(
        "El reembolso tarda 7 días hábiles [doc-002]. Es gratis para todos.", CONTEXTO
    )
    expect_close(out["score"], 0.5, what="score")
    expect_equal(
        out["claims"],
        [("El reembolso tarda 7 días hábiles.", True), ("Es gratis para todos.", False)],
        what="detalle",
    )


def test_hidden_faithfulness_de_una_abstencion_es_none(student):
    """Caso adicional: sin afirmaciones el score es None"""
    out = student.faithfulness("NO_LO_SE", CONTEXTO)
    expect_equal(out["score"], None, what="score")
    expect_equal(out["claims"], [], what="afirmaciones")


def test_hidden_context_recall(student):
    """Caso adicional: qué parte de la referencia cubre el contexto recuperado"""
    referencia = "El reembolso tarda 7 días. Se paga en euros."
    expect_close(student.context_recall(referencia, CONTEXTO), 0.5, what="recall del contexto")
    expect_equal(student.context_recall("NO_LO_SE", CONTEXTO), None, what="referencia vacía")
    expect_close(
        student.context_recall("tarda pago", CONTEXTO, threshold=0.5), 1.0, what="con umbral 0.5"
    )
    expect_equal(
        student.claim_supported("el de la", CONTEXTO), False, what="solo palabras vacías"
    )
