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

    # TODO: implementa el bucle
    raise NotImplementedError("Completa run_agent")


# Prueba tu código: pulsa «Ejecutar» para ver esta salida.
if __name__ == "__main__":
    llm = MockLLM(
        script=[
            {"tool": "buscar", "args": {"consulta": "plazo de devolución"}},
            "Tienes 14 días naturales desde la entrega.",
        ]
    )
    tools = {"buscar": lambda consulta: "Los particulares tienen 14 días naturales."}
    try:
        resultado = run_agent(llm, tools, "¿Cuántos días tengo para devolver?")
        print(resultado.answer)
        print("pasos:", resultado.steps)
    except NotImplementedError as e:
        print("Aún por completar:", e)
