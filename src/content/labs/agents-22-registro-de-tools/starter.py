from ragkit.agents import ToolSpec


class ToolRegistry:
    """Registro de herramientas con validación de argumentos contra un JSON Schema simplificado.

    El esquema de cada herramienta es un diccionario como:
        {"type": "object",
         "properties": {"a": {"type": "integer"}, "modo": {"type": "string", "enum": ["x", "y"]}},
         "required": ["a"]}
    Tipos admitidos: string, integer, number, boolean, array y object.
    """

    def __init__(self):
        self._tools = {}  # nombre -> (función, ToolSpec), en orden de registro

    def register(self, name, func, description, parameters):
        """Registra una herramienta. Lanza ValueError si el nombre ya existe."""
        # TODO
        raise NotImplementedError("Completa register")

    def specs(self):
        """Lista de ToolSpec (de ragkit.agents) en el orden de registro."""
        # TODO
        raise NotImplementedError("Completa specs")

    def validate(self, name, args):
        """Lista de errores en español (vacía si los argumentos son válidos). Mensajes exactos:

        - herramienta desconocida:  "herramienta desconocida: <nombre>"
        - falta un obligatorio:     "falta el argumento obligatorio: <arg>"
        - argumento no declarado:   "argumento no esperado: <arg>"
        - tipo incorrecto:          "el argumento '<arg>' debe ser <tipo>"
        - fuera del enum:           "el argumento '<arg>' debe ser uno de <lista del enum>"

        Primero los obligatorios que faltan (en el orden de `required`) y después, en el orden
        de `args`, los demás errores. Un booleano NO es un integer ni un number.
        """
        # TODO
        raise NotImplementedError("Completa validate")

    def call(self, name, args):
        """Valida y ejecuta la herramienta con **args.

        - Con errores de validación: {"ok": False, "error": "; ".join(errores)}.
        - Si la función lanza una excepción: {"ok": False, "error": "<Tipo>: <mensaje>"}.
        - Si todo va bien: {"ok": True, "result": <valor devuelto>}.
        """
        # TODO
        raise NotImplementedError("Completa call")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    registro = ToolRegistry()
    try:
        registro.register(
            "sumar",
            lambda a, b: a + b,
            "Suma dos enteros",
            {
                "type": "object",
                "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
                "required": ["a", "b"],
            },
        )
        print(registro.call("sumar", {"a": 2, "b": 3}))
        print(registro.call("sumar", {"a": "2"}))
    except NotImplementedError as e:
        print("Aún por completar:", e)
