import re

HEADER = re.compile(r"^(#{1,6}) +(.+?)\s*$")


def _split_body(body, max_chars):
    """Divide el cuerpo de una sección por párrafos, juntándolos mientras quepan."""
    body = body.strip()
    if len(body) <= max_chars:
        return [body]
    chunks, current = [], ""
    for paragraph in (p.strip() for p in re.split(r"\n\s*\n", body)):
        if not paragraph:
            continue
        if len(paragraph) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(paragraph[i : i + max_chars] for i in range(0, len(paragraph), max_chars))
            continue
        candidate = paragraph if not current else current + "\n\n" + paragraph
        if len(candidate) <= max_chars:
            current = candidate
        else:
            chunks.append(current)
            current = paragraph
    if current:
        chunks.append(current)
    return chunks


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
    result = []
    headers = []
    buffer = []
    in_code = False

    def flush():
        body = "\n".join(buffer).strip()
        buffer.clear()
        if not body:
            return
        for piece in _split_body(body, max_chars):
            result.append({"text": piece, "headers": list(headers), "path": " > ".join(headers)})

    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
            buffer.append(line)
            continue
        match = None if in_code else HEADER.match(line)
        if match:
            flush()
            level = len(match.group(1))
            headers = headers[: level - 1] + [match.group(2)]
        else:
            buffer.append(line)
    flush()
    return result


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    doc = "# Devoluciones\n\nIntroducción.\n\n## Plazos\n\n14 días naturales."
    for c in chunk_markdown(doc):
        print(c["path"], "|", c["text"])
