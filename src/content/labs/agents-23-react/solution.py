from ragkit.agents import AgentResult
from ragkit.llm import Message, MockLLM


def run_agent(llm, tools, question, max_steps=5):
    """Ejecuta el bucle de un agente y devuelve un AgentResult.

    llm:       objeto con generate(messages, tools=None) -> LLMResponse (text, tool_calls)
    tools:     dict {nombre: función}; se llama con tools[nombre](**arguments)
    question:  pregunta del usuario
    max_steps: máximo de llamadas al modelo

    Reglas:
    - Cada vuelta del bucle es una llamada al modelo.
    - Sin tool_calls, response.text es la respuesta: stopped="final".
    - Con tool_calls: añade el mensaje del asistente y, en orden, un Message("tool", ...)
      por cada herramienta (el resultado siempre es str).
    - Herramienta inexistente o que lanza excepción: el resultado es un texto que empieza
      por "error:" y el bucle continúa.
    - Si se agotan los pasos: AgentResult(None, max_steps, "max_steps", trace).
    - trace: una entrada {"tool", "arguments", "result"} por herramienta ejecutada.
    """
    messages = [Message("user", question)]
    trace = []

    for step in range(max_steps):
        response = llm.generate(messages, tools=list(tools))

        # Sin herramientas pedidas: el modelo ha terminado.
        if not response.tool_calls:
            return AgentResult(response.text, step + 1, "final", trace)

        # El modelo necesita ver su propia petición antes de los resultados.
        messages.append(Message("assistant", response.text, tool_calls=response.tool_calls))

        for call in response.tool_calls:
            if call.name not in tools:
                result = f"error: la herramienta '{call.name}' no existe"
            else:
                try:
                    result = str(tools[call.name](**call.arguments))
                except Exception as e:  # noqa: BLE001 - el error se devuelve al modelo
                    result = f"error: {type(e).__name__}: {e}"
            messages.append(Message("tool", result, tool_call_id=call.id))
            trace.append({"tool": call.name, "arguments": call.arguments, "result": result})

    return AgentResult(None, max_steps, "max_steps", trace)


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    llm = MockLLM(
        script=[
            {"tool": "buscar", "args": {"consulta": "plazo de devolución"}},
            "Tienes 14 días naturales desde la entrega.",
        ]
    )
    tools = {"buscar": lambda consulta: "Los particulares tienen 14 días naturales."}
    resultado = run_agent(llm, tools, "¿Cuántos días tengo para devolver?")
    print(resultado.answer)
    print("pasos:", resultado.steps)
