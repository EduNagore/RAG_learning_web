import re

from ragkit.text import tokenize

_CITA = re.compile(r"\[doc-\d+(?:\s*,\s*doc-\d+)*\]")
_NUMERO = re.compile(r"\d+(?:[.,]\d+)?")


def split_claims(answer):
    """Afirmaciones de la respuesta: una por frase, sin citas [doc-123] y sin frases vacías."""
    if answer.strip() == "NO_LO_SE":
        return []
    sentences = re.split(r"(?<=[.!?])\s+", answer.strip())
    claims = [" ".join(_CITA.sub("", s).split()) for s in sentences]
    claims = [re.sub(r"\s+([.!?])", r"\1", c) for c in claims]
    return [c for c in claims if re.search(r"\w", c)]


def claim_supported(claim, context_texts, threshold=0.6):
    """¿Está la afirmación respaldada por el contexto?

    - Todo número de la afirmación debe aparecer en el contexto.
    - Y al menos `threshold` de sus palabras (por raíz de 5 letras) deben aparecer en él.
    """
    context = " ".join(context_texts)
    if any(n not in _NUMERO.findall(context) for n in _NUMERO.findall(claim)):
        return False
    words = {t[:5] for t in tokenize(claim)}
    if not words:
        return False
    available = {t[:5] for t in tokenize(context)}
    return len(words & available) / len(words) >= threshold


def faithfulness(answer, context_texts, threshold=0.6):
    """{"score": afirmaciones respaldadas / total (None si no hay), "claims": [(texto, bool)]}."""
    claims = split_claims(answer)
    results = [(c, claim_supported(c, context_texts, threshold)) for c in claims]
    score = sum(ok for _, ok in results) / len(results) if results else None
    return {"score": score, "claims": results}


def context_recall(reference_answer, context_texts, threshold=0.6):
    """Fracción de las afirmaciones de la respuesta de referencia que el contexto respalda."""
    claims = split_claims(reference_answer)
    if not claims:
        return None
    return sum(claim_supported(c, context_texts, threshold) for c in claims) / len(claims)


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    contexto = ["El reembolso tarda un máximo de 7 días hábiles desde que el paquete llega."]
    print(
        faithfulness("El reembolso tarda 7 días hábiles [doc-002]. Es gratis para todos.", contexto)
    )
