import re

from ragkit.text import tokenize


def split_claims(answer):
    """Afirmaciones de la respuesta: una por frase.

    - Quita las citas [doc-123] o [doc-1, doc-2] y deja los espacios y la puntuación limpios
      ("Hola [doc-001]." -> "Hola.").
    - Descarta las frases sin ninguna letra o número (por ejemplo "...").
    - La abstención "NO_LO_SE" no contiene afirmaciones: devuelve [].
    """
    # TODO
    raise NotImplementedError("Completa split_claims")


def claim_supported(claim, context_texts, threshold=0.6):
    """¿Está la afirmación respaldada por el contexto (lista de textos)?

    - Todo número de la afirmación (p. ej. 7 o 3,5) debe aparecer en el contexto.
    - Al menos `threshold` de sus palabras (tokenize, por raíz de 5 letras) deben aparecer en él.
    - Una afirmación sin palabras útiles no está respaldada.
    """
    # TODO
    raise NotImplementedError("Completa claim_supported")


def faithfulness(answer, context_texts, threshold=0.6):
    """{"score": respaldadas / total (None si no hay afirmaciones), "claims": [(texto, bool)]}."""
    # TODO
    raise NotImplementedError("Completa faithfulness")


def context_recall(reference_answer, context_texts, threshold=0.6):
    """Fracción de las afirmaciones de la respuesta de referencia que el contexto respalda.

    None si la referencia no tiene afirmaciones.
    """
    # TODO
    raise NotImplementedError("Completa context_recall")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    contexto = ["El reembolso tarda un máximo de 7 días hábiles desde que el paquete llega."]
    try:
        print(faithfulness("El reembolso tarda 7 días hábiles [doc-002]. Es gratis para todos.", contexto))
    except NotImplementedError as e:
        print("Aún por completar:", e)
