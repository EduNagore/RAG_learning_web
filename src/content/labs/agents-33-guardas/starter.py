import json
import time


class AgentGuard:
    """Guardas de un agente: pasos, tokens, coste, tiempo y bucles.

    Parámetros (None = sin límite): max_steps (por defecto 10), max_tokens, max_cost,
    max_repeats (por defecto 3), timeout_s, clock (función sin argumentos que devuelve segundos;
    se inyecta para poder probar el tiempo).
    Atributos: started (clock() al crear), steps, tokens, cost, seen (dict), stopped (None o motivo).
    """

    def __init__(
        self, max_steps=10, max_tokens=None, max_cost=None, max_repeats=3, timeout_s=None, clock=time.monotonic
    ):
        # TODO: guarda los parámetros e inicializa el estado
        raise NotImplementedError("Completa __init__")

    def check(self, action=None, tokens=0, cost=0.0):
        """Se llama tras cada respuesta del modelo con lo que ha gastado y la acción que pide.

        Cuenta un paso y acumula tokens y coste. Devuelve None si puede continuar o el motivo de
        parada, el PRIMERO que se cumpla en este orden:
          "timeout"    si timeout_s no es None y han pasado MÁS de timeout_s segundos desde `started`,
          "max_steps"  si los pasos son MÁS que max_steps,
          "max_tokens" si los tokens acumulados son MÁS que max_tokens (si no es None),
          "max_cost"   si el coste acumulado es MÁS que max_cost (si no es None),
          "loop"       si la misma acción (dict comparado con json.dumps(..., sort_keys=True)) se ha
                       visto max_repeats veces o más, contando la actual (solo si action no es None).
        Una vez devuelto un motivo, queda fijado: las llamadas siguientes devuelven el mismo motivo
        sin contar nada más.
        """
        # TODO
        raise NotImplementedError("Completa check")

    def snapshot(self):
        """Devuelve {"steps", "tokens", "cost", "stopped"}."""
        # TODO
        raise NotImplementedError("Completa snapshot")


def run_guarded(next_step, guard):
    """Ejecuta pasos hasta que next_step devuelva None o la guarda pare el agente.

    next_step(i) recibe el número de acciones ejecutadas hasta ahora y devuelve None (el agente
    ha terminado) o un dict {"action": dict, "tokens": int (opcional), "cost": float (opcional)}.
    Cada paso se pasa por guard.check ANTES de ejecutarse; si la guarda para, esa acción NO se ejecuta.
    Devuelve {"stopped": "done" o el motivo de la guarda, "executed": lista de acciones ejecutadas}.
    """
    # TODO
    raise NotImplementedError("Completa run_guarded")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    try:
        guard = AgentGuard(max_steps=5, max_repeats=3)
        repetido = lambda i: {"action": {"tool": "buscar", "args": {"q": "x"}}}
        print(run_guarded(repetido, guard))
    except NotImplementedError as e:
        print("Aún por completar:", e)
