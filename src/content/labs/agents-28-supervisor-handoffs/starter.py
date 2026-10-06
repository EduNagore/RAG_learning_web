def run_supervisor(task, supervisor, agents, max_turns=8, max_repeats=3):
    """Supervisor multi-agente con handoffs y estado compartido.

    supervisor(state) -> nombre del siguiente agente o "FINISH".
    agents: dict nombre -> función(state) -> dict opcional con:
        "message": texto para el historial,
        "data": dict que se fusiona (update) en state["data"],
        "handoff": nombre de un agente al que pasar el control DIRECTAMENTE en el turno siguiente
                   (sin consultar al supervisor).
    El estado compartido es {"task": task, "history": [{"agent", "message"}], "data": {}}.

    Cada turno ejecuta un agente. Se detiene con:
      - "finish":        el supervisor devuelve "FINISH".
      - "invalid_agent": el nombre elegido (por el supervisor o por un handoff) no está en `agents`.
      - "stuck":         el supervisor elige el MISMO agente `max_repeats` veces seguidas
                         (los turnos por handoff no cuentan; antes de ejecutarlo).
      - "max_turns":     se agotan `max_turns` turnos.
    Si un agente lanza una excepción, se añade al historial
    {"agent": nombre, "message": "error: <Tipo>: <mensaje>"} y el bucle continúa.
    Los agentes pueden devolver None (se trata como {}).

    Devuelve {"state": state, "turns": agentes ejecutados, "stopped": motivo,
              "trace": [nombres de agentes ejecutados, en orden]}.
    """
    # TODO
    raise NotImplementedError("Completa run_supervisor")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":

    def supervisor(state):
        if "plazo" not in state["data"]:
            return "investigador"
        return "FINISH"

    agentes = {"investigador": lambda s: {"message": "encontrado", "data": {"plazo": "14 días"}}}
    try:
        print(run_supervisor("¿Plazo de devolución?", supervisor, agentes)["trace"])
    except NotImplementedError as e:
        print("Aún por completar:", e)
