import numpy as np
from ragkit.llm import Message


def hyde_prompt(question):
    """Texto que se envía al modelo: pide una respuesta breve a la pregunta."""
    return (
        "Escribe un párrafo breve, como el que aparecería en un documento de la empresa, "
        f"que responda a esta pregunta: {question}"
    )


def hyde_vector(question, llm, embed, mix=0.0):
    """Embedding de la respuesta hipotética, mezclado con el de la pregunta según `mix`."""
    respuesta = llm.generate([Message("user", hyde_prompt(question))]).text
    if respuesta is None or not respuesta.strip():
        return embed(question)
    vector = (1 - mix) * embed(respuesta) + mix * embed(question)
    norma = np.linalg.norm(vector)
    return vector / norma if norma > 0 else vector


def hyde_search(question, llm, embed, doc_vectors, doc_ids, top_k=3, mix=0.0):
    """Ids de los top_k documentos más cercanos al vector HyDE."""
    vector = hyde_vector(question, llm, embed, mix=mix)
    puntuaciones = np.asarray(doc_vectors) @ vector
    orden = np.argsort(-puntuaciones, kind="stable")[:top_k]
    return [doc_ids[i] for i in orden]


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    from ragkit.embeddings import HashingEmbedder
    from ragkit.llm import MockLLM

    emb = HashingEmbedder()
    llm = MockLLM(script=["Las contraseñas deben tener al menos 14 caracteres."])
    v = hyde_vector("¿Cuál es la longitud mínima de una contraseña?", llm, emb.embed)
    print(round(float(np.linalg.norm(v)), 3))
