import json

PARSE_ERROR, INVALID_REQUEST, METHOD_NOT_FOUND, INVALID_PARAMS = -32700, -32600, -32601, -32602


class MCPServer:
    """Servidor MCP de juguete: JSON-RPC 2.0 con initialize, ping, tools/list y tools/call."""

    def __init__(self, name, version="0.1.0"):
        self.name = name
        self.version = version
        self._tools = {}  # nombre -> (descripción, esquema, función), en orden de registro

    def add_tool(self, name, description, input_schema, handler):
        """Registra una herramienta (ya resuelta)."""
        self._tools[name] = (description, input_schema, handler)

    def handle_line(self, line):
        """Procesa una línea de texto con un mensaje JSON-RPC y devuelve la respuesta como TEXTO
        JSON (json.dumps), o None si el mensaje era una notificación (no lleva "id").

        Errores (respuesta con {"jsonrpc": "2.0", "id": ..., "error": {"code", "message"}}):
          - JSON inválido                                   -> -32700 "Parse error" (id None)
          - no es un objeto, o jsonrpc != "2.0", o "method" no es texto
                                                            -> -32600 "Invalid Request"
                                                               (id del mensaje si lo trae; si no, None)
          - método desconocido                              -> -32601 "Method not found: <método>"
          - tools/call con una herramienta inexistente      -> -32602 "Unknown tool: <nombre>"
        Métodos (el resultado va en {"jsonrpc": "2.0", "id": ..., "result": ...}):
          - "initialize": {"protocolVersion": params.get("protocolVersion"),
                           "capabilities": {"tools": {"listChanged": False}},
                           "serverInfo": {"name": self.name, "version": self.version}}
          - "ping": {}
          - "tools/list": {"tools": [{"name", "description", "inputSchema"}, ...]} en orden de registro
          - "tools/call": params {"name", "arguments"}. Si va bien:
                {"content": [{"type": "text", "text": str(valor)}], "isError": False}.
                Si faltan argumentos obligatorios del esquema (primer faltante) o la función lanza
                una excepción, NO es un error de protocolo: se devuelve un resultado con
                "isError": True y el texto "falta el argumento obligatorio: <arg>" o
                "<Tipo>: <mensaje>".
        Una notificación es un mensaje válido sin "id": se ignora y se devuelve None.
        """
        # TODO
        raise NotImplementedError("Completa handle_line")


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
    try:
        print(servidor.handle_line(json.dumps(peticion)))
    except NotImplementedError as e:
        print("Aún por completar:", e)
