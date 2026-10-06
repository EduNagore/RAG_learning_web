from ragkit.llm import LLMResponse, MockLLM
from ragkit.testing import expect_equal, expect_true

RUTAS = {
    "devoluciones": "plazos, reembolsos y devoluciones",
    "envios": "costes, plazos y seguimiento de envíos",
    "facturas": "facturación y pagos",
}


def test_el_prompt_contiene_rutas_descripciones_y_consulta(student):
    """build_router_prompt incluye todo lo que necesita el modelo"""
    prompt = student.build_router_prompt("¿Dónde está mi pedido?", RUTAS)
    for nombre, descripcion in RUTAS.items():
        expect_true(nombre in prompt, f"Falta la ruta «{nombre}» en el prompt.")
        expect_true(descripcion in prompt, f"Falta la descripción de «{nombre}».")
    expect_true("¿Dónde está mi pedido?" in prompt, "Falta la consulta en el prompt.")


def test_classify_devuelve_la_ruta_mencionada(student):
    """La ruta se reconoce aunque haya puntuación o mayúsculas"""
    llm = MockLLM(script=["Devoluciones."])
    expect_equal(student.classify("q", RUTAS, llm), "devoluciones", what="ruta")
    expect_equal(len(llm.calls), 1, what="llamadas al modelo")


def test_classify_usa_el_orden_de_las_rutas_si_aparecen_varias(student):
    """Si el modelo menciona varias rutas, gana la primera según el orden de `routes`"""
    llm = MockLLM(script=["quizá facturas o devoluciones"])
    expect_equal(student.classify("q", RUTAS, llm), "devoluciones", what="primera ruta en el orden")


def test_classify_devuelve_default_si_no_reconoce_nada(student):
    """Una respuesta sin ninguna ruta cae en el valor por defecto"""
    expect_equal(
        student.classify("q", RUTAS, MockLLM(script=["no lo sé"])), "otros", what="default"
    )
    expect_equal(
        student.classify("q", RUTAS, MockLLM(script=["no lo sé"]), default="humano"),
        "humano",
        what="default personalizado",
    )


def test_route_and_run_ejecuta_el_manejador_de_la_ruta(student):
    """Se ejecuta el manejador correcto con la consulta original"""
    handlers = {
        "devoluciones": lambda q: f"D:{q}",
        "envios": lambda q: f"E:{q}",
        "otros": lambda q: f"O:{q}",
    }
    out = student.route_and_run("consulta", RUTAS, handlers, MockLLM(script=["envios"]))
    expect_equal(out, {"route": "envios", "result": "E:consulta"}, what="resultado")


def test_hidden_las_palabras_deben_ser_completas(student):
    """Caso adicional: «envios» no se reconoce dentro de «envioso»"""
    llm = MockLLM(script=["envioso"])
    expect_equal(student.classify("q", RUTAS, llm), "otros", what="palabra completa")


def test_hidden_ruta_sin_manejador_cae_en_default_y_respuesta_none(student):
    """Caso adicional: sin manejador para la ruta se usa el de default; texto None no rompe"""
    handlers = {"otros": lambda q: "genérico"}
    out = student.route_and_run("q", RUTAS, handlers, MockLLM(script=["facturas"]))
    expect_equal(out, {"route": "otros", "result": "genérico"}, what="ruta sin manejador")
    vacio = MockLLM(script=[LLMResponse(text=None)])
    expect_equal(student.classify("q", RUTAS, vacio), "otros", what="texto None")
