import re


def split_sentences(text):
    """Divide en frases por el punto, la interrogación o la exclamación finales (ya resuelta)."""
    return [f.strip() for f in re.split(r"(?<=[.!?])\s+", text) if f.strip()]


def build_children(docs):
    """Un hijo por frase, en el orden del corpus.

    Cada hijo es un dict con:
      child_id: "<id del documento>#<posición>" (la posición empieza en 0 en cada documento)
      parent_id: el id del documento
      pos: posición de la frase en su documento
      text: la frase
    """
    # TODO
    raise NotImplementedError("Completa build_children")


def to_parents(child_ids, children, docs_by_id, max_parents=None):
    """Padres de los hijos recuperados, como dicts {"id", "text"}.

    - Orden de primera aparición y sin repetir ningún padre.
    - Un child_id desconocido se ignora.
    - Si max_parents no es None, recorta.
    """
    # TODO
    raise NotImplementedError("Completa to_parents")


def small_to_big_search(query, children, score_fn, docs_by_id, top_k_children=3, max_parents=None):
    """Busca con los hijos y entrega los padres.

    Puntúa cada hijo con score_fn(query, texto), descarta los de puntuación <= 0, toma los
    top_k_children mejores (empate: orden original) y devuelve to_parents de ese resultado.
    """
    # TODO
    raise NotImplementedError("Completa small_to_big_search")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    docs = [{"id": "d1", "text": "Primera frase. Segunda frase."}]
    try:
        for hijo in build_children(docs):
            print(hijo)
    except NotImplementedError as e:
        print("Aún por completar:", e)
