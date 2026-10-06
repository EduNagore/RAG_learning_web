import copy

END = "__end__"


class NeedsInput(Exception):
    """Un nodo la lanza para pausar el grafo y pedir un dato a una persona."""

    def __init__(self, question):
        super().__init__(question)
        self.question = question


class StateGraph:
    """Mini grafo de estados con checkpoints por hilo, pausas (human-in-the-loop) y reanudación."""

    def __init__(self):
        self.nodes = {}
        self.edges = {}  # origen -> nombre fijo o función router(state) -> nombre
        self.entry = None
        self.checkpoints = {}  # thread_id -> lista de checkpoints

    def add_node(self, name, func):
        self.nodes[name] = func
        if self.entry is None:
            self.entry = name

    def add_edge(self, source, target):
        self.edges[source] = target

    def add_conditional_edge(self, source, router):
        self.edges[source] = router

    def _next(self, node, state):
        edge = self.edges.get(node, END)
        return edge(state) if callable(edge) else edge

    def _save(self, thread_id, step, node, state, status):
        self.checkpoints.setdefault(thread_id, []).append(
            {"step": step, "node": node, "state": copy.deepcopy(state), "status": status}
        )

    def get_state(self, thread_id):
        """Copia del estado del último checkpoint del hilo, o None si no existe."""
        history = self.checkpoints.get(thread_id)
        return copy.deepcopy(history[-1]["state"]) if history else None

    def history(self, thread_id):
        """Lista de (paso, siguiente nodo) de los checkpoints del hilo."""
        return [(c["step"], c["node"]) for c in self.checkpoints.get(thread_id, [])]

    def run(self, thread_id, input_state=None, resume=None, max_steps=20):
        """Ejecuta o reanuda el hilo. Devuelve {"status", "state", ...}.

        status: "done", "interrupted" (con "question") o "max_steps".
        """
        history = self.checkpoints.get(thread_id)
        if not history:
            if input_state is None:
                raise ValueError("un hilo nuevo necesita input_state")
            state = copy.deepcopy(input_state)
            node = self.entry
            self._save(thread_id, 0, node, state, "running")
            step = 0
        else:
            last = history[-1]
            state, node, step = copy.deepcopy(last["state"]), last["node"], last["step"]
            if last["status"] == "done":
                return {"status": "done", "state": state, "steps": step}
            if last["status"] == "interrupted":
                if resume is None:
                    raise ValueError("el hilo está interrumpido: hace falta resume")
                state["resume"] = resume

        executed = 0
        while node != END:
            if executed >= max_steps:
                return {"status": "max_steps", "state": state, "steps": step}
            try:
                update = self.nodes[node](state) or {}
            except NeedsInput as pause:
                state.pop("resume", None)
                self._save(thread_id, step, node, state, "interrupted")
                return {"status": "interrupted", "question": pause.question, "state": state}
            state.pop("resume", None)
            state.update(update)
            step += 1
            executed += 1
            node = self._next(node, state)
            self._save(thread_id, step, node, state, "done" if node == END else "running")
        return {"status": "done", "state": state, "steps": step}


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":

    def aprobar(state):
        if "resume" not in state:
            raise NeedsInput("¿Apruebas el borrador?")
        return {"aprobado": state["resume"]}

    grafo = StateGraph()
    grafo.add_node("redactar", lambda s: {"borrador": f"Informe sobre {s['tema']}"})
    grafo.add_node("aprobar", aprobar)
    grafo.add_edge("redactar", "aprobar")
    print(grafo.run("h1", {"tema": "devoluciones"})["status"])  # interrupted
    print(grafo.run("h1", resume=True)["state"])
