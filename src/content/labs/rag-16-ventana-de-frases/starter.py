def window_ranges(positions, n_sentences, w):
    """Intervalos (inicio, fin exclusivo) de las ventanas, ordenados y fusionados.

    - Cada acierto en p produce (max(0, p - w), min(n_sentences, p + w + 1)).
    - Los intervalos que se solapan o son contiguos (inicio <= fin anterior) se unen.
    - Sin posiciones devuelve [].
    - Las posiciones fuera de 0..n_sentences-1 se ignoran.
    """
    # TODO
    raise NotImplementedError("Completa window_ranges")


def sentence_window_context(sentences_by_doc, hits, w=1):
    """Bloques {"doc": id, "text": texto} con las ventanas de cada documento, fusionadas.

    sentences_by_doc: dict id -> lista de frases.
    hits: lista de (id, posición) en orden de relevancia.
    - Los documentos salen en el orden de su primer acierto.
    - Dentro de un documento, los bloques van por posición; el texto une las frases con un espacio.
    - Los documentos desconocidos se ignoran.
    """
    # TODO
    raise NotImplementedError("Completa sentence_window_context")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    try:
        print(window_ranges([2, 4, 9], n_sentences=12, w=1))  # [(1, 6), (8, 11)]
    except NotImplementedError as e:
        print("Aún por completar:", e)
