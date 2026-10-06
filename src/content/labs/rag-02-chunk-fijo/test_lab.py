import itertools

from ragkit.testing import expect_equal, expect_raises, expect_true

DIEZ = "uno dos tres cuatro cinco seis siete ocho nueve diez"


def test_ejemplo_con_solape(student):
    """Trocea en ventanas de 4 palabras con solape de 1"""
    expect_equal(
        student.chunk_fixed(DIEZ, 4, 1),
        ["uno dos tres cuatro", "cuatro cinco seis siete", "siete ocho nueve diez"],
        what="fragmentos",
    )


def test_sin_solape_no_genera_fragmento_vacio(student):
    """Sin solape, 10 palabras en ventanas de 5 dan exactamente 2 fragmentos"""
    expect_equal(
        student.chunk_fixed(DIEZ, 5, 0),
        ["uno dos tres cuatro cinco", "seis siete ocho nueve diez"],
        what="fragmentos",
    )


def test_texto_corto_da_un_solo_fragmento(student):
    """Un texto con menos palabras que el tamaño produce un único fragmento"""
    expect_equal(student.chunk_fixed("hola mundo", 5, 1), ["hola mundo"], what="fragmentos")


def test_texto_vacio(student):
    """Un texto vacío o de solo espacios devuelve una lista vacía"""
    expect_equal(student.chunk_fixed("", 4, 1), [], what="texto vacío")
    expect_equal(student.chunk_fixed("   \n  ", 4, 1), [], what="solo espacios")


def test_parametros_invalidos(student):
    """Lanza ValueError con tamaño no positivo, solape negativo o solape >= tamaño"""
    expect_raises(ValueError, student.chunk_fixed, DIEZ, 4, 4, what="overlap == size")
    expect_raises(ValueError, student.chunk_fixed, DIEZ, 4, 7, what="overlap > size")
    expect_raises(ValueError, student.chunk_fixed, DIEZ, 0, 0, what="size == 0")
    expect_raises(ValueError, student.chunk_fixed, DIEZ, 4, -1, what="overlap negativo")


def test_hidden_el_ultimo_fragmento_no_se_duplica(student):
    """Caso adicional: último fragmento"""
    texto = "a b c d e f g"
    expect_equal(
        student.chunk_fixed(texto, 4, 2),
        ["a b c d", "c d e f", "e f g"],
        what="7 palabras, tamaño 4 y solape 2",
    )


def test_hidden_cubre_todo_el_texto_y_respeta_el_solape(student):
    """Caso adicional: cobertura y solape"""
    words = [f"p{i}" for i in range(23)]
    chunks = student.chunk_fixed(" ".join(words), 6, 2)
    parts = [c.split() for c in chunks]
    expect_true(all(len(p) <= 6 for p in parts), "Ningún fragmento puede superar el tamaño.")
    expect_equal(parts[0][0], "p0", what="primera palabra")
    expect_equal(parts[-1][-1], "p22", what="última palabra")
    for prev, nxt in itertools.pairwise(parts):
        expect_equal(prev[-2:], nxt[:2], what="solape entre fragmentos consecutivos")


def test_hidden_normaliza_espacios_y_saltos_de_linea(student):
    """Caso adicional: espacios en blanco"""
    texto = "uno   dos\n\ntres\tcuatro"
    expect_equal(student.chunk_fixed(texto, 2, 0), ["uno dos", "tres cuatro"], what="fragmentos")
