def wrap_untrusted(text, source):
    """Encierra contenido externo en un bloque de datos que no puede cerrarse desde dentro."""
    seguro = text.replace("</datos_no_fiables", "&lt;/datos_no_fiables")
    fuente = source.replace('"', "'")
    return f'<datos_no_fiables fuente="{fuente}">\n{seguro}\n</datos_no_fiables>'


class ToolGate:
    """Puerta de herramientas: lista blanca, rotura de la tríada letal y aprobación humana."""

    def __init__(self, allowed, private=(), external=(), sensitive=()):
        self.allowed = set(allowed)
        self.private = set(private)
        self.external = set(external)
        self.sensitive = set(sensitive)
        self.tainted = False
        self.has_private = False

    def observe(self, tool, untrusted=False):
        """Registra que la salida de `tool` ha entrado en el contexto del modelo."""
        if untrusted:
            self.tainted = True
        if tool in self.private:
            self.has_private = True

    def authorize(self, tool, approved=False):
        """Decide si se puede ejecutar `tool` ahora. Devuelve {"allow": bool, "reason": str}."""
        if tool not in self.allowed:
            return {"allow": False, "reason": "not_allowed"}
        if tool in self.external and self.tainted and self.has_private:
            return {"allow": False, "reason": "trifecta"}
        if tool in self.sensitive and self.tainted and not approved:
            return {"allow": False, "reason": "needs_approval"}
        return {"allow": True, "reason": "ok"}
