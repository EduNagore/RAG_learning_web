from ragkit.text import tokenize


def coverage(question, docs):
    """Fracción (0 a 1) de las raíces de 5 letras de la pregunta que aparecen en los documentos.

    docs: lista de dicts con 'text'. Usa ragkit.text.tokenize (ya quita palabras vacías) y
    compara t[:5]. Si la pregunta no tiene palabras útiles, devuelve 0.0.
    """
    # TODO
    raise NotImplementedError("Completa coverage")


def evaluate_retrieval(question, docs, high=0.6, low=0.35):
    """'correcto' si la cobertura es >= high, 'incorrecto' si es < low y 'ambiguo' si no."""
    # TODO
    raise NotImplementedError("Completa evaluate_retrieval")


def crag_answer(question, retrieve, answer_fn, rewrite_fn, max_retries=1, high=0.6, low=0.35):
    """Bucle correctivo.

    retrieve(pregunta) -> docs; answer_fn(pregunta, docs) -> texto; rewrite_fn(pregunta) -> pregunta.
    - correcto   -> responde con answer_fn (action "answer").
    - incorrecto -> se abstiene (action "abstain") sin reintentar.
    - ambiguo    -> si quedan reintentos, reformula con rewrite_fn y vuelve a empezar;
                    si no quedan, se abstiene.
    Devuelve {"action", "answer" (None si se abstuvo), "question" (la última), "trace"},
    donde trace es la lista de (pregunta, veredicto) de cada intento.
    """
    # TODO
    raise NotImplementedError("Completa crag_answer")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    docs = [{"text": "El reembolso se realiza por el mismo medio de pago"}]
    try:
        print(coverage("¿Cuánto tarda el reembolso del pago?", docs))
    except NotImplementedError as e:
        print("Aún por completar:", e)
