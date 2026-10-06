import re


def _default_normalize(answer):
    return str(answer).strip().lower()


def majority_vote(answers, normalize=_default_normalize):
    """(ganador, conteos) por mayoría. Las respuestas se comparan normalizadas.

    El ganador es la respuesta más votada; ante un empate, la que apareció antes. El texto
    devuelto del ganador es el de su primera aparición. Sin respuestas: (None, {}).
    """
    counts = {}
    first_seen = {}
    for answer in answers:
        key = normalize(answer)
        counts[key] = counts.get(key, 0) + 1
        first_seen.setdefault(key, answer)
    if not counts:
        return None, {}
    best = max(counts, key=lambda k: (counts[k], -list(counts).index(k)))
    return first_seen[best], counts


def agreement(answers, normalize=_default_normalize):
    """Fracción de respuestas que coinciden con la ganadora (0.0 si no hay respuestas)."""
    winner, counts = majority_vote(answers, normalize)
    if winner is None:
        return 0.0
    return counts[normalize(winner)] / len(answers)


def extract_last_number(text):
    """Último número del texto, con coma decimal convertida en punto, o None si no hay."""
    numbers = re.findall(r"\d+(?:[.,]\d+)?", text)
    return numbers[-1].replace(",", ".") if numbers else None


def sample_and_vote(generate, n, extract=lambda s: s, min_agreement=0.0):
    """Genera n muestras, extrae la respuesta de cada una y vota.

    generate(i) devuelve el texto de la muestra i. Las extracciones None se descartan.
    Devuelve {"answer": ganador o None, "agreement": fracción, "votes": conteos}. Si el acuerdo
    es menor que `min_agreement`, la respuesta es None (el sistema se abstiene).
    """
    extracted = [e for e in (extract(generate(i)) for i in range(n)) if e is not None]
    winner, counts = majority_vote(extracted)
    share = agreement(extracted)
    if winner is None or share < min_agreement:
        winner = None
    return {"answer": winner, "agreement": share, "votes": counts}


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    print(majority_vote(["42", " 42", "41", "42 "]))
    print(extract_last_number("Son 3,5 euros más 2 de envío: total 5,5"))
