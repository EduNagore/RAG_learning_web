LEVELS = {"public": 0, "internal": 1, "restricted": 2}


def can_access(user, doc):
    """¿Puede el usuario ver el documento?

    - public: cualquiera.
    - internal: usuarios con nivel internal o restricted.
    - restricted: nivel restricted Y el departamento del documento entre los suyos.
    - Un nivel de acceso desconocido, siempre denegado.
    """
    required = LEVELS.get(doc.get("access"))
    if required is None:
        return False
    granted = LEVELS.get(user.get("level"), 0)
    if required == LEVELS["restricted"]:
        return granted >= required and doc.get("department") in user.get("departments", [])
    return granted >= required


def filter_docs(user, docs):
    """Documentos accesibles, en el mismo orden."""
    return [d for d in docs if can_access(user, d)]


def acl_search(user, query, docs, score_fn, top_k=3):
    """Filtra por permisos ANTES de puntuar y devuelve los ids de los top_k mejores (score > 0)."""
    allowed = filter_docs(user, docs)
    scored = [(score_fn(query, d), i, d["id"]) for i, d in enumerate(allowed)]
    ranked = sorted((s for s in scored if s[0] > 0), key=lambda s: (-s[0], s[1]))
    return [doc_id for _, _, doc_id in ranked[:top_k]]


def audit_leaks(user, result_ids, docs_by_id):
    """Ids de los resultados que el usuario NO debería ver (o que no existen), en orden."""
    return [i for i in result_ids if i not in docs_by_id or not can_access(user, docs_by_id[i])]


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    doc = {"id": "d1", "access": "restricted", "department": "Recursos Humanos"}
    print(can_access({"level": "internal"}, doc))
    print(can_access({"level": "restricted", "departments": ["Recursos Humanos"]}, doc))
