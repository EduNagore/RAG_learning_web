import re


def _default_normalize(answer):
    return str(answer).strip().lower()


def majority_vote(answers, normalize=_default_normalize):
    """Devuelve (ganador, conteos) por mayoría.

    - Las respuestas se comparan tras aplicar `normalize`; `conteos` es un dict normalizada -> votos.
    - El ganador es el más votado; ante un empate gana la respuesta que apareció antes.
    - Se devuelve el texto ORIGINAL de la primera aparición del ganador.
    - Sin respuestas: (None, {}).
    """
    # TODO
    raise NotImplementedError("Completa majority_vote")


def agreement(answers, normalize=_default_normalize):
    """Fracción de respuestas que coinciden con la ganadora (0.0 si no hay respuestas)."""
    # TODO
    raise NotImplementedError("Completa agreement")


def extract_last_number(text):
    """Último número del texto (enteros o decimales con coma o punto), con la coma convertida
    en punto ("3,5" -> "3.5"), o None si no hay ninguno.
    """
    # TODO
    raise NotImplementedError("Completa extract_last_number")


def sample_and_vote(generate, n, extract=lambda s: s, min_agreement=0.0):
    """Self-consistency: genera n muestras, extrae la respuesta de cada una y vota.

    generate(i) devuelve el texto de la muestra i (i = 0..n-1). Las extracciones None se descartan.
    Devuelve {"answer": ganador o None, "agreement": fracción, "votes": conteos}.
    Si el acuerdo es menor que `min_agreement`, "answer" es None (el sistema se abstiene).
    """
    # TODO
    raise NotImplementedError("Completa sample_and_vote")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    try:
        print(majority_vote(["42", " 42", "41", "42 "]))
        print(extract_last_number("Son 3,5 euros más 2 de envío: total 5,5"))
    except NotImplementedError as e:
        print("Aún por completar:", e)
