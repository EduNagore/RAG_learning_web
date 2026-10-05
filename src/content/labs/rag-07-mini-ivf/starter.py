import numpy as np


def kmeans(X, n_clusters, n_iters=10, seed=0):
    """K-means esférico. Devuelve centroides normalizados de forma (n_clusters, d).

    - Inicialización: rng = np.random.default_rng(seed); rng.choice(len(X), n_clusters, replace=False)
    - Asigna cada vector al centroide de mayor producto escalar; recalcula como media normalizada.
    - Un grupo vacío conserva su centroide. ValueError si n_clusters > len(X).
    """
    # TODO
    raise NotImplementedError("Completa kmeans")


def build_ivf(X, n_lists, seed=0):
    """Devuelve {"centroids": array, "lists": [array de índices por lista]}.

    Cada vector está en exactamente una lista (la de su centroide más similar).
    """
    # TODO
    raise NotImplementedError("Completa build_ivf")


def ivf_search(query, X, index, k=10, n_probe=1):
    """Busca visitando solo las n_probe listas más cercanas. Devuelve (ids, n_candidatos).

    ids: índices en X de los k mejores, de mayor a menor similitud (empate: índice menor).
    n_candidatos: cuántos vectores se han revisado.
    """
    # TODO
    raise NotImplementedError("Completa ivf_search")


def recall_at_k(approx_ids, exact_ids):
    """Fracción de exact_ids presentes en approx_ids (1.0 si exact_ids está vacío)."""
    # TODO
    raise NotImplementedError("Completa recall_at_k")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    rng = np.random.default_rng(1)
    X = rng.normal(size=(500, 8))
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    try:
        index = build_ivf(X, n_lists=10)
        exact = np.argsort(-(X @ X[0]))[:5]
        ids, n = ivf_search(X[0], X, index, k=5, n_probe=2)
        print(ids, n, recall_at_k(ids, exact))
    except NotImplementedError as e:
        print("Aún por completar:", e)
