class Blackboard:
    """Pizarra común: los agentes publican contribuciones y cualquiera puede leerlas."""

    def __init__(self):
        self._items = []  # cada contribución: {"author", "key", "value", "confidence", "seq"}
        self._seq = 0

    def post(self, author, key, value, confidence=1.0):
        """Publica una contribución y devuelve su número de secuencia (1, 2, 3...)."""
        # TODO
        raise NotImplementedError("Completa post")

    def contributions(self, key):
        """Contribuciones (diccionarios) de la clave, en orden de publicación."""
        # TODO
        raise NotImplementedError("Completa contributions")

    def read(self, key):
        """Valor de la contribución con mayor confianza; a igualdad, la publicada más tarde.

        None si no hay contribuciones para la clave.
        """
        # TODO
        raise NotImplementedError("Completa read")

    def count(self):
        """Número total de contribuciones en la pizarra."""
        # TODO
        raise NotImplementedError("Completa count")

    def has_consensus(self, key, quorum):
        """¿Hay al menos `quorum` autores distintos cuya ÚLTIMA contribución a la clave coincide?

        Cada autor cuenta una sola vez, con su contribución más reciente. Devuelve el valor
        consensuado o None. Si varios valores alcanzan el quórum, gana el que lo alcanzó antes
        (recorriendo las últimas contribuciones por orden de publicación).
        """
        # TODO
        raise NotImplementedError("Completa has_consensus")


def run_blackboard(agents, board, max_rounds=5, done=lambda board: False):
    """Cada ronda, todos los agentes (funciones agente(board), en orden) pueden publicar.

    Tras cada ronda: si done(board) es verdadero, devuelve {"rounds": n, "stopped": "done"};
    si la ronda no añadió ninguna contribución, {"rounds": n, "stopped": "quiescent"}.
    Si se agotan las rondas, {"rounds": max_rounds, "stopped": "max_rounds"}.
    """
    # TODO
    raise NotImplementedError("Completa run_blackboard")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    pizarra = Blackboard()
    try:
        pizarra.post("a", "plazo", "14 días", confidence=0.6)
        pizarra.post("b", "plazo", "7 días", confidence=0.9)
        print(pizarra.read("plazo"))
    except NotImplementedError as e:
        print("Aún por completar:", e)
