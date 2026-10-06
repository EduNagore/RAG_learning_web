import copy

END = "__end__"


class NeedsInput(Exception):
    """Un nodo la lanza para pausar el grafo y pedir un dato a una persona."""

    def __init__(self, question):
        super().__init__(question)
        self.question = question


class StateGraph:
    """Mini grafo de estados con checkpoints por hilo, pausas (human-in-the-loop) y reanudación.

    Un nodo es una función(state) -> dict con las claves a actualizar (o None). El estado es un
    diccionario que se va fusionando (`state.update(...)`). Un hilo (thread_id) tiene su propia
    lista de checkpoints.
    """

    def __init__(self):
        self.nodes = {}
        self.edges = {}  # origen -> nombre fijo o función router(state) -> nombre
        self.entry = None  # el primer nodo añadido
        self.checkpoints = {}  # thread_id -> lista de checkpoints

    def add_node(self, name, func):
        """Registra un nodo; el primero que se añade es el de entrada."""
        # TODO
        raise NotImplementedError("Completa add_node")

    def add_edge(self, source, target):
        """Arista fija source -> target."""
        # TODO
        raise NotImplementedError("Completa add_edge")

    def add_conditional_edge(self, source, router):
        """Arista condicional: router(state) devuelve el nombre del siguiente nodo (o END)."""
        # TODO
        raise NotImplementedError("Completa add_conditional_edge")

    def get_state(self, thread_id):
        """COPIA del estado del último checkpoint del hilo, o None si el hilo no existe."""
        # TODO
        raise NotImplementedError("Completa get_state")

    def history(self, thread_id):
        """Lista de (paso, siguiente nodo) de cada checkpoint del hilo, en orden."""
        # TODO
        raise NotImplementedError("Completa history")

    def run(self, thread_id, input_state=None, resume=None, max_steps=20):
        """Ejecuta o reanuda un hilo y devuelve un diccionario con "status":

        - Hilo nuevo: necesita input_state (si no, ValueError). Se guarda un checkpoint inicial
          {"step": 0, "node": entrada, "state": copia, "status": "running"} y se empieza por la entrada.
        - Hilo existente: continúa desde el último checkpoint (su "node" es el SIGUIENTE a ejecutar).
            * status "done": devuelve {"status": "done", "state", "steps"} sin ejecutar nada.
            * status "interrupted": exige `resume` (si es None, ValueError); se re-ejecuta ese mismo
              nodo con state["resume"] = resume.
        - Tras ejecutar un nodo con éxito: se quita state["resume"], se hace state.update(salida),
          step += 1, se calcula el siguiente nodo (arista fija o router; sin arista: END) y se guarda
          un checkpoint {"step", "node": siguiente, "state": copia, "status": "done" si es END, si no
          "running"}.
        - Si un nodo lanza NeedsInput: se guarda un checkpoint con status "interrupted" (mismo nodo, mismo
          paso, estado sin la clave resume) y se devuelve {"status": "interrupted", "question", "state"}.
        - Cualquier otra excepción se propaga SIN perder los checkpoints ya guardados (así, otra
          llamada a run reanuda desde el último nodo completado).
        - Se ejecutan como mucho `max_steps` nodos por llamada; si queda trabajo, devuelve
          {"status": "max_steps", "state", "steps"} y el checkpoint sigue en "running".
        - Al terminar: {"status": "done", "state", "steps"}.
        Los checkpoints guardan COPIAS PROFUNDAS (copy.deepcopy) del estado.
        """
        # TODO
        raise NotImplementedError("Completa run")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":

    def aprobar(state):
        if "resume" not in state:
            raise NeedsInput("¿Apruebas el borrador?")
        return {"aprobado": state["resume"]}

    try:
        grafo = StateGraph()
        grafo.add_node("redactar", lambda s: {"borrador": f"Informe sobre {s['tema']}"})
        grafo.add_node("aprobar", aprobar)
        grafo.add_edge("redactar", "aprobar")
        print(grafo.run("h1", {"tema": "devoluciones"})["status"])  # interrupted
        print(grafo.run("h1", resume=True)["state"])
    except NotImplementedError as e:
        print("Aún por completar:", e)
