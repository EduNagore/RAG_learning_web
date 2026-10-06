import networkx as nx
from ragkit.text import strip_accents


def normalize_entity(name):
    """Sin acentos, en minúsculas y con los espacios colapsados."""
    return " ".join(strip_accents(name).casefold().split())


def build_graph(triples):
    """MultiDiGraph con un nodo por entidad normalizada y una arista (clave = relación)."""
    graph = nx.MultiDiGraph()
    for subject, relation, obj in triples:
        graph.add_edge(normalize_entity(subject), normalize_entity(obj), key=relation)
    return graph


def neighbors_within(graph, entity, hops):
    """Entidades alcanzables en como mucho `hops` saltos, ignorando la dirección."""
    start = normalize_entity(entity)
    if start not in graph:
        return []
    reachable = nx.single_source_shortest_path_length(
        graph.to_undirected(as_view=True), start, cutoff=hops
    )
    return sorted(node for node in reachable if node != start)


def follow_relations(graph, start, relations):
    """Sigue una cadena de relaciones salientes y devuelve la entidad final (o None)."""
    current = normalize_entity(start)
    if current not in graph:
        return None
    for relation in relations:
        targets = sorted(t for _, t, key in graph.out_edges(current, keys=True) if key == relation)
        if not targets:
            return None
        current = targets[0]
    return current


def find_communities(graph):
    """Comunidades del grafo no dirigido, ordenadas de mayor a menor tamaño."""
    undirected = nx.Graph(graph.to_undirected(as_view=True))
    communities = [sorted(c) for c in nx.community.greedy_modularity_communities(undirected)]
    return sorted(communities, key=lambda c: (-len(c), c[0]))


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    g = build_graph(
        [
            ("Envío exprés", "gestionado_por", "Equipo de Envíos"),
            ("Equipo de Envíos", "responsable", "Marta Ruiz"),
        ]
    )
    print(follow_relations(g, "envio exprés", ["gestionado_por", "responsable"]))
