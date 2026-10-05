from ragkit.testing import expect_equal, expect_true

TRIPLES = [
    ("Envío exprés", "gestionado_por", "Equipo de Envíos"),
    ("Equipo de Envíos", "responsable", "Marta Ruiz"),
    ("Marta Ruiz", "reporta_a", "Dirección de Operaciones"),
    ("Factura", "emitida_por", "Facturación"),
    ("Facturación", "responsable", "Luis Pardo"),
]


def test_normaliza_acentos_mayusculas_y_espacios(student):
    """Las distintas grafías de una entidad se unifican"""
    expect_equal(student.normalize_entity("  Envío   Exprés "), "envio expres", what="normalizada")
    expect_equal(student.normalize_entity("Año Nuevo"), "año nuevo", what="la ñ se conserva")


def test_el_grafo_tiene_una_arista_por_tripleta_y_nodos_normalizados(student):
    """build_graph crea nodos normalizados y aristas con la relación como clave"""
    g = student.build_graph(TRIPLES)
    expect_equal(g.number_of_edges(), 5, what="aristas")
    expect_true(
        "equipo de envios" in g, "El nodo debe estar normalizado (sin acentos, minúsculas)."
    )
    expect_true(
        g.has_edge("envio expres", "equipo de envios", key="gestionado_por"), "Falta una arista."
    )


def test_las_tripletas_repetidas_no_duplican_aristas(student):
    """Una tripleta con otra grafía no añade una arista nueva"""
    g = student.build_graph(
        [("Factura", "emitida_por", "Facturación"), ("FACTURA ", "emitida_por", "facturacion")]
    )
    expect_equal(g.number_of_edges(), 1, what="aristas")
    expect_equal(g.number_of_nodes(), 2, what="nodos")


def test_vecinos_a_distancia_limitada_ignorando_la_direccion(student):
    """neighbors_within recorre en ambos sentidos hasta `hops` saltos"""
    g = student.build_graph(TRIPLES)
    expect_equal(
        student.neighbors_within(g, "Marta Ruiz", 1),
        ["direccion de operaciones", "equipo de envios"],
        what="vecinos a 1 salto",
    )
    expect_equal(
        student.neighbors_within(g, "marta ruiz", 2),
        ["direccion de operaciones", "envio expres", "equipo de envios"],
        what="vecinos a 2 saltos",
    )


def test_multi_hop_sigue_la_cadena_de_relaciones(student):
    """follow_relations responde una pregunta de varios saltos"""
    g = student.build_graph(TRIPLES)
    expect_equal(
        student.follow_relations(g, "Envío exprés", ["gestionado_por", "responsable"]),
        "marta ruiz",
        what="responsable del equipo que gestiona el envío exprés",
    )
    expect_equal(
        student.follow_relations(g, "envio expres", ["gestionado_por", "responsable", "reporta_a"]),
        "direccion de operaciones",
        what="tres saltos",
    )


def test_multi_hop_devuelve_none_si_la_cadena_se_rompe(student):
    """Una relación inexistente o una entidad desconocida da None"""
    g = student.build_graph(TRIPLES)
    expect_equal(
        student.follow_relations(g, "factura", ["responsable"]), None, what="relación ausente"
    )
    expect_equal(
        student.follow_relations(g, "desconocida", ["responsable"]), None, what="entidad ausente"
    )


def test_comunidades_separan_los_grupos_desconectados(student):
    """Dos componentes desconectados dan dos comunidades ordenadas por tamaño"""
    g = student.build_graph(TRIPLES)
    comunidades = student.find_communities(g)
    expect_equal(
        comunidades,
        [
            ["direccion de operaciones", "envio expres", "equipo de envios", "marta ruiz"],
            ["factura", "facturacion", "luis pardo"],
        ],
        what="comunidades",
    )


def test_hidden_entidad_desconocida_y_cero_saltos(student):
    """Caso adicional: sin entidad o con 0 saltos no hay vecinos"""
    g = student.build_graph(TRIPLES)
    expect_equal(student.neighbors_within(g, "no existe", 2), [], what="entidad desconocida")
    expect_equal(student.neighbors_within(g, "factura", 0), [], what="cero saltos")


def test_hidden_varios_destinos_toman_el_primero_alfabetico(student):
    """Caso adicional: ante varios destinos se elige el primero por orden alfabético"""
    g = student.build_graph([("A", "usa", "Zeta"), ("A", "usa", "Beta"), ("Beta", "es", "Fin")])
    expect_equal(student.follow_relations(g, "a", ["usa", "es"]), "fin", what="cadena con elección")
