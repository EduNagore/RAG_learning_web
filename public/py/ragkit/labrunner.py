"""Ejecutor de laboratorios. Se usa tal cual en el navegador (Pyodide) y en CI (CPython).

Un laboratorio se compone del código del alumno y de un archivo de tests. Cada función
`test_*` del archivo de tests recibe como argumento el módulo del alumno (`student`):

    def test_devuelve_los_k_mejores(student):
        \"\"\"Devuelve los k vecinos más cercanos.\"\"\"
        indices, _ = student.cosine_top_k(...)
        assert list(indices) == [2, 0], "mensaje didáctico"

Las funciones cuyo nombre empieza por `test_hidden` son tests ocultos: la interfaz los muestra
con un nombre genérico para no dar la solución en el enunciado.
"""

import contextlib
import io
import types

STUDENT_FILE = "<tu-codigo>"
TESTS_FILE = "<tests>"
MAX_OUTPUT = 8000


def _clip(text: str) -> str:
    return text if len(text) <= MAX_OUTPUT else text[:MAX_OUTPUT] + "\n… (salida recortada)"


def _student_line(exc: BaseException) -> int | None:
    """Última línea del código del alumno que aparece en la traza del error."""
    line = None
    tb = exc.__traceback__
    while tb is not None:
        if tb.tb_frame.f_code.co_filename == STUDENT_FILE:
            line = tb.tb_lineno
        tb = tb.tb_next
    return line


def format_error(exc: BaseException) -> str:
    """Mensaje de error comprensible, con la línea del código del alumno si se conoce."""
    if isinstance(exc, SyntaxError):
        where = f" en la línea {exc.lineno}" if exc.lineno else ""
        return f"Error de sintaxis{where}: {exc.msg}"
    if isinstance(exc, AssertionError):
        return str(exc) or "La comprobación falló."
    line = _student_line(exc)
    where = f" (línea {line} de tu código)" if line else ""
    return f"{type(exc).__name__}: {exc}{where}"


def run_code(source: str) -> dict:
    """Ejecuta el código del alumno y devuelve su salida: {"stdout": str, "error": str | None}."""
    out = io.StringIO()
    error = None
    # Como "Ejecutar" simula lanzar el script, el código corre con __name__ == "__main__":
    # así el bloque `if __name__ == "__main__":` del starter solo se ejecuta aquí y no al comprobar.
    module = types.ModuleType("__main__")
    try:
        with contextlib.redirect_stdout(out):
            exec(compile(source, STUDENT_FILE, "exec"), module.__dict__)  # noqa: S102 - ejecutar código del alumno es el objetivo de este módulo
    except BaseException as e:  # noqa: BLE001
        error = format_error(e)
    return {"stdout": _clip(out.getvalue()), "error": error}


def _title(name: str, func) -> str:
    doc = (func.__doc__ or "").strip().splitlines()
    return doc[0].strip() if doc else name.removeprefix("test_").replace("_", " ")


def run_lab(student_source: str, test_source: str) -> dict:
    """Ejecuta los tests de un laboratorio sobre el código del alumno.

    Devuelve un diccionario serializable a JSON:
        {"load_error": str | None, "results": [{name, title, hidden, passed, message, stdout}]}
    """
    student = types.ModuleType("student")
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(student_source, STUDENT_FILE, "exec"), student.__dict__)  # noqa: S102 - ejecutar código del alumno es el objetivo de este módulo
    except BaseException as e:  # noqa: BLE001
        return {"load_error": format_error(e), "results": []}

    namespace: dict = {"__name__": "lab_tests"}
    exec(compile(test_source, TESTS_FILE, "exec"), namespace)  # noqa: S102 - ejecutar código del alumno es el objetivo de este módulo
    results = []
    for name, func in namespace.items():
        if not (name.startswith("test_") and callable(func)):
            continue
        out = io.StringIO()
        passed, message = True, ""
        try:
            with contextlib.redirect_stdout(out):
                func(student)
        except BaseException as e:  # noqa: BLE001
            passed, message = False, format_error(e)
        results.append(
            {
                "name": name,
                "title": _title(name, func),
                "hidden": name.startswith("test_hidden"),
                "passed": passed,
                "message": message,
                "stdout": _clip(out.getvalue()),
            }
        )
    return {"load_error": None, "results": results}
