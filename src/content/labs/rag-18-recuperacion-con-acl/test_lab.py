from ragkit.data import load_corpus
from ragkit.testing import expect_equal

PUBLICO = {"id": "p", "access": "public", "department": "Envíos"}
INTERNO = {"id": "i", "access": "internal", "department": "Almacén"}
RESTRINGIDO = {"id": "r", "access": "restricted", "department": "Recursos Humanos"}

ANONIMO = {"level": "public", "departments": []}
EMPLEADO = {"level": "internal", "departments": ["Almacén"]}
DIRECTORA_RRHH = {"level": "restricted", "departments": ["Recursos Humanos"]}
DIRECTOR_ENVIOS = {"level": "restricted", "departments": ["Envíos"]}


def solapamiento(query, doc):
    return len(set(query.lower().split()) & set(doc["text"].lower().split()))


def test_cada_nivel_ve_lo_que_le_corresponde(student):
    """public, internal y restricted segun el nivel del usuario"""
    expect_equal(student.can_access(ANONIMO, PUBLICO), True, what="anónimo ve público")
    expect_equal(student.can_access(ANONIMO, INTERNO), False, what="anónimo no ve interno")
    expect_equal(student.can_access(EMPLEADO, INTERNO), True, what="empleado ve interno")
    expect_equal(
        student.can_access(EMPLEADO, RESTRINGIDO), False, what="empleado no ve restringido"
    )


def test_el_restringido_exige_nivel_y_departamento(student):
    """Un restringido requiere nivel restricted Y que el departamento sea uno de los del usuario"""
    expect_equal(
        student.can_access(DIRECTORA_RRHH, RESTRINGIDO), True, what="RRHH ve su restringido"
    )
    expect_equal(
        student.can_access(DIRECTOR_ENVIOS, RESTRINGIDO), False, what="otro departamento no lo ve"
    )
    expect_equal(student.can_access(DIRECTORA_RRHH, INTERNO), True, what="restricted ve interno")


def test_filter_docs_conserva_el_orden(student):
    """filter_docs devuelve los accesibles en el orden original"""
    docs = [RESTRINGIDO, PUBLICO, INTERNO]
    out = student.filter_docs(EMPLEADO, docs)
    expect_equal([d["id"] for d in out], ["p", "i"], what="documentos accesibles")


def test_la_busqueda_filtra_antes_de_puntuar(student):
    """El restringido no aparece aunque sea el que más puntúa, y los huecos los ocupan otros"""
    docs = [
        {
            "id": "r",
            "access": "restricted",
            "department": "Recursos Humanos",
            "text": "salario salario salario",
        },
        {"id": "p1", "access": "public", "department": "Envíos", "text": "salario medio"},
        {"id": "p2", "access": "public", "department": "Envíos", "text": "salario"},
    ]
    sin_permiso = student.acl_search(ANONIMO, "salario", docs, solapamiento, top_k=2)
    expect_equal(sin_permiso, ["p1", "p2"], what="sin permiso, top_k se llena con accesibles")
    con_permiso = student.acl_search(DIRECTORA_RRHH, "salario", docs, solapamiento, top_k=2)
    expect_equal(con_permiso[0], "r", what="con permiso el restringido sí puede ser el primero")


def test_la_busqueda_ignora_puntuaciones_nulas_y_desempata_por_orden(student):
    """Solo cuentan los documentos con puntuación > 0 y el empate respeta el orden de entrada"""
    docs = [
        {"id": "a", "access": "public", "department": "X", "text": "reembolso"},
        {"id": "b", "access": "public", "department": "X", "text": "reembolso"},
        {"id": "c", "access": "public", "department": "X", "text": "otro tema"},
    ]
    expect_equal(
        student.acl_search(ANONIMO, "reembolso", docs, solapamiento, top_k=5),
        ["a", "b"],
        what="resultados",
    )


def test_audit_leaks_detecta_lo_que_no_debe_verse(student):
    """audit_leaks lista los ids no autorizados o inexistentes"""
    por_id = {d["id"]: d for d in (PUBLICO, INTERNO, RESTRINGIDO)}
    out = student.audit_leaks(EMPLEADO, ["p", "r", "i", "fantasma"], por_id)
    expect_equal(out, ["r", "fantasma"], what="fugas")


def test_hidden_nivel_desconocido_se_deniega_y_usuario_sin_nivel_es_publico(student):
    """Caso adicional: acceso desconocido denegado; usuario sin nivel = público"""
    raro = {"id": "x", "access": "secreto", "department": "Legal"}
    expect_equal(
        student.can_access(DIRECTORA_RRHH, raro), False, what="nivel de documento desconocido"
    )
    expect_equal(student.can_access({}, PUBLICO), True, what="usuario sin nivel ve público")
    expect_equal(student.can_access({}, INTERNO), False, what="usuario sin nivel no ve interno")
    expect_equal(
        student.can_access({"level": "restricted"}, RESTRINGIDO), False, what="sin departamentos"
    )


def test_hidden_con_el_corpus_real_el_usuario_publico_nunca_recibe_restringidos(student):
    """Caso adicional: con el corpus de Nimbus, ninguna consulta filtra documentos restringidos"""
    corpus = load_corpus()
    por_id = {d["id"]: d for d in corpus}
    for consulta in ("bandas salariales categoría", "huelga transportistas plan de contingencia"):
        ids = student.acl_search(ANONIMO, consulta, corpus, solapamiento, top_k=10)
        expect_equal(student.audit_leaks(ANONIMO, ids, por_id), [], what=f"fugas en «{consulta}»")
        expect_equal([i for i in ids if por_id[i]["access"] != "public"], [], what="solo públicos")
