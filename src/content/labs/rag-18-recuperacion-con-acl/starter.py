LEVELS = {"public": 0, "internal": 1, "restricted": 2}


def can_access(user, doc):
    """¿Puede el usuario ver el documento?

    user: {"level": "public" | "internal" | "restricted", "departments": [...]}
    doc:  {"id", "access", "department", ...}
    - public: cualquiera.
    - internal: usuarios con nivel internal o restricted.
    - restricted: nivel restricted Y el departamento del documento entre los del usuario.
    - Un nivel de acceso desconocido en el documento se deniega siempre.
    - Un usuario sin nivel (o con un nivel desconocido) cuenta como public.
    """
    # TODO
    raise NotImplementedError("Completa can_access")


def filter_docs(user, docs):
    """Documentos accesibles para el usuario, en el mismo orden."""
    # TODO
    raise NotImplementedError("Completa filter_docs")


def acl_search(user, query, docs, score_fn, top_k=3):
    """Filtra por permisos ANTES de puntuar y devuelve los ids de los top_k mejores.

    score_fn(query, doc) -> float. Solo cuentan los documentos con puntuación > 0; ante un
    empate gana el que aparece antes en `docs`.
    """
    # TODO
    raise NotImplementedError("Completa acl_search")


def audit_leaks(user, result_ids, docs_by_id):
    """Ids de los resultados que el usuario NO debería ver (o que no existen), en orden.

    Es la defensa en profundidad: se aplica sobre el resultado final antes de construir el prompt.
    """
    # TODO
    raise NotImplementedError("Completa audit_leaks")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    doc = {"id": "d1", "access": "restricted", "department": "Recursos Humanos"}
    try:
        print(can_access({"level": "internal"}, doc))
        print(can_access({"level": "restricted", "departments": ["Recursos Humanos"]}, doc))
    except NotImplementedError as e:
        print("Aún por completar:", e)
