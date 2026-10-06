from ragkit.testing import expect_equal, expect_raises, expect_true


def lineal(student, contador=None):
    """redactar -> revisar -> publicar, contando cuántas veces se ejecuta cada nodo."""
    contador = contador if contador is not None else {}

    def nodo(nombre, clave, valor):
        def f(state):
            contador[nombre] = contador.get(nombre, 0) + 1
            return {clave: valor}

        return f

    g = student.StateGraph()
    g.add_node("redactar", nodo("redactar", "borrador", "v1"))
    g.add_node("revisar", nodo("revisar", "revisado", True))
    g.add_node("publicar", nodo("publicar", "publicado", True))
    g.add_edge("redactar", "revisar")
    g.add_edge("revisar", "publicar")
    return g, contador


def test_ejecuta_el_grafo_y_guarda_un_checkpoint_por_paso(student):
    """El estado se fusiona y cada paso deja un checkpoint con el siguiente nodo"""
    g, _ = lineal(student)
    out = g.run("h1", {"tema": "x"})
    expect_equal(out["status"], "done", what="estado final")
    expect_equal(out["steps"], 3, what="pasos")
    expect_equal(
        out["state"],
        {"tema": "x", "borrador": "v1", "revisado": True, "publicado": True},
        what="estado",
    )
    expect_equal(
        g.history("h1"),
        [(0, "redactar"), (1, "revisar"), (2, "publicar"), (3, "__end__")],
        what="checkpoints",
    )
    expect_equal(
        [c["status"] for c in g.checkpoints["h1"]],
        ["running", "running", "running", "done"],
        what="estado de cada checkpoint",
    )


def test_los_hilos_estan_aislados_y_get_state_devuelve_una_copia(student):
    """Cada hilo tiene su estado; modificar la copia no altera el checkpoint"""
    g, _ = lineal(student)
    g.run("a", {"tema": "A"})
    g.run("b", {"tema": "B"})
    expect_equal(g.get_state("a")["tema"], "A", what="hilo a")
    expect_equal(g.get_state("b")["tema"], "B", what="hilo b")
    g.get_state("a")["tema"] = "manipulado"
    expect_equal(g.get_state("a")["tema"], "A", what="get_state debe devolver una copia")
    expect_equal(g.get_state("no-existe"), None, what="hilo inexistente")


def test_un_hilo_terminado_no_se_vuelve_a_ejecutar(student):
    """Llamar de nuevo a run sobre un hilo done devuelve el resultado sin ejecutar nodos"""
    g, contador = lineal(student)
    g.run("h", {"tema": "x"})
    out = g.run("h")
    expect_equal(out["status"], "done", what="estado")
    expect_equal(contador, {"redactar": 1, "revisar": 1, "publicar": 1}, what="ejecuciones")


def test_la_pausa_guarda_el_estado_y_la_reanudacion_continua(student):
    """NeedsInput interrumpe; resume re-ejecuta el nodo interrumpido con state['resume']"""
    llamadas = {"antes": 0, "aprobar": 0}

    def antes(state):
        llamadas["antes"] += 1
        return {"borrador": "texto"}

    def aprobar(state):
        llamadas["aprobar"] += 1
        if "resume" not in state:
            raise student.NeedsInput("¿Apruebas?")
        return {"aprobado": state["resume"]}

    g = student.StateGraph()
    g.add_node("antes", antes)
    g.add_node("aprobar", aprobar)
    g.add_edge("antes", "aprobar")
    pausa = g.run("h", {})
    expect_equal((pausa["status"], pausa["question"]), ("interrupted", "¿Apruebas?"), what="pausa")
    expect_equal(g.get_state("h"), {"borrador": "texto"}, what="estado guardado en la pausa")
    ultimo = g.checkpoints["h"][-1]
    expect_equal(
        (ultimo["step"], ultimo["node"], ultimo["status"]),
        (1, "aprobar", "interrupted"),
        what="checkpoint de la pausa",
    )
    expect_raises(ValueError, g.run, "h", what="reanudar sin resume")
    fin = g.run("h", resume="sí")
    expect_equal(fin["status"], "done", what="estado final")
    expect_equal(fin["state"], {"borrador": "texto", "aprobado": "sí"}, what="estado final")
    expect_equal(llamadas, {"antes": 1, "aprobar": 2}, what="el nodo anterior no se repite; el interrumpido sí")


def test_un_fallo_deja_los_checkpoints_y_se_reanuda_desde_el_ultimo_nodo(student):
    """Tolerancia a fallos: otra llamada continúa donde se quedó, sin repetir lo hecho"""
    contador = {}
    g, contador = lineal(student, contador)
    estado = {"falla": True}
    original = g.nodes["revisar"]

    def revisar(state):
        if estado["falla"]:
            raise RuntimeError("caída del servicio")
        return original(state)

    g.nodes["revisar"] = revisar
    expect_raises(RuntimeError, g.run, "h", {"tema": "x"}, what="el fallo se propaga")
    expect_equal(g.history("h"), [(0, "redactar"), (1, "revisar")], what="checkpoints tras el fallo")
    estado["falla"] = False
    out = g.run("h")
    expect_equal(out["status"], "done", what="estado final")
    expect_equal(contador["redactar"], 1, what="redactar no se repite")


def test_las_aristas_condicionales_eligen_el_camino(student):
    """El router decide el siguiente nodo según el estado"""
    g = student.StateGraph()
    g.add_node("clasificar", lambda s: {"urgente": s["importe"] > 100})
    g.add_node("humano", lambda s: {"ruta": "humano"})
    g.add_node("auto", lambda s: {"ruta": "auto"})
    g.add_conditional_edge("clasificar", lambda s: "humano" if s["urgente"] else "auto")
    expect_equal(g.run("a", {"importe": 500})["state"]["ruta"], "humano", what="importe alto")
    expect_equal(g.run("b", {"importe": 5})["state"]["ruta"], "auto", what="importe bajo")


def test_hidden_max_steps_deja_el_hilo_reanudable(student):
    """Caso adicional: un bucle se corta tras max_steps y otra llamada lo continúa"""
    g = student.StateGraph()
    g.add_node("contar", lambda s: {"n": s["n"] + 1})
    g.add_conditional_edge("contar", lambda s: "contar" if s["n"] < 5 else student.END)
    primera = g.run("h", {"n": 0}, max_steps=2)
    expect_equal((primera["status"], primera["state"]["n"]), ("max_steps", 2), what="primera parte")
    segunda = g.run("h", max_steps=10)
    expect_equal((segunda["status"], segunda["state"]["n"]), ("done", 5), what="reanudación")


def test_hidden_hilo_nuevo_sin_estado_y_copias_profundas(student):
    """Caso adicional: ValueError sin input_state; los checkpoints no comparten objetos con el estado"""
    g = student.StateGraph()
    g.add_node("anadir", lambda s: s["lista"].append(1))
    expect_raises(ValueError, g.run, "nuevo", what="hilo nuevo sin input_state")
    entrada = {"lista": [0]}
    g.run("h", entrada)
    primero = g.checkpoints["h"][0]["state"]
    expect_equal(primero, {"lista": [0]}, what="el checkpoint inicial no se modifica después")
    expect_true(primero is not entrada, "El checkpoint debe ser una copia, no el estado original.")
