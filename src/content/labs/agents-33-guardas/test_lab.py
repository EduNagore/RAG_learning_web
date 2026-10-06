from ragkit.testing import expect_equal


class Reloj:
    """Reloj falso: avanza solo cuando se le dice."""

    def __init__(self):
        self.t = 100.0

    def __call__(self):
        return self.t


def accion(i):
    return {"tool": "paso", "args": {"i": i}}


def test_sin_limites_alcanzados_continua(student):
    """Mientras no se supere ningún límite check devuelve None y acumula el consumo"""
    guard = student.AgentGuard(max_steps=3, max_tokens=100, max_cost=1.0)
    expect_equal(guard.check(accion(0), tokens=10, cost=0.1), None, what="paso 1")
    expect_equal(guard.check(accion(1), tokens=20, cost=0.2), None, what="paso 2")
    snap = guard.snapshot()
    expect_equal((snap["steps"], snap["tokens"], snap["stopped"]), (2, 30, None), what="estado")
    expect_equal(round(snap["cost"], 6), 0.3, what="coste acumulado")


def test_max_steps_permite_exactamente_ese_numero(student):
    """Con max_steps=3 se permiten 3 pasos y el 4.º para"""
    guard = student.AgentGuard(max_steps=3)
    motivos = [guard.check(accion(i)) for i in range(4)]
    expect_equal(motivos, [None, None, None, "max_steps"], what="motivos por paso")


def test_limites_de_tokens_y_coste(student):
    """Se para al SUPERAR el límite, no al alcanzarlo"""
    g1 = student.AgentGuard(max_tokens=50)
    expect_equal(g1.check(accion(0), tokens=50), None, what="justo en el límite de tokens")
    expect_equal(g1.check(accion(1), tokens=1), "max_tokens", what="supera tokens")
    g2 = student.AgentGuard(max_cost=0.5)
    expect_equal(g2.check(accion(0), cost=0.5), None, what="justo en el límite de coste")
    expect_equal(g2.check(accion(1), cost=0.01), "max_cost", what="supera coste")


def test_deteccion_de_bucle(student):
    """La misma acción repetida max_repeats veces para (la 3.ª con el valor por defecto)"""
    guard = student.AgentGuard(max_steps=50)
    igual = {"tool": "buscar", "args": {"q": "x"}}
    expect_equal([guard.check(igual) for _ in range(3)], [None, None, "loop"], what="motivos")
    otra = student.AgentGuard(max_steps=50)
    expect_equal(
        [otra.check(accion(i)) for i in range(5)],
        [None] * 5,
        what="acciones distintas no son bucle",
    )


def test_el_motivo_queda_fijado(student):
    """Tras parar, las llamadas siguientes devuelven el mismo motivo y no cuentan más pasos"""
    guard = student.AgentGuard(max_steps=1)
    guard.check(accion(0))
    expect_equal(guard.check(accion(1)), "max_steps", what="primera parada")
    expect_equal(guard.check(accion(2), tokens=999), "max_steps", what="se mantiene")
    snap = guard.snapshot()
    expect_equal((snap["steps"], snap["tokens"]), (2, 0), what="no se cuenta nada tras parar")


def test_timeout_con_reloj_inyectado(student):
    """timeout cuando pasan MÁS de timeout_s segundos desde que se creó la guarda"""
    reloj = Reloj()
    guard = student.AgentGuard(timeout_s=10, clock=reloj)
    reloj.t += 10
    expect_equal(guard.check(accion(0)), None, what="justo en el tiempo")
    reloj.t += 0.5
    expect_equal(guard.check(accion(1)), "timeout", what="pasado el tiempo")


def test_run_guarded_ejecuta_hasta_que_para(student):
    """run_guarded no ejecuta la acción que la guarda rechaza"""
    guard = student.AgentGuard(max_steps=3)
    out = student.run_guarded(lambda i: {"action": accion(i)}, guard)
    expect_equal(out["stopped"], "max_steps", what="motivo")
    expect_equal(out["executed"], [accion(0), accion(1), accion(2)], what="acciones ejecutadas")


def test_hidden_orden_de_los_motivos(student):
    """Caso adicional: si se cumplen varios límites a la vez, gana el primero de la lista"""
    reloj = Reloj()
    guard = student.AgentGuard(max_steps=0, max_tokens=1, max_cost=0.0, timeout_s=1, clock=reloj)
    reloj.t += 5
    expect_equal(
        guard.check(accion(0), tokens=5, cost=1.0), "timeout", what="timeout antes que pasos"
    )
    g2 = student.AgentGuard(max_steps=0, max_tokens=1, max_cost=0.0)
    expect_equal(
        g2.check(accion(0), tokens=5, cost=1.0), "max_steps", what="pasos antes que tokens"
    )
    g3 = student.AgentGuard(max_tokens=1, max_cost=0.0)
    expect_equal(
        g3.check(accion(0), tokens=5, cost=1.0), "max_tokens", what="tokens antes que coste"
    )
    g4 = student.AgentGuard(max_cost=0.0, max_repeats=1)
    expect_equal(g4.check(accion(0), cost=1.0), "max_cost", what="coste antes que bucle")


def test_hidden_bucle_con_argumentos_en_otro_orden_y_none(student):
    """Caso adicional: dos dicts con las mismas claves en otro orden son la misma acción; None no cuenta"""
    guard = student.AgentGuard(max_repeats=2)
    a = {"tool": "t", "args": {"x": 1, "y": 2}}
    b = {"args": {"y": 2, "x": 1}, "tool": "t"}
    expect_equal(guard.check(a), None, what="primera")
    expect_equal(guard.check(b), "loop", what="misma acción con otro orden de claves")
    solo_none = student.AgentGuard(max_repeats=2)
    expect_equal(
        [solo_none.check(None) for _ in range(4)], [None] * 4, what="sin acción no hay bucle"
    )


def test_hidden_run_guarded_termina_cuando_el_agente_acaba(student):
    """Caso adicional: si next_step devuelve None el motivo es 'done'; tokens y coste se acumulan"""
    guard = student.AgentGuard(max_tokens=100)
    pasos = [
        {"action": accion(0), "tokens": 30, "cost": 0.1},
        {"action": accion(1), "tokens": 30},
    ]
    out = student.run_guarded(lambda i: pasos[i] if i < len(pasos) else None, guard)
    expect_equal(out["stopped"], "done", what="motivo")
    expect_equal(len(out["executed"]), 2, what="acciones")
    expect_equal(guard.snapshot()["tokens"], 60, what="tokens acumulados")
    caro = student.AgentGuard(max_tokens=50)
    out = student.run_guarded(lambda i: {"action": accion(i), "tokens": 30}, caro)
    expect_equal(
        (out["stopped"], len(out["executed"])),
        ("max_tokens", 1),
        what="el 2.º paso supera los tokens",
    )
