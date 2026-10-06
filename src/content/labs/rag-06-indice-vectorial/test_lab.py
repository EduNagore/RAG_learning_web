import numpy as np
from ragkit.testing import expect_close, expect_equal, expect_raises, expect_true


def _demo(student):
    index = student.VectorIndex(dim=2)
    index.add("a", [1, 0], {"dep": "envíos", "nivel": "public"})
    index.add("b", [0.9, 0.1], {"dep": "envíos", "nivel": "internal"})
    index.add("c", [0, 1], {"dep": "facturación", "nivel": "public"})
    return index


def test_busqueda_basica_ordenada(student):
    """search devuelve (id, coseno) de mayor a menor similitud"""
    results = _demo(student).search([1, 0], k=3)
    expect_equal([r[0] for r in results], ["a", "b", "c"], what="orden de los ids")
    expect_close(results[0][1], 1.0, what="coseno con el vector idéntico")
    expect_close(results[2][1], 0.0, what="coseno con el vector ortogonal")


def test_k_mayor_que_el_numero_de_entradas(student):
    """Con k mayor que las entradas devuelve todas"""
    expect_equal(len(_demo(student).search([1, 0], k=10)), 3, what="resultados")


def test_filtro_por_igualdad_se_aplica_antes_de_buscar(student):
    """El filtro es un prefiltro: devuelve resultados aunque no estén entre los más cercanos globales"""
    results = _demo(student).search([1, 0], k=1, where={"dep": "facturación"})
    expect_equal([r[0] for r in results], ["c"], what="resultado con filtro")


def test_el_filtro_devuelve_k_resultados_si_hay_suficientes(student):
    """Si hay al menos k entradas válidas, se devuelven exactamente k"""
    index = student.VectorIndex(dim=2)
    for i in range(10):
        # Las 'x' están muy lejos de la consulta y las 'y' muy cerca.
        index.add(f"y{i}", [1, 0.01 * i], {"grupo": "y"})
        index.add(f"x{i}", [0, 1 + 0.01 * i], {"grupo": "x"})
    results = index.search([1, 0], k=5, where={"grupo": "x"})
    expect_equal(len(results), 5, what="número de resultados filtrados")
    expect_true(
        all(r[0].startswith("x") for r in results), "Todos los resultados deben cumplir el filtro."
    )


def test_filtro_con_lista_y_varias_condiciones(student):
    """where admite listas (cualquiera de) y combina condiciones con AND"""
    index = _demo(student)

    def ids(**kw):
        return sorted(r[0] for r in index.search([1, 0], k=5, **kw))

    expect_equal(
        ids(where={"dep": ["envíos", "facturación"]}), ["a", "b", "c"], what="lista de valores"
    )
    expect_equal(ids(where={"dep": "envíos", "nivel": "public"}), ["a"], what="dos condiciones")


def test_add_reemplaza_y_delete_elimina(student):
    """add con un id existente reemplaza; delete elimina y devuelve si existía"""
    index = _demo(student)
    index.add("c", [1, 0], {"dep": "envíos"})
    expect_equal(len(index), 3, what="tamaño tras reemplazar")
    expect_close(dict(index.search([1, 0], k=3))["c"], 1.0, what="coseno del vector reemplazado")
    expect_equal(index.delete("c"), True, what="delete de un id existente")
    expect_equal(index.delete("c"), False, what="delete de un id inexistente")
    expect_equal(len(index), 2, what="tamaño tras borrar")
    expect_true(
        "c" not in [r[0] for r in index.search([1, 0], k=5)], "El id borrado no debe aparecer."
    )


def test_hidden_validaciones(student):
    """Caso adicional: entradas inválidas"""
    index = student.VectorIndex(dim=3)
    expect_raises(ValueError, index.add, "x", [1, 2], what="dimensión incorrecta")
    expect_raises(ValueError, index.add, "x", [0, 0, 0], what="vector cero")


def test_hidden_filtro_sin_coincidencias(student):
    """Caso adicional: filtro que no cumple ninguna entrada"""
    expect_equal(_demo(student).search([1, 0], k=3, where={"dep": "rrhh"}), [], what="resultados")


def test_hidden_normaliza_y_no_modifica_la_consulta(student):
    """Caso adicional: normalización"""
    index = student.VectorIndex(dim=2)
    index.add("corto", [1, 0])
    index.add("largo", [100, 0])
    query = np.array([3.0, 0.0])
    before = query.copy()
    scores = dict(index.search(query, k=2))
    expect_close(scores["corto"], 1.0, what="coseno del vector corto")
    expect_close(scores["largo"], 1.0, what="coseno del vector largo (misma dirección)")
    expect_true(np.array_equal(query, before), "La función ha modificado la consulta.")


def test_hidden_empates_conservan_el_orden_de_insercion(student):
    """Caso adicional: desempate"""
    index = student.VectorIndex(dim=2)
    for id in ["p", "q", "r"]:
        index.add(id, [1, 0])
    expect_equal(
        [r[0] for r in index.search([1, 0], k=3)], ["p", "q", "r"], what="orden con empates"
    )
