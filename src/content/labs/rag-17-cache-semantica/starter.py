import numpy as np


class SemanticCache:
    """Caché semántica con umbral de similitud, límite de tamaño (LRU) y caducidad (TTL).

    embed: función texto -> vector. threshold: similitud coseno mínima para considerar un acierto.
    max_size: número máximo de entradas (se expulsa la menos usada recientemente).
    ttl: segundos de vida de una entrada (None = no caduca). El tiempo se pasa con `now`.
    """

    def __init__(self, embed, threshold=0.9, max_size=100, ttl=None):
        self.embed = embed
        self.threshold = threshold
        self.max_size = max_size
        self.ttl = ttl
        self.entries = []  # el más reciente al final
        self.hits = 0
        self.misses = 0

    def get(self, query, now=0):
        """Respuesta de la entrada más parecida con similitud coseno >= threshold, o None.

        - Primero se descartan las entradas caducadas: now - created > ttl (justo igual NO caduca).
        - Si hay acierto: hits += 1 y la entrada pasa a ser la más reciente (LRU).
        - Si no: misses += 1 y devuelve None.
        """
        # TODO
        raise NotImplementedError("Completa get")

    def put(self, query, answer, now=0):
        """Guarda la respuesta con su vector y su instante de creación.

        Si se supera max_size, expulsa la entrada menos usada recientemente (la primera).
        """
        # TODO
        raise NotImplementedError("Completa put")

    def stats(self):
        """{"hits", "misses", "hit_rate" (0.0 si no hay consultas), "size"}."""
        # TODO
        raise NotImplementedError("Completa stats")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    from ragkit.embeddings import HashingEmbedder

    try:
        cache = SemanticCache(HashingEmbedder().embed, threshold=0.8)
        cache.put("cuánto tarda el reembolso", "7 días hábiles")
        print(cache.get("cuánto tarda el reembolso"), cache.get("horario del chat"), cache.stats())
    except NotImplementedError as e:
        print("Aún por completar:", e)
