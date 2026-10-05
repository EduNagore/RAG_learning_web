"""Valida todos los laboratorios con el MISMO ejecutor que usa el navegador (ragkit.labrunner).

Para cada laboratorio:
- están los cuatro archivos;
- la solución de referencia pasa TODOS los tests;
- el código inicial (starter) carga sin errores pero NO pasa todos los tests;
- hay al menos 4 tests y al menos uno oculto.
"""

from pathlib import Path

import pytest
from ragkit.labrunner import run_lab

LABS_DIR = Path(__file__).resolve().parents[2] / "src" / "content" / "labs"
LAB_IDS = sorted(p.name for p in LABS_DIR.iterdir() if p.is_dir()) if LABS_DIR.exists() else []
REQUIRED = ("index.mdx", "starter.py", "solution.py", "test_lab.py")


@pytest.fixture(params=LAB_IDS)
def lab_id(request):
    return request.param


def _read(lab_id: str, name: str) -> str:
    return (LABS_DIR / lab_id / name).read_text(encoding="utf-8")


def _failures(report: dict) -> list[str]:
    return [f"{r['name']}: {r['message']}" for r in report["results"] if not r["passed"]]


def test_hay_laboratorios():
    assert LAB_IDS, "No se encontró ningún laboratorio en src/content/labs"


def test_archivos_requeridos(lab_id):
    for name in REQUIRED:
        assert (LABS_DIR / lab_id / name).is_file(), f"{lab_id}: falta {name}"


def test_la_solucion_pasa_todos_los_tests(lab_id):
    report = run_lab(_read(lab_id, "solution.py"), _read(lab_id, "test_lab.py"))
    assert report["load_error"] is None, f"{lab_id}: la solución no carga: {report['load_error']}"
    assert report["results"], f"{lab_id}: no se ejecutó ningún test"
    assert not _failures(report), f"{lab_id}: la solución falla:\n" + "\n".join(_failures(report))


def test_el_starter_carga_pero_no_pasa(lab_id):
    report = run_lab(_read(lab_id, "starter.py"), _read(lab_id, "test_lab.py"))
    assert report["load_error"] is None, f"{lab_id}: el starter no carga: {report['load_error']}"
    assert _failures(report), (
        f"{lab_id}: el starter ya pasa todos los tests (no hay nada que resolver)"
    )


def test_el_starter_no_contiene_la_solucion(lab_id):
    """El starter y la solución deben diferir; si no, el ejercicio ya está resuelto."""
    assert _read(lab_id, "starter.py").strip() != _read(lab_id, "solution.py").strip()


def test_estructura_de_los_tests(lab_id):
    report = run_lab(_read(lab_id, "solution.py"), _read(lab_id, "test_lab.py"))
    results = report["results"]
    assert len(results) >= 4, f"{lab_id}: se esperan al menos 4 tests y hay {len(results)}"
    assert any(r["hidden"] for r in results), (
        f"{lab_id}: falta al menos un test oculto (test_hidden_*)"
    )
    assert all(r["title"].strip() for r in results), (
        f"{lab_id}: todos los tests necesitan docstring"
    )
