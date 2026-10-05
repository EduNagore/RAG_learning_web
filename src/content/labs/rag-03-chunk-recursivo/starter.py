def chunk_recursive(text, max_chars, separators=("\n\n", "\n", " ")):
    """Trocea `text` en fragmentos de como mucho `max_chars` caracteres, respetando la estructura.

    1. Si el texto cabe, devuelve [texto] (vacío -> []).
    2. Si no, divide por el primer separador que aparezca y fusiona las piezas de forma voraz.
    3. Una pieza que por sí sola excede el máximo se trocea recursivamente con los separadores
       que quedan.
    4. Sin separadores, corta a la fuerza cada `max_chars` caracteres.
    Los fragmentos salen en orden, sin vacíos y con longitud <= max_chars.
    """
    # TODO
    raise NotImplementedError("Completa chunk_recursive")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    texto = "Primer párrafo corto.\n\nSegundo párrafo corto.\n\nTercero."
    try:
        print(chunk_recursive(texto, max_chars=50))
    except NotImplementedError as e:
        print("Aún por completar:", e)
