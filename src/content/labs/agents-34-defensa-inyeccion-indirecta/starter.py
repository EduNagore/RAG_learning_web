def wrap_untrusted(text, source):
    """Encierra contenido externo en un bloque de datos que no puede cerrarse desde dentro.

    Devuelve exactamente:
        <datos_no_fiables fuente="{source}">
        {text}
        </datos_no_fiables>
    con estas dos precauciones: dentro de `text`, cualquier aparición de "</datos_no_fiables"
    se sustituye por "&lt;/datos_no_fiables" (para que el contenido no pueda cerrar el bloque),
    y en `source` las comillas dobles " se sustituyen por comillas simples '.
    """
    # TODO
    raise NotImplementedError("Completa wrap_untrusted")


class ToolGate:
    """Puerta de herramientas: lista blanca, rotura de la tríada letal y aprobación humana.

    allowed:   nombres de herramientas permitidas para esta tarea (lista blanca).
    private:   herramientas que leen datos privados.
    external:  herramientas que comunican hacia fuera (correo, HTTP, publicar...).
    sensitive: herramientas con efectos que requieren aprobación si el contexto está contaminado.
    Atributos: tainted (el contexto contiene contenido no fiable) y has_private (el contexto
    contiene datos privados), ambos False al empezar.
    """

    def __init__(self, allowed, private=(), external=(), sensitive=()):
        # TODO
        raise NotImplementedError("Completa __init__")

    def observe(self, tool, untrusted=False):
        """Registra que la salida de `tool` ha entrado en el contexto del modelo.

        Si untrusted es True, el contexto queda contaminado (tainted). Si `tool` está en
        `private`, el contexto contiene datos privados (has_private).
        """
        # TODO
        raise NotImplementedError("Completa observe")

    def authorize(self, tool, approved=False):
        """Decide si se puede ejecutar `tool` ahora. Devuelve {"allow": bool, "reason": str}.

        Se aplican en este orden:
          1. `tool` no está en allowed                       -> {"allow": False, "reason": "not_allowed"}
          2. `tool` es external y hay contaminación Y datos privados
                                                             -> {"allow": False, "reason": "trifecta"}
             (ni la aprobación humana lo anula: se rompe la tríada letal)
          3. `tool` es sensitive, el contexto está contaminado y NO hay aprobación
                                                             -> {"allow": False, "reason": "needs_approval"}
          4. en cualquier otro caso                          -> {"allow": True, "reason": "ok"}
        """
        # TODO
        raise NotImplementedError("Completa authorize")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    try:
        gate = ToolGate(["leer_correos", "leer_web", "enviar_correo"], private=["leer_correos"], external=["enviar_correo"])
        gate.observe("leer_correos")
        gate.observe("leer_web", untrusted=True)
        print(gate.authorize("enviar_correo"))
    except NotImplementedError as e:
        print("Aún por completar:", e)
