from ragkit.agents import ToolSpec

_TYPES = {
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "array": lambda v: isinstance(v, list),
    "object": lambda v: isinstance(v, dict),
}


class ToolRegistry:
    """Registro de herramientas con validación de argumentos contra un JSON Schema simplificado."""

    def __init__(self):
        self._tools = {}  # nombre -> (función, ToolSpec), en orden de registro

    def register(self, name, func, description, parameters):
        """Registra una herramienta. ValueError si el nombre ya existe."""
        if name in self._tools:
            raise ValueError(f"la herramienta '{name}' ya está registrada")
        spec = ToolSpec(name, description, parameters)
        self._tools[name] = (func, spec)

    def specs(self):
        """Lista de ToolSpec en el orden de registro (lo que se le presenta al modelo)."""
        return [spec for _, spec in self._tools.values()]

    def validate(self, name, args):
        """Lista de errores (vacía si los argumentos son válidos)."""
        if name not in self._tools:
            return [f"herramienta desconocida: {name}"]
        schema = self._tools[name][1].parameters
        properties = schema.get("properties", {})
        errors = []
        for required in schema.get("required", []):
            if required not in args:
                errors.append(f"falta el argumento obligatorio: {required}")
        for key, value in args.items():
            if key not in properties:
                errors.append(f"argumento no esperado: {key}")
                continue
            prop = properties[key]
            expected = prop.get("type")
            if expected in _TYPES and not _TYPES[expected](value):
                errors.append(f"el argumento '{key}' debe ser {expected}")
            elif "enum" in prop and value not in prop["enum"]:
                errors.append(f"el argumento '{key}' debe ser uno de {prop['enum']}")
        return errors

    def call(self, name, args):
        """Valida y ejecuta. Devuelve {"ok": True, "result": ...} o {"ok": False, "error": "..."}."""
        errors = self.validate(name, args)
        if errors:
            return {"ok": False, "error": "; ".join(errors)}
        try:
            return {"ok": True, "result": self._tools[name][0](**args)}
        except Exception as e:  # noqa: BLE001 - el error se devuelve al modelo como observación
            return {"ok": False, "error": f"{type(e).__name__}: {e}"}


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    registro = ToolRegistry()
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
