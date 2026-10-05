"""Valida cada laboratorio: solution.py pasa su test_lab.py y starter.py no.

Se rellena en F3 junto al motor de labs; en F0 solo descubre los labs existentes.
"""

from pathlib import Path

import pytest

LABS_DIR = Path(__file__).resolve().parents[2] / "src" / "content" / "labs"
LAB_IDS = sorted(p.name for p in LABS_DIR.iterdir() if p.is_dir()) if LABS_DIR.exists() else []


@pytest.mark.parametrize(
    "lab_id", LAB_IDS or [pytest.param(None, marks=pytest.mark.skip(reason="aún no hay labs"))]
)
def test_lab_files_exist(lab_id):
    lab = LABS_DIR / lab_id
    for name in ("index.mdx", "starter.py", "solution.py", "test_lab.py"):
        assert (lab / name).is_file(), f"{lab_id}: falta {name}"
