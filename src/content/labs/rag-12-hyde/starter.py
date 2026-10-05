import numpy as np
from ragkit.llm import Message


def hyde_prompt(question):
    """Texto que se envía al modelo: debe contener la pregunta y pedir una respuesta breve."""
    # TODO
    raise NotImplementedError("Completa hyde_prompt")


def hyde_vector(question, llm, embed, mix=0.0):
    """Embedding de la respuesta hipotética, mezclado con el de la pregunta según `mix`.

    1. UNA llamada: llm.generate([Message("user", hyde_prompt(question))]).text
    2. Si el texto es None, vacío o solo espacios: devuelve embed(question).
    3. Si no: (1 - mix) * embed(texto) + mix * embed(question), normalizado a norma 1
       (si la norma es 0, se devuelve tal cual).
    """
    # TODO
    raise NotImplementedError("Completa hyde_vector")


def hyde_search(question, llm, embed, doc_vectors, doc_ids, top_k=3, mix=0.0):
    """Ids de los top_k documentos con mayor producto escalar con el vector HyDE.

    Los empates conservan el orden de doc_ids.
    """
    # TODO
    raise NotImplementedError("Completa hyde_search")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    from ragkit.embeddings import HashingEmbedder
    from ragkit.llm import MockLLM

    try:
        emb = HashingEmbedder()
        llm = MockLLM(script=["Las contraseñas deben tener al menos 14 caracteres."])
        v = hyde_vector("¿Cuál es la longitud mínima de una contraseña?", llm, emb.embed)
        print(round(float(np.linalg.norm(v)), 3))  # 1.0
    except NotImplementedError as e:
        print("Aún por completar:", e)
