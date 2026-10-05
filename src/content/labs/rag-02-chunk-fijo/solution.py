def chunk_fixed(text, size, overlap):
    """Trocea `text` en ventanas de `size` palabras que se solapan `overlap` palabras.

    - Devuelve una lista de str (palabras unidas por un solo espacio).
    - Texto vacío -> [].  Texto con <= size palabras -> un único fragmento.
    - ValueError si size <= 0, overlap < 0 o overlap >= size.
    - El último fragmento termina donde acaba el texto, sin generar uno redundante.
    """
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("size debe ser positivo y overlap debe cumplir 0 <= overlap < size")

    words = text.split()
    step = size - overlap
    chunks = []
    for start in range(0, len(words), step):
        chunks.append(" ".join(words[start : start + size]))
        # Esta ventana ya llega al final: otra solo repetiría palabras ya incluidas.
        if start + size >= len(words):
            break
    return chunks


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    texto = "uno dos tres cuatro cinco seis siete ocho nueve diez"
    for c in chunk_fixed(texto, size=4, overlap=1):
        print(c)
