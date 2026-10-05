import numpy as np


def _normalize_rows(M):
    norms = np.linalg.norm(M, axis=1, keepdims=True)
    return M / np.where(norms == 0, 1, norms)


def kmeans(X, n_clusters, n_iters=10, seed=0):
    """K-means esférico. Devuelve centroides normalizados de forma (n_clusters, d).

    - Inicialización: rng = np.random.default_rng(seed); rng.choice(len(X), n_clusters, replace=False)
    - Asigna cada vector al centroide de mayor producto escalar; recalcula como media normalizada.
    - Un grupo vacío conserva su centroide. ValueError si n_clusters > len(X).
    """
    X = np.asarray(X, dtype=float)
    if n_clusters > len(X):
        raise ValueError("n_clusters no puede superar el número de vectores")
    rng = np.random.default_rng(seed)
    centroids = _normalize_rows(X[rng.choice(len(X), n_clusters, replace=False)])
    for _ in range(n_iters):
        assignment = np.argmax(X @ centroids.T, axis=1)
        for j in range(n_clusters):
            members = X[assignment == j]
            if len(members):
                mean = members.mean(axis=0)
                norm = np.linalg.norm(mean)
                if norm > 0:
                    centroids[j] = mean / norm
    return centroids


def build_ivf(X, n_lists, seed=0):
    """Devuelve {"centroids": array, "lists": [array de índices por lista]}.

    Cada vector está en exactamente una lista (la de su centroide más similar).
    """
    X = np.asarray(X, dtype=float)
    centroids = kmeans(X, n_lists, seed=seed)
    assignment = np.argmax(X @ centroids.T, axis=1)
    lists = [np.flatnonzero(assignment == j) for j in range(n_lists)]
    return {"centroids": centroids, "lists": lists}


def ivf_search(query, X, index, k=10, n_probe=1):
    """Busca visitando solo las n_probe listas más cercanas. Devuelve (ids, n_candidatos).

    ids: índices en X de los k mejores, de mayor a menor similitud (empate: índice menor).
    n_candidatos: cuántos vectores se han revisado.
    """
    X = np.asarray(X, dtype=float)
    q = np.asarray(query, dtype=float)
    nearest_lists = np.argsort(-(index["centroids"] @ q), kind="stable")[:n_probe]
    candidates = np.sort(np.concatenate([index["lists"][j] for j in nearest_lists]))
    if len(candidates) == 0:
        return np.array([], dtype=int), 0
    order = np.argsort(-(X[candidates] @ q), kind="stable")[:k]
    return candidates[order], len(candidates)


def recall_at_k(approx_ids, exact_ids):
    """Fracción de exact_ids presentes en approx_ids (1.0 si exact_ids está vacío)."""
    exact = {int(i) for i in exact_ids}
    if not exact:
        return 1.0
    return len(exact & {int(i) for i in approx_ids}) / len(exact)


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    rng = np.random.default_rng(1)
    X = rng.normal(size=(500, 8))
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    index = build_ivf(X, n_lists=10)
    exact = np.argsort(-(X @ X[0]))[:5]
    ids, n = ivf_search(X[0], X, index, k=5, n_probe=2)
    print(ids, n, recall_at_k(ids, exact))
