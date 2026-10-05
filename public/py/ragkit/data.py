"""Acceso al corpus ficticio de Nimbus Logística y a su conjunto de evaluación (golden set).

La empresa, sus políticas, cifras y personas son inventadas; sirven solo para practicar.
Estructura esperada (la misma en el repo y en el sistema de archivos virtual de Pyodide):

    <raíz>/py/ragkit/data.py
    <raíz>/data/nimbus/corpus.json
    <raíz>/data/nimbus/golden.json
"""

import json
import os
from pathlib import Path


def data_dir() -> Path:
    """Directorio de datos. Se puede forzar con la variable de entorno RAGKIT_DATA_DIR."""
    override = os.environ.get("RAGKIT_DATA_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[2] / "data" / "nimbus"


def load_corpus() -> list[dict]:
    """Lista de documentos: id, title, text, department, kind, updated, access.

    `access` es "public", "internal" o "restricted".
    """
    return json.loads((data_dir() / "corpus.json").read_text(encoding="utf-8"))


def load_golden() -> list[dict]:
    """Preguntas de evaluación: id, question, relevant_ids, reference_answer, answerable.

    Las preguntas con `answerable: false` no tienen respuesta en el corpus: un buen sistema
    debe abstenerse. `requires_access` indica el nivel mínimo para ver la evidencia.
    """
    return json.loads((data_dir() / "golden.json").read_text(encoding="utf-8"))
