import re


def split_sentences(text):
    """Divide en frases por el punto, la interrogación o la exclamación finales (ya resuelta)."""
    return [f.strip() for f in re.split(r"(?<=[.!?])\s+", text) if f.strip()]


def build_children(docs):
    """Un hijo por frase: child_id, parent_id, pos y text."""
    children = []
    for doc in docs:
        for pos, sentence in enumerate(split_sentences(doc["text"])):
            children.append(
                {
                    "child_id": f"{doc['id']}#{pos}",
                    "parent_id": doc["id"],
                    "pos": pos,
                    "text": sentence,
                }
            )
    return children


def to_parents(child_ids, children, docs_by_id, max_parents=None):
    """Padres de los hijos recuperados, en orden de primera aparición y sin repetir."""
    parent_of = {c["child_id"]: c["parent_id"] for c in children}
    parents, seen = [], set()
    for child_id in child_ids:
        parent_id = parent_of.get(child_id)
        if parent_id is None or parent_id in seen:
            continue
        seen.add(parent_id)
        parents.append({"id": parent_id, "text": docs_by_id[parent_id]["text"]})
    return parents if max_parents is None else parents[:max_parents]


def small_to_big_search(query, children, score_fn, docs_by_id, top_k_children=3, max_parents=None):
    """Busca con los hijos y entrega los padres."""
    scored = [(score_fn(query, c["text"]), c["child_id"]) for c in children]
    ranked = sorted((s for s in scored if s[0] > 0), key=lambda x: -x[0])
    top = [child_id for _, child_id in ranked[:top_k_children]]
    return to_parents(top, children, docs_by_id, max_parents=max_parents)


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    docs = [{"id": "d1", "text": "Primera frase. Segunda frase."}]
    for hijo in build_children(docs):
        print(hijo)
