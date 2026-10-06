from ragkit.testing import expect_equal, expect_true

P1 = "Los clientes particulares disponen de 14 días."  # 46 caracteres
P2 = "Los clientes empresa disponen de 7 días."  # 40
P3 = "Pasado ese plazo no se aceptan devoluciones."  # 44


def test_texto_corto_se_devuelve_entero(student):
    """Un texto que cabe en max_chars es un único fragmento"""
    expect_equal(student.chunk_recursive("Hola mundo", 50), ["Hola mundo"], what="fragmentos")
    expect_equal(student.chunk_recursive("   ", 50), [], what="texto vacío")


def test_ningun_fragmento_supera_el_maximo(student):
    """Todos los fragmentos miden como mucho max_chars"""
    texto = "\n\n".join([P1, P2, P3] * 3)
    chunks = student.chunk_recursive(texto, 100)
    expect_true(len(chunks) > 1, "El texto no cabe en un fragmento: debería haber varios.")
    for c in chunks:
        expect_true(
            len(c) <= 100, f"Un fragmento mide {len(c)} caracteres y el máximo es 100: {c!r}"
        )


def test_prefiere_los_limites_de_parrafo(student):
    """Fusiona párrafos completos mientras caben, sin partirlos"""
    texto = f"{P2}\n\n{P3}\n\n{P1}"  # 40 + 44 = 86 + 2 de separador
    chunks = student.chunk_recursive(texto, 90)
    expect_equal(chunks, [f"{P2}\n\n{P3}", P1], what="fragmentos")


def test_un_parrafo_largo_se_divide_por_palabras(student):
    """Un párrafo mayor que el máximo se parte entre palabras, sin cortarlas"""
    parrafo = "uno dos tres cuatro cinco seis siete ocho nueve diez"  # 51 caracteres
    chunks = student.chunk_recursive(parrafo, 20)
    expect_true(len(chunks) > 1, "El párrafo no cabe en un fragmento: debería dividirse.")
    for c in chunks:
        expect_true(len(c) <= 20, f"Fragmento demasiado largo: {c!r}")
        expect_true(
            all(w in parrafo.split() for w in c.split()), f"Se ha cortado una palabra: {c!r}"
        )


def test_no_pierde_palabras_ni_cambia_el_orden(student):
    """Conserva todas las palabras en el mismo orden"""
    texto = f"{P1}\n{P2}\n\n{P3}\n\n\n{P1} {P2}"
    chunks = student.chunk_recursive(texto, 60)
    expect_equal(" ".join(chunks).split(), texto.split(), what="palabras")


def test_hidden_palabra_mas_larga_que_el_maximo_se_corta(student):
    """Caso adicional: corte duro"""
    expect_equal(
        student.chunk_recursive("x" * 25, 10), ["x" * 10, "x" * 10, "x" * 5], what="corte duro"
    )


def test_hidden_sin_fragmentos_vacios(student):
    """Caso adicional: líneas en blanco repetidas"""
    texto = f"{P1}\n\n\n\n\n\n{P2}\n\n\n\n{P3}"
    chunks = student.chunk_recursive(texto, 60)
    expect_true(all(c.strip() for c in chunks), "No debe haber fragmentos vacíos.")
    expect_equal(" ".join(chunks).split(), texto.split(), what="palabras")


def test_hidden_respeta_los_separadores_indicados(student):
    """Caso adicional: separadores personalizados"""
    chunks = student.chunk_recursive("aa|bb|cc", 5, separators=("|",))
    expect_equal(chunks, ["aa|bb", "cc"], what="fragmentos")


def test_un_parrafo_demasiado_grande_se_parte_sin_cortar_palabras(student):
    """Una pieza mayor que el máximo dentro de un texto con varios párrafos se trocea con separadores más finos"""
    largo = "uno dos tres cuatro cinco seis siete ocho nueve diez"  # 51 caracteres
    texto = f"Corto.\n\n{largo}\n\nOtro corto."
    chunks = student.chunk_recursive(texto, 28)
    for c in chunks:
        expect_true(len(c) <= 28, f"Fragmento demasiado largo: {c!r}")
        expect_true(all(w in texto.split() for w in c.split()), f"Se ha cortado una palabra: {c!r}")
    expect_equal(" ".join(chunks).split(), texto.split(), what="palabras")


def test_hidden_los_fragmentos_no_arrastran_separadores_sobrantes(student):
    """Caso adicional: fragmentos limpios"""
    texto = f"{P1}\n\n\n\n\n\n{P2}\n\n\n\n{P3}"
    for c in student.chunk_recursive(texto, 60):
        expect_equal(c, c.strip(), what="fragmento sin espacios en los extremos")
        expect_true("\n\n\n" not in c, f"Quedan líneas en blanco de más en {c!r}")
