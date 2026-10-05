def window_ranges(positions, n_sentences, w):
    """Intervalos (inicio, fin exclusivo) de las ventanas, ordenados y fusionados."""
    ranges = sorted(
        (max(0, p - w), min(n_sentences, p + w + 1)) for p in positions if 0 <= p < n_sentences
    )
    merged = []
    for start, end in ranges:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def sentence_window_context(sentences_by_doc, hits, w=1):
    """Bloques {"doc", "text"} con las ventanas de cada documento, fusionadas."""
    positions_by_doc = {}
    for doc_id, pos in hits:
        if doc_id in sentences_by_doc:
            positions_by_doc.setdefault(doc_id, []).append(pos)

    blocks = []
    for doc_id, positions in positions_by_doc.items():
        sentences = sentences_by_doc[doc_id]
        for start, end in window_ranges(positions, len(sentences), w):
            blocks.append({"doc": doc_id, "text": " ".join(sentences[start:end])})
    return blocks


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    print(window_ranges([2, 4, 9], n_sentences=12, w=1))  # [(1, 6), (8, 11)]
