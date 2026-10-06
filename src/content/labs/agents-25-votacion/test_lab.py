from ragkit.testing import expect_close, expect_equal


def test_la_mayoria_gana_y_se_normaliza(student):
    """Se comparan las respuestas normalizadas (espacios y mayúsculas)"""
    ganador, conteos = student.majority_vote(["42", " 42", "41", "42 "])
    expect_equal(ganador, "42", what="ganador")
    expect_equal(conteos, {"42": 3, "41": 1}, what="conteos")


def test_empate_gana_la_primera_aparicion(student):
    """Ante un empate gana la respuesta que apareció antes"""
    ganador, _ = student.majority_vote(["b", "a", "a", "b"])
    expect_equal(ganador, "b", what="ganador del empate")


def test_devuelve_el_texto_original_del_ganador(student):
    """El ganador es el texto de su primera aparición, no el normalizado"""
    ganador, _ = student.majority_vote(["Madrid", "madrid", "Sevilla"])
    expect_equal(ganador, "Madrid", what="texto original")


def test_sin_respuestas(student):
    """Una lista vacía no tiene ganador"""
    expect_equal(student.majority_vote([]), (None, {}), what="sin respuestas")
    expect_equal(student.agreement([]), 0.0, what="acuerdo sin respuestas")


def test_el_acuerdo_es_la_fraccion_de_votos_del_ganador(student):
    """agreement = votos del ganador / total"""
    expect_close(student.agreement(["a", "a", "a", "b"]), 0.75, what="acuerdo")
    expect_close(student.agreement(["a", "b", "c"]), 1 / 3, what="acuerdo en empate")


def test_extract_last_number(student):
    """Último número, con la coma decimal convertida en punto"""
    expect_equal(student.extract_last_number("Total: 5,5 euros"), "5.5", what="decimal con coma")
    expect_equal(student.extract_last_number("3 más 4 son 7."), "7", what="último entero")
    expect_equal(student.extract_last_number("sin números"), None, what="sin números")


def test_sample_and_vote_con_extraccion(student):
    """Se generan n muestras, se extrae el número final y se vota"""
    muestras = [
        "razono... total 12",
        "otro camino: 12",
        "me equivoco: 13",
        "resultado 12",
        "creo 12",
    ]
    out = student.sample_and_vote(lambda i: muestras[i], n=5, extract=student.extract_last_number)
    expect_equal(out["answer"], "12", what="respuesta")
    expect_close(out["agreement"], 0.8, what="acuerdo")
    expect_equal(out["votes"], {"12": 4, "13": 1}, what="votos")


def test_hidden_abstencion_si_el_acuerdo_es_bajo(student):
    """Caso adicional: con acuerdo menor que min_agreement la respuesta es None"""
    out = student.sample_and_vote(lambda i: ["a", "b", "c"][i], n=3, min_agreement=0.5)
    expect_equal(out["answer"], None, what="se abstiene")
    expect_close(out["agreement"], 1 / 3, what="acuerdo")
    abierto = student.sample_and_vote(lambda i: ["a", "a", "c"][i], n=3, min_agreement=0.5)
    expect_equal(abierto["answer"], "a", what="supera el umbral")
    justo = student.sample_and_vote(lambda i: ["a", "a", "c", "d"][i], n=4, min_agreement=0.5)
    expect_equal(justo["answer"], "a", what="acuerdo justo en el umbral")


def test_hidden_las_extracciones_none_se_descartan(student):
    """Caso adicional: una muestra sin número no cuenta como voto ni en el acuerdo"""
    muestras = ["total 7", "no sé", "total 7"]
    out = student.sample_and_vote(lambda i: muestras[i], n=3, extract=student.extract_last_number)
    expect_equal(out["answer"], "7", what="respuesta")
    expect_close(out["agreement"], 1.0, what="acuerdo sobre las válidas")
