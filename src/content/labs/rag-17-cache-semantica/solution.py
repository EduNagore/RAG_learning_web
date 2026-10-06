import numpy as np


class SemanticCache:
    """Caché semántica con umbral de similitud, límite de tamaño (LRU) y caducidad (TTL)."""

    def __init__(self, embed, threshold=0.9, max_size=100, ttl=None):
        self.embed = embed
        self.threshold = threshold
        self.max_size = max_size
        self.ttl = ttl
        self.entries = []  # el más reciente al final: {"vector", "query", "answer", "created"}
        self.hits = 0
        self.misses = 0

    def _unit(self, query):
        vector = np.asarray(self.embed(query), dtype=float)
        norm = np.linalg.norm(vector)
        return vector / norm if norm > 0 else vector

    def _expired(self, entry, now):
        return self.ttl is not None and now - entry["created"] > self.ttl

    def get(self, query, now=0):
        """Respuesta de la entrada más parecida con similitud >= threshold, o None."""
        self.entries = [e for e in self.entries if not self._expired(e, now)]
        vector = self._unit(query)
        best_index, best_score = None, -1.0
        for index, entry in enumerate(self.entries):
            score = float(entry["vector"] @ vector)
            if score > best_score:
                best_index, best_score = index, score
        if best_index is not None and best_score >= self.threshold:
            self.hits += 1
            best = self.entries.pop(best_index)
            self.entries.append(best)
            return best["answer"]
        self.misses += 1
        return None

    def put(self, query, answer, now=0):
        """Guarda la respuesta; si se supera max_size, expulsa la menos usada recientemente."""
        self.entries.append(
            {"vector": self._unit(query), "query": query, "answer": answer, "created": now}
        )
        while len(self.entries) > self.max_size:
            self.entries.pop(0)

    def stats(self):
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / total if total else 0.0,
            "size": len(self.entries),
        }


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    from ragkit.embeddings import HashingEmbedder

    cache = SemanticCache(HashingEmbedder().embed, threshold=0.8)
    cache.put("cuánto tarda el reembolso", "7 días hábiles")
    print(cache.get("cuánto tarda el reembolso"), cache.get("horario del chat"), cache.stats())
