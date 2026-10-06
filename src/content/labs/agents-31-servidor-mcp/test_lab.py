import json

from ragkit.testing import expect_equal, expect_true

SUMAR = {
    "type": "object",
    "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
    "required": ["a", "b"],
}


def servidor(student):
    s = student.MCPServer("nimbus", "1.2.3")
    s.add_tool("sumar", "Suma dos enteros", SUMAR, lambda a, b: a + b)
    s.add_tool("dividir", "Divide a entre b", SUMAR, lambda a, b: a / b)
    return s


def pedir(s, metodo, params=None, id=1):
    mensaje = {"jsonrpc": "2.0", "id": id, "method": metodo}
    if params is not None:
        mensaje["params"] = params
    return json.loads(s.handle_line(json.dumps(mensaje)))


def test_initialize_anuncia_capacidades_e_identidad(student):
    """initialize devuelve la versión pedida, las capacidades de tools y serverInfo"""
    r = pedir(servidor(student), "initialize", {"protocolVersion": "2025-06-18"})
    expect_equal(r["jsonrpc"], "2.0", what="jsonrpc")
    expect_equal(r["id"], 1, what="id")
    expect_equal(
        r["result"],
        {
            "protocolVersion": "2025-06-18",
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "nimbus", "version": "1.2.3"},
        },
        what="resultado de initialize",
    )


def test_tools_list_devuelve_las_herramientas_en_orden(student):
    """tools/list incluye nombre, descripción y esquema de entrada"""
    r = pedir(servidor(student), "tools/list")
    herramientas = r["result"]["tools"]
    expect_equal([t["name"] for t in herramientas], ["sumar", "dividir"], what="nombres")
    expect_equal(
        herramientas[0],
        {"name": "sumar", "description": "Suma dos enteros", "inputSchema": SUMAR},
        what="primera herramienta",
    )


def test_tools_call_devuelve_contenido_de_texto(student):
    """Una llamada correcta devuelve content con texto e isError False"""
    r = pedir(
        servidor(student), "tools/call", {"name": "sumar", "arguments": {"a": 2, "b": 3}}, id=7
    )
    expect_equal(r["id"], 7, what="el id se conserva")
    expect_equal(
        r["result"],
        {"content": [{"type": "text", "text": "5"}], "isError": False},
        what="resultado",
    )


def test_herramienta_desconocida_es_un_error_de_protocolo(student):
    """Una herramienta inexistente da el error JSON-RPC -32602"""
    r = pedir(servidor(student), "tools/call", {"name": "restar", "arguments": {}})
    expect_equal(r["error"], {"code": -32602, "message": "Unknown tool: restar"}, what="error")
    expect_true("result" not in r, "Una respuesta de error no debe llevar result.")


def test_los_fallos_de_la_herramienta_son_resultados_con_iserror(student):
    """Excepciones y argumentos que faltan NO son errores de protocolo"""
    s = servidor(student)
    division = pedir(s, "tools/call", {"name": "dividir", "arguments": {"a": 1, "b": 0}})
    expect_equal(
        division["result"],
        {
            "content": [{"type": "text", "text": "ZeroDivisionError: division by zero"}],
            "isError": True,
        },
        what="excepción de la herramienta",
    )
    falta = pedir(s, "tools/call", {"name": "sumar", "arguments": {"a": 1}})
    expect_equal(
        falta["result"],
        {
            "content": [{"type": "text", "text": "falta el argumento obligatorio: b"}],
            "isError": True,
        },
        what="argumento obligatorio ausente",
    )


def test_metodo_desconocido_y_ping(student):
    """-32601 para un método que no existe; ping devuelve un resultado vacío"""
    s = servidor(student)
    expect_equal(
        pedir(s, "resources/list")["error"],
        {"code": -32601, "message": "Method not found: resources/list"},
        what="método desconocido",
    )
    expect_equal(pedir(s, "ping")["result"], {}, what="ping")


def test_hidden_json_invalido_y_peticiones_invalidas(student):
    """Caso adicional: -32700 con id null y -32600 con el id si lo trae"""
    s = servidor(student)
    expect_equal(
        json.loads(s.handle_line("{esto no es json")),
        {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}},
        what="parse error",
    )
    sin_version = json.loads(s.handle_line(json.dumps({"id": 9, "method": "ping"})))
    expect_equal(sin_version["error"]["code"], -32600, what="falta jsonrpc")
    expect_equal(sin_version["id"], 9, what="id de la petición inválida")
    metodo_numerico = json.loads(
        s.handle_line(json.dumps({"jsonrpc": "2.0", "id": 3, "method": 5}))
    )
    expect_equal(
        (metodo_numerico["id"], metodo_numerico["error"]["code"]),
        (3, -32600),
        what="método no es texto",
    )
    otra_version = pedir(s, "initialize", {"protocolVersion": "2026-07-28"})
    expect_equal(otra_version["result"]["protocolVersion"], "2026-07-28", what="eco de la versión")
    lista = json.loads(s.handle_line("[1, 2]"))
    expect_equal((lista["id"], lista["error"]["code"]), (None, -32600), what="no es un objeto")


def test_hidden_las_notificaciones_no_se_responden(student):
    """Caso adicional: un mensaje sin id es una notificación y devuelve None"""
    s = servidor(student)
    notificacion = json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"})
    expect_equal(s.handle_line(notificacion), None, what="notificación")
    respuesta = s.handle_line(json.dumps({"jsonrpc": "2.0", "id": 0, "method": "ping"}))
    expect_true(respuesta is not None, "Un id 0 es una petición válida y debe responderse.")
