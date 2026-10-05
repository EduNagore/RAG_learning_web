from ragkit.testing import expect_equal, expect_true

DOC = """# Devoluciones

Introducción.

## Plazos

14 días naturales.

## Reembolsos

7 días hábiles."""


def test_secciones_con_ruta_de_titulos(student):
    """Cada sección es un fragmento con su ruta de encabezados"""
    chunks = student.chunk_markdown(DOC)
    expect_equal(
        [(c["path"], c["text"]) for c in chunks],
        [
            ("Devoluciones", "Introducción."),
            ("Devoluciones > Plazos", "14 días naturales."),
            ("Devoluciones > Reembolsos", "7 días hábiles."),
        ],
        what="fragmentos",
    )


def test_headers_es_una_lista(student):
    """headers es la lista de títulos, de mayor a menor nivel"""
    chunk = student.chunk_markdown(DOC)[1]
    expect_equal(chunk["headers"], ["Devoluciones", "Plazos"], what="headers")


def test_texto_antes_del_primer_encabezado(student):
    """El texto previo al primer encabezado tiene ruta vacía"""
    chunks = student.chunk_markdown("Preámbulo suelto.\n\n# Título\n\nCuerpo.")
    expect_equal(chunks[0]["headers"], [], what="headers del preámbulo")
    expect_equal(chunks[0]["path"], "", what="path del preámbulo")
    expect_equal(chunks[0]["text"], "Preámbulo suelto.", what="texto del preámbulo")


def test_un_encabezado_de_nivel_superior_descarta_los_mas_profundos(student):
    """Al subir de nivel se olvidan los títulos más profundos"""
    doc = "# A\n\n## B\n\n### C\n\ntexto c\n\n## D\n\ntexto d\n\n# E\n\ntexto e"
    paths = [c["path"] for c in student.chunk_markdown(doc)]
    expect_equal(paths, ["A > B > C", "A > D", "E"], what="rutas")


def test_las_secciones_vacias_no_generan_fragmento(student):
    """Una sección sin cuerpo no produce ningún fragmento"""
    doc = "# A\n\n## B\n\n## C\n\ntexto c"
    chunks = student.chunk_markdown(doc)
    expect_equal([c["path"] for c in chunks], ["A > C"], what="rutas")


def test_seccion_larga_se_divide_por_parrafos(student):
    """Un cuerpo que supera max_chars se divide por párrafos con la misma ruta"""
    parrafos = [f"Párrafo número {i} con algo de texto." for i in range(6)]
    doc = "# Manual\n\n" + "\n\n".join(parrafos)
    chunks = student.chunk_markdown(doc, max_chars=80)
    expect_true(len(chunks) > 1, "El cuerpo no cabe en 80 caracteres: debería dividirse.")
    for c in chunks:
        expect_equal(c["path"], "Manual", what="ruta de cada trozo")
        expect_true(len(c["text"]) <= 80, f"Fragmento demasiado largo: {c['text']!r}")
    expect_equal(
        " ".join(c["text"] for c in chunks).split(), " ".join(parrafos).split(), what="palabras"
    )


def test_hidden_las_almohadillas_dentro_de_codigo_no_son_encabezados(student):
    """Caso adicional: bloques de código"""
    doc = "# Guía\n\n```python\n# esto es un comentario\nx = 1\n```\n\nFin."
    chunks = student.chunk_markdown(doc)
    expect_equal(len(chunks), 1, what="número de fragmentos")
    expect_true(
        "# esto es un comentario" in chunks[0]["text"],
        "El comentario del código debe quedarse en el texto.",
    )
    expect_equal(chunks[0]["path"], "Guía", what="ruta")


def test_hidden_el_texto_no_incluye_la_linea_del_encabezado(student):
    """Caso adicional: el título no se repite en el cuerpo"""
    chunks = student.chunk_markdown("## Plazos\n\n14 días.")
    expect_equal(chunks[0]["text"], "14 días.", what="texto")


def test_hidden_salto_de_nivel_de_encabezado(student):
    """Caso adicional: de nivel 1 a nivel 3"""
    chunks = student.chunk_markdown("# A\n\n### C\n\ntexto")
    expect_equal(chunks[0]["headers"][-1], "C", what="último título")
    expect_equal(chunks[0]["headers"][0], "A", what="primer título")


def test_hidden_un_parrafo_mayor_que_el_maximo_se_corta(student):
    """Caso adicional: párrafo gigante"""
    doc = "# Datos\n\n" + "x" * 50
    chunks = student.chunk_markdown(doc, max_chars=20)
    expect_equal([len(c["text"]) for c in chunks], [20, 20, 10], what="longitudes")
    expect_equal({c["path"] for c in chunks}, {"Datos"}, what="rutas")
