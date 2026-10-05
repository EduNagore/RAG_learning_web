import numpy as np
from ragkit.data import load_corpus, load_golden
from ragkit.embeddings import HashingEmbedder
from ragkit.llm import LLMResponse, MockLLM
from ragkit.testing import expect_close, expect_equal, expect_true

EMB = HashingEmbedder()
CORPUS = load_corpus()
IDS = [d["id"] for d in CORPUS]
VECTORS = EMB.embed_many([d["title"] + ". " + d["text"] for d in CORPUS])
PREGUNTAS = {q["id"]: q["question"] for q in load_golden()}

HIPOTESIS_Q09 = (
    "Para seguir tu pedido recibes un correo con el número de seguimiento "
    "y puedes ver su estado en Mi Nimbus."
)
HIPOTESIS_Q20 = (
    "Las contraseñas deben tener al menos 14 caracteres según la política de contraseñas."
)


def test_el_prompt_contiene_la_pregunta(student):
    """hyde_prompt incluye la pregunta del usuario"""
    prompt = student.hyde_prompt("¿Cómo sigo mi pedido?")
    expect_true("¿Cómo sigo mi pedido?" in prompt, "El prompt debe incluir la pregunta.")


def test_el_vector_hyde_es_el_de_la_hipotesis_normalizado(student):
    """Con mix=0 el vector es el embedding de la hipótesis"""
    llm = MockLLM(script=[HIPOTESIS_Q20])
    v = student.hyde_vector(PREGUNTAS["q20"], llm, EMB.embed)
    expect_true(np.allclose(v, EMB.embed(HIPOTESIS_Q20)), "Debe coincidir con embed(hipótesis).")
    expect_equal(len(llm.calls), 1, what="llamadas al modelo")


def test_la_mezcla_interpola_y_normaliza(student):
    """Con mix intermedio se mezclan ambos embeddings y el resultado tiene norma 1"""
    llm = MockLLM(script=[HIPOTESIS_Q20])
    v = student.hyde_vector(PREGUNTAS["q20"], llm, EMB.embed, mix=0.3)
    esperado = 0.7 * EMB.embed(HIPOTESIS_Q20) + 0.3 * EMB.embed(PREGUNTAS["q20"])
    esperado = esperado / np.linalg.norm(esperado)
    expect_true(np.allclose(v, esperado), "Mezcla incorrecta de los embeddings.")
    expect_close(np.linalg.norm(v), 1.0, what="norma del vector mezclado")


def test_hyde_encuentra_documentos_que_la_pregunta_sola_no_encuentra(student):
    """Con la hipótesis, el documento correcto es el primero"""
    for qid, hipotesis, esperado in (
        ("q09", HIPOTESIS_Q09, "doc-009"),
        ("q20", HIPOTESIS_Q20, "doc-035"),
    ):
        llm = MockLLM(script=[hipotesis])
        out = student.hyde_search(PREGUNTAS[qid], llm, EMB.embed, VECTORS, IDS, top_k=3)
        expect_equal(out[0], esperado, what=f"primer resultado de {qid}")
        expect_equal(len(out), 3, what="número de resultados")


def test_con_mix_uno_equivale_a_buscar_con_la_pregunta(student):
    """mix=1 ignora la hipótesis"""
    llm = MockLLM(script=[HIPOTESIS_Q09])
    out = student.hyde_search(PREGUNTAS["q09"], llm, EMB.embed, VECTORS, IDS, top_k=5, mix=1.0)
    directo = [IDS[i] for i in np.argsort(-(VECTORS @ EMB.embed(PREGUNTAS["q09"])), kind="stable")]
    expect_equal(out, directo[:5], what="resultado con mix=1")


def test_hidden_plan_b_si_el_modelo_no_devuelve_texto(student):
    """Caso adicional: respuesta vacía, solo espacios o None → se usa la pregunta"""
    for respuesta in ("", "   \n", LLMResponse(text=None)):
        llm = MockLLM(script=[respuesta])
        v = student.hyde_vector(PREGUNTAS["q20"], llm, EMB.embed, mix=0.0)
        expect_true(
            np.allclose(v, EMB.embed(PREGUNTAS["q20"])), "Sin texto, debe usar embed(pregunta)."
        )


def test_hidden_los_empates_conservan_el_orden_de_los_ids(student):
    """Caso adicional: vectores idénticos se devuelven en el orden de doc_ids"""
    vectores = np.array([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    llm = MockLLM(script=["texto"])
    out = student.hyde_search("q", llm, lambda t: np.array([1.0, 0.0]), vectores, ["a", "b", "c"])
    expect_equal(out, ["a", "b", "c"], what="orden con empate")
