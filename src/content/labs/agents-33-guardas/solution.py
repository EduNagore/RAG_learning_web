import json
import time


class AgentGuard:
    """Guardas de un agente: pasos, tokens, coste, tiempo y bucles."""

    def __init__(
        self,
        max_steps=10,
        max_tokens=None,
        max_cost=None,
        max_repeats=3,
        timeout_s=None,
        clock=time.monotonic,
    ):
        self.max_steps = max_steps
        self.max_tokens = max_tokens
        self.max_cost = max_cost
        self.max_repeats = max_repeats
        self.timeout_s = timeout_s
        self.clock = clock
        self.started = clock()
        self.steps = 0
        self.tokens = 0
        self.cost = 0.0
        self.seen = {}
        self.stopped = None

    def check(self, action=None, tokens=0, cost=0.0):
        """Se llama tras cada respuesta del modelo. Devuelve None o el motivo de parada."""
        if self.stopped is not None:
            return self.stopped
        self.steps += 1
        self.tokens += tokens
        self.cost += cost
        self.stopped = self._reason(action)
        return self.stopped

    def _reason(self, action):
        if self.timeout_s is not None and self.clock() - self.started > self.timeout_s:
            return "timeout"
        if self.steps > self.max_steps:
            return "max_steps"
        if self.max_tokens is not None and self.tokens > self.max_tokens:
            return "max_tokens"
        if self.max_cost is not None and self.cost > self.max_cost:
            return "max_cost"
        if action is not None:
            key = json.dumps(action, sort_keys=True)
            self.seen[key] = self.seen.get(key, 0) + 1
            if self.seen[key] >= self.max_repeats:
                return "loop"
        return None

    def snapshot(self):
        return {
            "steps": self.steps,
            "tokens": self.tokens,
            "cost": self.cost,
            "stopped": self.stopped,
        }


def run_guarded(next_step, guard):
    """Ejecuta pasos hasta que next_step devuelva None o la guarda pare el agente."""
    executed = []
    while True:
        step = next_step(len(executed))
        if step is None:
            return {"stopped": "done", "executed": executed}
        reason = guard.check(step["action"], step.get("tokens", 0), step.get("cost", 0.0))
        if reason is not None:
            return {"stopped": reason, "executed": executed}
        executed.append(step["action"])
