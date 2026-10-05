from ragkit.testing import expect_equal

FRASES = {
    "d1": ["a0", "a1", "a2", "a3", "a4", "a5", "a6"],
    "d2": ["b0", "b1", "b2"],
}


def test_una_ventana_se_recorta_en_los_bordes(student):
    """Las ventanas no salen del documento"""
    expect_equal(student.window_ranges([0], 7, 1), [(0, 2)], what="ventana en el inicio")
    expect_equal(student.window_ranges([6], 7, 2), [(4, 7)], what="ventana en el final")


def test_las_ventanas_que_se_solapan_se_fusionan(student):
    """Las ventanas solapadas forman un único intervalo"""
    expect_equal(
        student.window_ranges([2, 4, 9], 12, 1), [(1, 6), (8, 11)], what="intervalos fusionados"
    )


def test_las_ventanas_contiguas_tambien_se_fusionan(student):
    """Dos ventanas que se tocan sin solaparse también se unen"""
    expect_equal(student.window_ranges([1, 4], 10, 1), [(0, 6)], what="ventanas contiguas")


def test_posiciones_desordenadas_y_repetidas(student):
    """El orden de entrada no importa y las repeticiones no duplican"""
    expect_equal(
        student.window_ranges([9, 2, 2, 4], 12, 1),
        [(1, 6), (8, 11)],
        what="posiciones desordenadas",
    )
    expect_equal(student.window_ranges([], 5, 1), [], what="sin posiciones")


def test_w_cero_entrega_solo_las_frases_acertadas(student):
    """Con w=0 cada ventana es la propia frase"""
    expect_equal(student.window_ranges([1, 5], 7, 0), [(1, 2), (5, 6)], what="w=0")


def test_contexto_une_las_frases_de_cada_bloque(student):
    """sentence_window_context devuelve bloques de texto contiguos"""
    out = student.sentence_window_context(FRASES, [("d1", 3)], w=1)
    expect_equal(out, [{"doc": "d1", "text": "a2 a3 a4"}], what="bloque único")


def test_contexto_ordena_documentos_por_primer_acierto(student):
    """El documento del acierto más relevante va primero; dentro de él, por posición"""
    hits = [("d2", 1), ("d1", 5), ("d1", 0)]
    out = student.sentence_window_context(FRASES, hits, w=0)
    expect_equal(
        out,
        [
            {"doc": "d2", "text": "b1"},
            {"doc": "d1", "text": "a0"},
            {"doc": "d1", "text": "a5"},
        ],
        what="orden de los bloques",
    )


def test_hidden_fusiona_dentro_del_documento_sin_mezclar_documentos(student):
    """Caso adicional: aciertos cercanos en documentos distintos no se fusionan entre sí"""
    hits = [("d1", 6), ("d2", 0), ("d1", 5)]
    out = student.sentence_window_context(FRASES, hits, w=1)
    expect_equal(
        out,
        [{"doc": "d1", "text": "a4 a5 a6"}, {"doc": "d2", "text": "b0 b1"}],
        what="bloques por documento",
    )


def test_hidden_ignora_documentos_desconocidos_y_posiciones_fuera_de_rango(student):
    """Caso adicional: aciertos inválidos se descartan sin error"""
    out = student.sentence_window_context(FRASES, [("zz", 0), ("d2", 99), ("d2", 2)], w=0)
    expect_equal(out, [{"doc": "d2", "text": "b2"}], what="solo el acierto válido")
    expect_equal(student.window_ranges([-3, 50], 7, 1), [], what="posiciones fuera de rango")
