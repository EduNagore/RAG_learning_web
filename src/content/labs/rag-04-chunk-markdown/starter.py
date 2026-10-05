def chunk_markdown(text, max_chars=500):
    """Trocea un documento Markdown por encabezados y devuelve dicts {text, headers, path}.

    - Encabezado: línea que empieza por 1 a 6 '#' y un espacio. Nivel = nº de '#'.
    - El cuerpo de cada sección (sin la línea del encabezado) es un fragmento.
    - headers: ruta de títulos hasta la sección; al llegar un encabezado de nivel n se
      descartan los títulos de nivel n o más profundo. path = " > ".join(headers).
    - Texto previo al primer encabezado: headers [] y path "".
    - Secciones sin cuerpo: no generan fragmento.
    - Cuerpo mayor que max_chars: se divide por párrafos (línea en blanco), juntándolos mientras
      quepan; un párrafo mayor que el máximo se corta cada max_chars caracteres.
    - Una línea que empieza por '#' dentro de un bloque ``` NO es un encabezado.
    """
    # TODO
    raise NotImplementedError("Completa chunk_markdown")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    doc = "# Devoluciones\n\nIntroducción.\n\n## Plazos\n\n14 días naturales."
    try:
        for c in chunk_markdown(doc):
            print(c["path"], "|", c["text"])
    except NotImplementedError as e:
        print("Aún por completar:", e)
