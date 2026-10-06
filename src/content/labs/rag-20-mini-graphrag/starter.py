import networkx as nx
from ragkit.text import strip_accents


def normalize_entity(name):
    """Sin acentos, en minúsculas (casefold) y con los espacios colapsados.

    "Envío  Exprés" y "envio exprés" deben dar el mismo resultado.
    """
    # TODO
    raise NotImplementedError("Completa normalize_entity")


def build_graph(triples):
    """nx.MultiDiGraph con un nodo por entidad NORMALIZADA.

    triples: lista de (sujeto, relación, objeto). Cada tripleta es una arista dirigida
    sujeto -> objeto con key=relación. Una tripleta repetida no duplica la arista.
    """
    # TODO
    raise NotImplementedError("Completa build_graph")


def neighbors_within(graph, entity, hops):
    """Lista ORDENADA de entidades alcanzables en como mucho `hops` saltos, ignorando la
    dirección de las aristas y sin incluir la propia entidad. `entity` se normaliza.
    Si no existe en el grafo, devuelve [].
    """
    # TODO
    raise NotImplementedError("Completa neighbors_within")


def follow_relations(graph, start, relations):
    """Parte de `start` (normalizado) y sigue en orden las relaciones de `relations`.

    En cada paso se mueve al destino de una arista SALIENTE con esa relación (si hay varios,
    el primero por orden alfabético). Devuelve la entidad final, o None si alguna relación
    no existe en algún paso o `start` no está en el grafo.
    """
    # TODO
    raise NotImplementedError("Completa follow_relations")


def find_communities(graph):
    """Comunidades del grafo no dirigido (nx.community.greedy_modularity_communities).

    Devuelve una lista de listas: cada comunidad ordenada y las comunidades de mayor a menor
    tamaño (desempate por su primera entidad).
    """
    # TODO
    raise NotImplementedError("Completa find_communities")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    try:
        g = build_graph(
            [
                ("Envío exprés", "gestionado_por", "Equipo de Envíos"),
                ("Equipo de Envíos", "responsable", "Marta Ruiz"),
            ]
        )
        print(follow_relations(g, "envio exprés", ["gestionado_por", "responsable"]))
    except NotImplementedError as e:
        print("Aún por completar:", e)
