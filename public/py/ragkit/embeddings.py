"""Embeddings deterministas para practicar la mecánica de la búsqueda vectorial.

`HashingEmbedder` usa el "hashing trick": cada palabra (y cada par de palabras seguidas) suma
o resta en una posición decidida por su hash. No entiende sinónimos como un modelo real, pero
textos que comparten palabras quedan cerca, y es 100 % reproducible.
"""

import zlib
from itertools import pairwise

import numpy as np

from .text import tokenize


class HashingEmbedder:
    def __init__(self, dim: int = 256, language: str = "es", use_bigrams: bool = True):
        self.dim = dim
        self.language = language
        self.use_bigrams = use_bigrams

    def _features(self, text: str) -> list[str]:
        tokens = tokenize(text, language=self.language)
        features = list(tokens)
        if self.use_bigrams:
            features += [f"{a}_{b}" for a, b in pairwise(tokens)]
        return features

    def embed(self, text: str) -> np.ndarray:
        """Vector de norma 1 (o de ceros si el texto no tiene palabras útiles)."""
        vec = np.zeros(self.dim, dtype=np.float64)
        for feature in self._features(text):
            h = zlib.crc32(feature.encode("utf-8"))
            index = h % self.dim
            sign = 1.0 if (h >> 16) & 1 else -1.0
            vec[index] += sign
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    def embed_many(self, texts: list[str]) -> np.ndarray:
        """Matriz de forma (n, dim) con un embedding por fila."""
        if not texts:
            return np.zeros((0, self.dim))
        return np.vstack([self.embed(t) for t in texts])
