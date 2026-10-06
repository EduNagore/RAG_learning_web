from ragkit.data import load_corpus
from ragkit.testing import expect_equal, expect_true

DOCS = [
    {"id": "d1", "text": "Alfa uno. Alfa dos. Alfa tres."},
    {"id": "d2", "text": "Beta uno. Beta dos."},
]
POR_ID = {d["id"]: d for d in DOCS}


def solapamiento(query, texto):
    return len(set(query.lower().split()) & set(texto.lower().replace(".", "").split()))


def test_build_children_crea_un_hijo_por_frase(student):
    """build_children genera child_id, parent_id, pos y text"""
    hijos = student.build_children(DOCS)
    expect_equal(len(hijos), 5, what="número de hijos")
    expect_equal(
        hijos[1],
        {"child_id": "d1#1", "parent_id": "d1", "pos": 1, "text": "Alfa dos."},
        what="segundo hijo",
    )
    expect_equal(hijos[3]["child_id"], "d2#0", what="la posición se reinicia en cada documento")


def test_to_parents_no_repite_padres(student):
    """Varios hijos del mismo padre dan un solo padre"""
    hijos = student.build_children(DOCS)
    out = student.to_parents(["d1#2", "d1#0", "d2#1"], hijos, POR_ID)
    expect_equal([p["id"] for p in out], ["d1", "d2"], what="padres sin repetir")
    expect_equal(out[0]["text"], DOCS[0]["text"], what="texto del padre")


def test_to_parents_respeta_el_orden_de_primera_aparicion(student):
    """El primer hijo recuperado decide el orden de los padres"""
    hijos = student.build_children(DOCS)
    out = student.to_parents(["d2#0", "d1#1", "d2#1"], hijos, POR_ID)
    expect_equal([p["id"] for p in out], ["d2", "d1"], what="orden")


def test_to_parents_recorta_con_max_parents(student):
    """max_parents limita el número de padres entregados"""
    hijos = student.build_children(DOCS)
    out = student.to_parents(["d1#0", "d2#0"], hijos, POR_ID, max_parents=1)
    expect_equal([p["id"] for p in out], ["d1"], what="con max_parents=1")


def test_small_to_big_entrega_el_padre_del_mejor_hijo(student):
    """La búsqueda con hijos devuelve el documento completo"""
    hijos = student.build_children(DOCS)
    out = student.small_to_big_search("beta dos", hijos, solapamiento, POR_ID, top_k_children=1)
    expect_equal([p["id"] for p in out], ["d2"], what="padre entregado")
    expect_equal(out[0]["text"], "Beta uno. Beta dos.", what="se entrega el documento entero")


def test_small_to_big_descarta_puntuaciones_nulas(student):
    """Los hijos con puntuación 0 no se devuelven aunque haya hueco"""
    hijos = student.build_children(DOCS)
    out = student.small_to_big_search("alfa", hijos, solapamiento, POR_ID, top_k_children=5)
    expect_equal([p["id"] for p in out], ["d1"], what="solo el documento con coincidencias")


def test_hidden_varios_hijos_del_mismo_padre_cuentan_una_vez(student):
    """Caso adicional: tres hijos del mismo padre entregan un único padre"""
    hijos = student.build_children(DOCS)
    out = student.small_to_big_search("alfa", hijos, solapamiento, POR_ID, top_k_children=3)
    expect_equal(len(out), 1, what="número de padres")


def test_hidden_ids_desconocidos_y_corpus_real(student):
    """Caso adicional: ids desconocidos se ignoran y funciona con el corpus de Nimbus"""
    hijos = student.build_children(DOCS)
    expect_equal(student.to_parents(["x#9"], hijos, POR_ID), [], what="id desconocido")
    corpus = load_corpus()
    todos = student.build_children(corpus)
    expect_true(len(todos) > len(corpus), "Cada documento de Nimbus tiene varias frases.")
    expect_equal(todos[0]["parent_id"], corpus[0]["id"], what="primer padre")
