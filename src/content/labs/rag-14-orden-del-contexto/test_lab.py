from ragkit.testing import expect_equal, expect_raises, expect_true


def test_edges_order_con_cinco_elementos(student):
    """El mejor al principio, el segundo al final, los peores en medio"""
    expect_equal(
        student.edges_order(["d1", "d2", "d3", "d4", "d5"]),
        ["d1", "d3", "d5", "d4", "d2"],
        what="orden en extremos",
    )


def test_edges_order_con_seis_y_con_pocos_elementos(student):
    """Casos con número par y con listas muy cortas"""
    expect_equal(
        student.edges_order(["1", "2", "3", "4", "5", "6"]),
        ["1", "3", "5", "6", "4", "2"],
        what="seis elementos",
    )
    expect_equal(student.edges_order(["a"]), ["a"], what="un elemento")
    expect_equal(student.edges_order(["a", "b"]), ["a", "b"], what="dos elementos")
    expect_equal(student.edges_order([]), [], what="lista vacía")


def test_edges_order_no_modifica_la_entrada(student):
    """La lista original no cambia"""
    original = ["a", "b", "c", "d"]
    student.edges_order(original)
    expect_equal(original, ["a", "b", "c", "d"], what="lista original")


def test_insert_evidence_en_cada_posicion(student):
    """La evidencia se inserta donde se pide y devuelve una copia"""
    base = ["x", "y", "z"]
    expect_equal(student.insert_evidence(base, "E", 0), ["E", "x", "y", "z"], what="inicio")
    expect_equal(student.insert_evidence(base, "E", 2), ["x", "y", "E", "z"], what="medio")
    expect_equal(base, ["x", "y", "z"], what="la lista original no cambia")


def test_insert_evidence_acota_la_posicion(student):
    """Posiciones fuera de rango se acotan"""
    base = ["x", "y"]
    expect_equal(student.insert_evidence(base, "E", -1), ["E", "x", "y"], what="negativa")
    expect_equal(student.insert_evidence(base, "E", 99), ["x", "y", "E"], what="demasiado grande")


def test_fit_to_budget_conserva_los_primeros_que_caben(student):
    """Se acumulan documentos hasta agotar el presupuesto"""
    docs = [
        {"id": "a", "text": "x" * 40},  # 10 tokens
        {"id": "b", "text": "x" * 40},  # 10 tokens
        {"id": "c", "text": "x" * 40},  # 10 tokens
    ]
    expect_equal(student.fit_to_budget(docs, 25), ["a", "b"], what="presupuesto de 25")
    expect_equal(student.fit_to_budget(docs, 30), ["a", "b", "c"], what="presupuesto de 30")


def test_position_zone_reparte_en_tercios(student):
    """inicio, medio y final según el tercio"""
    orden = ["a", "b", "c", "d", "e", "f"]
    zonas = [student.position_zone(orden, d) for d in orden]
    expect_equal(zonas, ["inicio", "inicio", "medio", "medio", "final", "final"], what="zonas")
    expect_equal(student.position_zone(["solo"], "solo"), "inicio", what="un solo elemento")


def test_hidden_fit_to_budget_salta_los_que_no_caben_y_sigue(student):
    """Caso adicional: un documento grande no impide incluir otros más pequeños después"""
    docs = [
        {"id": "pequeño1", "text": "x" * 40},  # 10
        {"id": "grande", "text": "x" * 400},  # 100
        {"id": "pequeño2", "text": "x" * 40},  # 10
    ]
    expect_equal(student.fit_to_budget(docs, 30), ["pequeño1", "pequeño2"], what="sin el grande")
    expect_equal(student.fit_to_budget(docs, 0), [], what="presupuesto cero")


def test_hidden_position_zone_falla_si_el_documento_no_esta(student):
    """Caso adicional: un id ausente lanza ValueError y el mejor tras edges_order queda al inicio"""
    expect_raises(ValueError, student.position_zone, ["a", "b"], "z", what="id ausente")
    orden = student.edges_order(["m1", "m2", "m3", "m4", "m5", "m6"])
    expect_true(student.position_zone(orden, "m1") == "inicio", "El mejor debe quedar al inicio.")
    expect_true(student.position_zone(orden, "m2") == "final", "El segundo debe quedar al final.")
