def run_supervisor(task, supervisor, agents, max_turns=8, max_repeats=3):
    """Supervisor multi-agente con handoffs y estado compartido.

    supervisor(state) -> nombre del siguiente agente o "FINISH".
    agents: dict nombre -> función(state) -> dict opcional con:
        "message": texto para el historial,
        "data": dict que se fusiona en state["data"],
        "handoff": nombre de un agente al que pasar el control directamente en el turno siguiente.
    El estado compartido es {"task", "history": [{"agent", "message"}], "data": {}}.

    Se detiene con: "finish" (el supervisor decide terminar), "invalid_agent" (nombre desconocido),
    "stuck" (el mismo agente elegido `max_repeats` veces seguidas por el supervisor) o
    "max_turns". Un agente que lanza una excepción deja en el historial "error: <Tipo>: <mensaje>"
    y el bucle continúa.
    Devuelve {"state", "turns", "stopped", "trace"} (trace: nombres de agentes ejecutados).
    """
    state = {"task": task, "history": [], "data": {}}
    trace = []
    forced = None
    repeats, last_chosen = 0, None
    turns = 0
    stopped = "max_turns"
    for _ in range(max_turns):
        if forced is not None:
            name, forced = forced, None
        else:
            name = supervisor(state)
            if name == "FINISH":
                stopped = "finish"
                break
            repeats = repeats + 1 if name == last_chosen else 1
            last_chosen = name
            if repeats >= max_repeats:
                stopped = "stuck"
                break
        if name not in agents:
            stopped = "invalid_agent"
            break
        turns += 1
        trace.append(name)
        try:
            out = agents[name](state) or {}
        except Exception as e:  # noqa: BLE001 - el fallo queda en el historial compartido
            state["history"].append({"agent": name, "message": f"error: {type(e).__name__}: {e}"})
            continue
        state["history"].append({"agent": name, "message": out.get("message", "")})
        state["data"].update(out.get("data", {}))
        forced = out.get("handoff")
    return {"state": state, "turns": turns, "stopped": stopped, "trace": trace}


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    def supervisor(state):
        if "plazo" not in state["data"]:
            return "investigador"
        return "FINISH"

    agentes = {"investigador": lambda s: {"message": "encontrado", "data": {"plazo": "14 días"}}}
    print(run_supervisor("¿Plazo de devolución?", supervisor, agentes)["trace"])
