class Blackboard:
    """Pizarra común: los agentes publican contribuciones y cualquiera puede leerlas."""

    def __init__(self):
        self._items = []  # {"author", "key", "value", "confidence", "seq"}
        self._seq = 0

    def post(self, author, key, value, confidence=1.0):
        """Publica una contribución. Devuelve su número de secuencia (1, 2, 3...)."""
        self._seq += 1
        self._items.append(
            {
                "author": author,
                "key": key,
                "value": value,
                "confidence": confidence,
                "seq": self._seq,
            }
        )
        return self._seq

    def contributions(self, key):
        """Contribuciones de la clave, en orden de publicación."""
        return [item for item in self._items if item["key"] == key]

    def read(self, key):
        """Valor con mayor confianza; a igualdad, el publicado más tarde. None si no hay."""
        items = self.contributions(key)
        if not items:
            return None
        return max(items, key=lambda i: (i["confidence"], i["seq"]))["value"]

    def count(self):
        return len(self._items)

    def has_consensus(self, key, quorum):
        """¿Hay al menos `quorum` autores distintos cuya ÚLTIMA contribución a la clave coincide?

        Devuelve el valor consensuado, o None. Si varios valores alcanzan el quórum, el que
        alcanzó antes su última contribución.
        """
        latest = {}
        for item in self.contributions(key):
            latest[item["author"]] = item  # la última de cada autor
        votes = {}
        for item in sorted(latest.values(), key=lambda i: i["seq"]):
            votes.setdefault(item["value"], []).append(item["author"])
            if len(votes[item["value"]]) >= quorum:
                return item["value"]
        return None


def run_blackboard(agents, board, max_rounds=5, done=lambda board: False):
    """Cada ronda, todos los agentes (en orden) leen la pizarra y pueden publicar.

    Se detiene con "done" (la función `done(board)` es verdadera, comprobada tras cada ronda),
    "quiescent" (una ronda completa sin nuevas contribuciones) o "max_rounds".
    Devuelve {"rounds": rondas ejecutadas, "stopped": motivo}.
    """
    for round_number in range(1, max_rounds + 1):
        before = board.count()
        for agent in agents:
            agent(board)
        if done(board):
            return {"rounds": round_number, "stopped": "done"}
        if board.count() == before:
            return {"rounds": round_number, "stopped": "quiescent"}
    return {"rounds": max_rounds, "stopped": "max_rounds"}


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    pizarra = Blackboard()
    pizarra.post("a", "plazo", "14 días", confidence=0.6)
    pizarra.post("b", "plazo", "7 días", confidence=0.9)
    print(pizarra.read("plazo"))
