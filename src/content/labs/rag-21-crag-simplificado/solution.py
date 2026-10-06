from ragkit.text import tokenize


def coverage(question, docs):
    """Fracción de las raíces de 5 letras de la pregunta que aparecen en los documentos."""
    wanted = {t[:5] for t in tokenize(question)}
    if not wanted:
        return 0.0
    available = {t[:5] for doc in docs for t in tokenize(doc["text"])}
    return len(wanted & available) / len(wanted)


def evaluate_retrieval(question, docs, high=0.6, low=0.35):
    """'correcto', 'ambiguo' o 'incorrecto' según la cobertura."""
    score = coverage(question, docs)
    if score >= high:
        return "correcto"
    if score < low:
        return "incorrecto"
    return "ambiguo"


def crag_answer(question, retrieve, answer_fn, rewrite_fn, max_retries=1, high=0.6, low=0.35):
    """Bucle correctivo: responder, reformular y reintentar, o abstenerse."""
    trace = []
    current = question
    retries = 0
    while True:
        docs = retrieve(current)
        verdict = evaluate_retrieval(current, docs, high=high, low=low)
        trace.append((current, verdict))
        if verdict == "correcto":
            return {
                "action": "answer",
                "answer": answer_fn(current, docs),
                "question": current,
                "trace": trace,
            }
        if verdict == "ambiguo" and retries < max_retries:
            retries += 1
            current = rewrite_fn(current)
            continue
        return {"action": "abstain", "answer": None, "question": current, "trace": trace}


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    docs = [{"text": "El reembolso se realiza por el mismo medio de pago"}]
    print(coverage("¿Cuánto tarda el reembolso del pago?", docs))
