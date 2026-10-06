from ragkit.llm import MockLLM
from ragkit.testing import expect_equal, expect_true


def test_parse_variants_limpia_numeracion_y_vinetas(student):
    """parse_variants quita numeración, viñetas y espacios"""
    texto = "1. plazo de reembolso\n2) tiempo de devolución\n- estado del pedido\n  * otra más  "
    expect_equal(
        student.parse_variants(texto, 10),
        ["plazo de reembolso", "tiempo de devolución", "estado del pedido", "otra más"],
        what="variantes limpias",
    )


def test_parse_variants_ignora_vacias_y_respeta_n(student):
    """Se ignoran las líneas vacías y se devuelven como máximo n"""
    texto = "uno\n\n   \ndos\ntres\ncuatro"
    expect_equal(student.parse_variants(texto, 2), ["uno", "dos"], what="con n=2")


def test_parse_variants_quita_duplicados_sin_distinguir_mayusculas(student):
    """Los duplicados (aunque cambien las mayúsculas) se descartan"""
    texto = "1. Plazo de reembolso\n2. plazo de reembolso\n3. otra consulta"
    expect_equal(
        student.parse_variants(texto, 5),
        ["Plazo de reembolso", "otra consulta"],
        what="sin duplicados",
    )


def test_expand_queries_pone_la_original_primero_y_llama_una_vez(student):
    """expand_queries devuelve [original, *variantes] con una sola llamada"""
    llm = MockLLM(script=["1. variante A\n2. variante B"])
    out = student.expand_queries(llm, "¿Cómo sigo mi pedido?", n=2)
    expect_equal(out, ["¿Cómo sigo mi pedido?", "variante A", "variante B"], what="consultas")
    expect_equal(len(llm.calls), 1, what="llamadas al modelo")


def test_expand_queries_incluye_pregunta_y_n_en_el_prompt(student):
    """El mensaje enviado al modelo contiene la pregunta y el número de variantes"""
    llm = MockLLM(script=["x"])
    student.expand_queries(llm, "¿Cómo sigo mi pedido?", n=4)
    contenido = llm.calls[0]["messages"][0].content
    expect_true("¿Cómo sigo mi pedido?" in contenido, "El prompt debe incluir la pregunta.")
    expect_true("4" in contenido, "El prompt debe indicar cuántas reformulaciones pedir.")
    expect_equal(llm.calls[0]["messages"][0].role, "user", what="rol del mensaje")


def test_multi_query_search_fusiona_los_rankings(student):
    """multi_query_search fusiona el ranking de cada consulta con RRF"""
    rankings = {
        "original": ["d1", "d2", "d3"],
        "variante": ["d2", "d4", "d1"],
    }
    llm = MockLLM(script=["variante"])
    out = student.multi_query_search("original", llm, lambda q: rankings[q], n=1, top_k=3)
    expect_equal(out, ["d2", "d1", "d4"], what="top 3 fusionado")


def test_hidden_la_variante_igual_a_la_original_no_se_duplica(student):
    """Caso adicional: una variante idéntica a la pregunta (otras mayúsculas) se descarta"""
    llm = MockLLM(script=["¿CÓMO SIGO MI PEDIDO?\nnueva variante"])
    out = student.expand_queries(llm, "¿Cómo sigo mi pedido?", n=3)
    expect_equal(out, ["¿Cómo sigo mi pedido?", "nueva variante"], what="consultas sin duplicar")


def test_hidden_si_el_modelo_devuelve_basura_queda_la_original(student):
    """Caso adicional: sin variantes útiles, se busca solo con la pregunta original"""
    llm = MockLLM(script=["\n  \n"])
    consultas = []
    out = student.multi_query_search(
        "pregunta", llm, lambda q: consultas.append(q) or ["d1", "d2"], top_k=1
    )
    expect_equal(consultas, ["pregunta"], what="consultas ejecutadas")
    expect_equal(out, ["d1"], what="resultado")
