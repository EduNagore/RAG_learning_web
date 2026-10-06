from ragkit.testing import expect_equal, expect_raises

SUMAR = {
    "type": "object",
    "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
    "required": ["a", "b"],
}
CONVERTIR = {
    "type": "object",
    "properties": {
        "valor": {"type": "number"},
        "unidad": {"type": "string", "enum": ["km", "mi"]},
        "etiquetas": {"type": "array"},
        "exacto": {"type": "boolean"},
    },
    "required": ["valor", "unidad"],
}


def registro(student):
    r = student.ToolRegistry()
    r.register("sumar", lambda a, b: a + b, "Suma dos enteros", SUMAR)
    r.register("convertir", lambda valor, unidad, **kw: f"{valor} {unidad}", "Convierte", CONVERTIR)
    return r


def test_specs_en_orden_de_registro(student):
    """specs devuelve un ToolSpec por herramienta, en orden"""
    specs = registro(student).specs()
    expect_equal([s.name for s in specs], ["sumar", "convertir"], what="nombres")
    expect_equal(specs[0].description, "Suma dos enteros", what="descripción")
    expect_equal(specs[0].parameters, SUMAR, what="esquema")


def test_no_se_puede_registrar_dos_veces_el_mismo_nombre(student):
    """Un nombre duplicado lanza ValueError"""
    r = registro(student)
    expect_raises(
        ValueError, r.register, "sumar", lambda: 0, "otra", {"type": "object"}, what="duplicado"
    )


def test_argumentos_validos_no_dan_errores(student):
    """validate devuelve una lista vacía cuando todo es correcto"""
    r = registro(student)
    expect_equal(r.validate("sumar", {"a": 1, "b": 2}), [], what="sumar válido")
    expect_equal(
        r.validate("convertir", {"valor": 2.5, "unidad": "km", "etiquetas": [], "exacto": True}),
        [],
        what="convertir válido",
    )


def test_detecta_obligatorios_inexistentes_y_herramienta_desconocida(student):
    """Mensajes de error exactos"""
    r = registro(student)
    expect_equal(
        r.validate("sumar", {"a": 1}), ["falta el argumento obligatorio: b"], what="falta b"
    )
    expect_equal(
        r.validate("sumar", {"a": 1, "b": 2, "c": 3}),
        ["argumento no esperado: c"],
        what="argumento extra",
    )
    expect_equal(
        r.validate("restar", {}), ["herramienta desconocida: restar"], what="herramienta ausente"
    )


def test_detecta_tipos_incorrectos_y_valores_fuera_del_enum(student):
    """Tipos y enum"""
    r = registro(student)
    expect_equal(
        r.validate("sumar", {"a": "1", "b": 2}),
        ["el argumento 'a' debe ser integer"],
        what="tipo incorrecto",
    )
    expect_equal(
        r.validate("convertir", {"valor": 1, "unidad": "m"}),
        ["el argumento 'unidad' debe ser uno de ['km', 'mi']"],
        what="enum",
    )


def test_call_ejecuta_y_devuelve_el_resultado(student):
    """call devuelve ok y result"""
    expect_equal(
        registro(student).call("sumar", {"a": 2, "b": 3}), {"ok": True, "result": 5}, what="call"
    )


def test_call_devuelve_los_errores_de_validacion_unidos(student):
    """Varios errores se unen con '; ' y la función no se ejecuta"""
    ejecutada = []
    r = student.ToolRegistry()
    r.register("sumar", lambda a, b: ejecutada.append(1) or a + b, "Suma", SUMAR)
    out = r.call("sumar", {"a": "x", "c": 1})
    expect_equal(
        out,
        {
            "ok": False,
            "error": "falta el argumento obligatorio: b; el argumento 'a' debe ser integer; "
            "argumento no esperado: c",
        },
        what="errores unidos",
    )
    expect_equal(ejecutada, [], what="la función no debe ejecutarse")


def test_hidden_los_booleanos_no_son_enteros_ni_numeros(student):
    """Caso adicional: True no es un integer ni un number válido"""
    r = registro(student)
    expect_equal(
        r.validate("sumar", {"a": True, "b": 2}),
        ["el argumento 'a' debe ser integer"],
        what="bool como integer",
    )
    expect_equal(
        r.validate("convertir", {"valor": False, "unidad": "km"}),
        ["el argumento 'valor' debe ser number"],
        what="bool como number",
    )


def test_hidden_una_excepcion_de_la_herramienta_se_devuelve_como_error(student):
    """Caso adicional: la excepción no rompe al agente, se convierte en observación"""
    r = student.ToolRegistry()
    r.register("dividir", lambda a, b: a / b, "Divide", SUMAR)
    expect_equal(
        r.call("dividir", {"a": 1, "b": 0}),
        {"ok": False, "error": "ZeroDivisionError: division by zero"},
        what="excepción",
    )
