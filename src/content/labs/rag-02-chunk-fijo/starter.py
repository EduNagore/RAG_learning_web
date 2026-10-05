def chunk_fixed(text, size, overlap):
    """Trocea `text` en ventanas de `size` palabras que se solapan `overlap` palabras.

    - Devuelve una lista de str (palabras unidas por un solo espacio).
    - Texto vacío -> [].  Texto con <= size palabras -> un único fragmento.
    - ValueError si size <= 0, overlap < 0 o overlap >= size.
    - El último fragmento termina donde acaba el texto, sin generar uno redundante.
    """
    # TODO: implementa la ventana deslizante
    raise NotImplementedError("Completa chunk_fixed")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    texto = "uno dos tres cuatro cinco seis siete ocho nueve diez"
    try:
        for c in chunk_fixed(texto, size=4, overlap=1):
            print(c)
    except NotImplementedError as e:
        print("Aún por completar:", e)
