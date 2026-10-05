import numpy as np


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
        # TODO: estructura para guardar las entradas

    def add(self, id, vector, metadata=None):
        # TODO
        raise NotImplementedError("Completa add")

    def delete(self, id):
        # TODO
        raise NotImplementedError("Completa delete")

    def __len__(self):
        # TODO
        raise NotImplementedError("Completa __len__")

    def search(self, query, k=3, where=None):
        # TODO
        raise NotImplementedError("Completa search")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    index = VectorIndex(dim=2)
    try:
        index.add("a", [1, 0], {"dep": "envíos"})
        index.add("b", [0.9, 0.1], {"dep": "envíos"})
        index.add("c", [0, 1], {"dep": "facturación"})
        print(index.search([1, 0], k=2))
        print(index.search([1, 0], k=2, where={"dep": "facturación"}))
    except NotImplementedError as e:
        print("Aún por completar:", e)
