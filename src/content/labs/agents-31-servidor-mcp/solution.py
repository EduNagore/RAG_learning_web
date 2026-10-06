import json

PARSE_ERROR, INVALID_REQUEST, METHOD_NOT_FOUND, INVALID_PARAMS = -32700, -32600, -32601, -32602


class MCPServer:
    """Servidor MCP de juguete: JSON-RPC 2.0 con initialize, ping, tools/list y tools/call."""

    def __init__(self, name, version="0.1.0"):
        self.name = name
        self.version = version
        self._tools = {}  # nombre -> (descripción, esquema, función), en orden de registro

    def add_tool(self, name, description, input_schema, handler):
        self._tools[name] = (description, input_schema, handler)

    @staticmethod
    def _error(request_id, code, message):
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}

    def handle_line(self, line):
        """Procesa una línea de texto con un mensaje JSON-RPC y devuelve la respuesta como texto
        JSON, o None si el mensaje era una notificación (no lleva "id").
        """
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            return json.dumps(self._error(None, PARSE_ERROR, "Parse error"))
        if (
            not isinstance(message, dict)
            or message.get("jsonrpc") != "2.0"
            or not isinstance(message.get("method"), str)
        ):
            request_id = message.get("id") if isinstance(message, dict) else None
            return json.dumps(self._error(request_id, INVALID_REQUEST, "Invalid Request"))
        if "id" not in message:  # notificación: se procesa, pero no se responde
            return None
        response = self._dispatch(message["id"], message["method"], message.get("params") or {})
        return json.dumps(response, ensure_ascii=False)

    def _dispatch(self, request_id, method, params):
        if method == "initialize":
            result = {
                "protocolVersion": params.get("protocolVersion"),
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": self.name, "version": self.version},
            }
        elif method == "ping":
            result = {}
        elif method == "tools/list":
            result = {
                "tools": [
                    {"name": n, "description": d, "inputSchema": s}
                    for n, (d, s, _) in self._tools.items()
                ]
            }
        elif method == "tools/call":
            return self._call_tool(request_id, params)
        else:
            return self._error(request_id, METHOD_NOT_FOUND, f"Method not found: {method}")
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    def _call_tool(self, request_id, params):
        name = params.get("name")
        if name not in self._tools:
            return self._error(request_id, INVALID_PARAMS, f"Unknown tool: {name}")
        arguments = params.get("arguments") or {}
        _, schema, handler = self._tools[name]
        missing = [a for a in schema.get("required", []) if a not in arguments]
        if missing:
            text, is_error = f"falta el argumento obligatorio: {missing[0]}", True
        else:
            try:
                text, is_error = str(handler(**arguments)), False
            except Exception as e:  # noqa: BLE001 - es un error de ejecución de la herramienta
                text, is_error = f"{type(e).__name__}: {e}", True
        result = {"content": [{"type": "text", "text": text}], "isError": is_error}
        return {"jsonrpc": "2.0", "id": request_id, "result": result}


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    servidor = MCPServer("nimbus")
    servidor.add_tool(
        "sumar",
        "Suma dos enteros",
        {
            "type": "object",
            "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
            "required": ["a", "b"],
        },
        lambda a, b: a + b,
    )
    peticion = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "sumar", "arguments": {"a": 2, "b": 3}},
    }
    print(servidor.handle_line(json.dumps(peticion)))
