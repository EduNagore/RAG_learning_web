"""Comprobaciones con mensajes en español para los tests de los laboratorios."""

import math


def expect_equal(actual, expected, what: str = "el resultado") -> None:
    if actual != expected:
        raise AssertionError(
            f"{what}: se esperaba {expected!r} pero tu código devolvió {actual!r}."
        )


def expect_close(actual, expected, tol: float = 1e-6, what: str = "el valor") -> None:
    if not math.isclose(float(actual), float(expected), rel_tol=tol, abs_tol=tol):
        raise AssertionError(
            f"{what}: se esperaba ≈ {expected!r} pero tu código devolvió {actual!r}."
        )


def expect_true(condition, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expect_raises(exception_type, func, *args, what: str = "la llamada", **kwargs) -> None:
    try:
        func(*args, **kwargs)
    except exception_type:
        return
    except Exception as e:  # noqa: BLE001
        raise AssertionError(
            f"{what}: se esperaba {exception_type.__name__} pero se lanzó {type(e).__name__}: {e}."
        ) from None
    raise AssertionError(
        f"{what}: se esperaba que lanzara {exception_type.__name__}, pero no lanzó nada."
    )
