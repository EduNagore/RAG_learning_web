import re

from ragkit.llm import Message


def build_router_prompt(query, routes):
    """Prompt de clasificación: lista las rutas con su descripción y pide una sola etiqueta."""
    lines = "\n".join(f"- {name}: {description}" for name, description in routes.items())
    return (
        "Clasifica la consulta en UNA de estas rutas y responde solo con su nombre:\n"
        f"{lines}\n\nConsulta: {query}"
    )


def classify(query, routes, llm, default="otros"):
    """Una llamada al modelo; devuelve la primera ruta (en el orden de `routes`) que aparece como
    palabra completa en su respuesta, sin distinguir mayúsculas, o `default` si no aparece ninguna.
    """
    text = llm.generate([Message("user", build_router_prompt(query, routes))]).text or ""
    for name in routes:
        if re.search(rf"\b{re.escape(name)}\b", text, flags=re.IGNORECASE):
            return name
    return default


def route_and_run(query, routes, handlers, llm, default="otros"):
    """Clasifica y ejecuta el manejador de la ruta: {"route": ..., "result": handlers[route](query)}.

    Si la ruta elegida no tiene manejador, se usa el de `default`.
    """
    route = classify(query, routes, llm, default=default)
    if route not in handlers:
        route = default
    return {"route": route, "result": handlers[route](query)}


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    from ragkit.llm import MockLLM

    rutas = {"devoluciones": "plazos y reembolsos", "envios": "costes y seguimiento"}
    llm = MockLLM(script=["Devoluciones."])
    print(classify("¿Cuánto tarda el reembolso?", rutas, llm))
