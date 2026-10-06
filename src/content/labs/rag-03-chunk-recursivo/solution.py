def chunk_recursive(text, max_chars, separators=("\n\n", "\n", " ")):
    """Trocea `text` en fragmentos de como mucho `max_chars` caracteres, respetando la estructura.

    1. Si el texto cabe, devuelve [texto] (vacío -> []).
    2. Si no, divide por el primer separador que aparezca y fusiona las piezas de forma voraz.
    3. Una pieza que por sí sola excede el máximo se trocea recursivamente con los separadores
       que quedan.
    4. Sin separadores, corta a la fuerza cada `max_chars` caracteres.
    Los fragmentos salen en orden, sin vacíos y con longitud <= max_chars.
    """
    text = text.strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    for i, sep in enumerate(separators):
        if sep not in text:
            continue
        remaining = separators[i + 1 :]
        pieces = [p.strip() for p in text.split(sep) if p.strip()]
        chunks = []
        current = ""
        for piece in pieces:
            if len(piece) > max_chars:
                # Pieza demasiado grande: se cierra lo acumulado y se trocea con separadores más finos.
                if current:
                    chunks.append(current)
                    current = ""
                chunks.extend(chunk_recursive(piece, max_chars, remaining))
                continue
            candidate = piece if not current else current + sep + piece
            if len(candidate) <= max_chars:
                current = candidate
            else:
                chunks.append(current)
                current = piece
        if current:
            chunks.append(current)
        return chunks

    # Ningún separador aparece: corte duro.
    return [text[i : i + max_chars] for i in range(0, len(text), max_chars)]


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    texto = "Primer párrafo corto.\n\nSegundo párrafo corto.\n\nTercero."
    print(chunk_recursive(texto, max_chars=50))
