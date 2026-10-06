import numpy as np


def _cumple(metadata, where):
    """True si la entrada cumple todas las condiciones de `where`."""
    for campo, esperado in where.items():
        valor = metadata.get(campo)
        if isinstance(esperado, (list, tuple, set, frozenset)):
            if valor not in esperado:
                return False
        elif valor != esperado:
            return False
    return True


class VectorIndex:
    """Índice vectorial en memoria con búsqueda por coseno y filtro de metadatos.

    - add(id, vector, metadata=None): inserta o REEMPLAZA; guarda el vector normalizado.
      ValueError si la longitud no es `dim` o si es el vector cero.
    - delete(id): True si existía, False si no.
    - len(index): número de entradas.
    - search(query, k=3, where=None): [(id, coseno)] de mayor a menor, como mucho k.
      `where` = {campo: valor}; cumple si TODOS los campos coinciden (si el valor es lista,
      tupla o conjunto, basta con que el metadato sea uno de ellos).
      El filtro se aplica ANTES de buscar. Empates: gana el insertado antes.
    """

    def __init__(self, dim):
        self.dim = dim
        self._entries = {}  # id -> (vector normalizado, metadatos); conserva el orden de inserción

    def _check(self, vector):
        v = np.asarray(vector, dtype=float)
        if v.shape != (self.dim,):
            raise ValueError(f"se esperaba un vector de {self.dim} componentes")
        return v

    def add(self, id, vector, metadata=None):
        v = self._check(vector)
        norm = np.linalg.norm(v)
        if norm == 0:
            raise ValueError("no se puede indexar el vector cero")
        self._entries[id] = (v / norm, dict(metadata or {}))

    def delete(self, id):
        return self._entries.pop(id, None) is not None

    def __len__(self):
        return len(self._entries)

    def search(self, query, k=3, where=None):
        q = self._check(query)
        norm = np.linalg.norm(q)
        if norm == 0 or k <= 0:
            return []
        q = q / norm

        # Prefiltrado: solo se puntúan las entradas que cumplen la condición.
        candidatos = [
            (id, vec)
            for id, (vec, meta) in self._entries.items()
            if not where or _cumple(meta, where)
        ]
        if not candidatos:
            return []
        ids = [id for id, _ in candidatos]
        scores = np.vstack([vec for _, vec in candidatos]) @ q
        orden = np.argsort(-scores, kind="stable")[:k]
        return [(ids[i], float(scores[i])) for i in orden]


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    index = VectorIndex(dim=2)
    index.add("a", [1, 0], {"dep": "envíos"})
    index.add("b", [0.9, 0.1], {"dep": "envíos"})
    index.add("c", [0, 1], {"dep": "facturación"})
    print(index.search([1, 0], k=2))
    print(index.search([1, 0], k=2, where={"dep": "facturación"}))
