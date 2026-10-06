import re

from ragkit.llm import Message


def build_router_prompt(query, routes):
    """Prompt de clasificación para el modelo.

    routes: dict nombre -> descripción. El prompt debe contener cada ruta con su descripción,
    la consulta y la instrucción de responder solo con el nombre de la ruta.
    """
    # TODO
    raise NotImplementedError("Completa build_router_prompt")


def classify(query, routes, llm, default="otros"):
    """Una única llamada a llm.generate con el prompt anterior.

    Devuelve la primera ruta (en el orden de `routes`) que aparezca como PALABRA COMPLETA en la
    respuesta del modelo, sin distinguir mayúsculas; si no aparece ninguna, devuelve `default`.
    El texto del modelo es `respuesta.text` (puede ser None).
    """
    # TODO
    raise NotImplementedError("Completa classify")


def route_and_run(query, routes, handlers, llm, default="otros"):
    """Clasifica y ejecuta el manejador de la ruta elegida.

    Devuelve {"route": ruta, "result": handlers[ruta](query)}. Si la ruta elegida no tiene
    manejador en `handlers`, se usa `default` (y route vale `default`).
    """
    # TODO
    raise NotImplementedError("Completa route_and_run")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    from ragkit.llm import MockLLM

    rutas = {"devoluciones": "plazos y reembolsos", "envios": "costes y seguimiento"}
    llm = MockLLM(script=["Devoluciones."])
    try:
        print(classify("¿Cuánto tarda el reembolso?", rutas, llm))
    except NotImplementedError as e:
        print("Aún por completar:", e)
