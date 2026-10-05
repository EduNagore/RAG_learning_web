"""Pruebas de mutación de los laboratorios: cada mutante es un error típico de alumno
y los tests DEBEN detectarlo (al menos un test falla).

Uso: uv run python scripts/mutate_labs.py
Al añadir un laboratorio, añade aquí sus mutantes. Un mutante que sobrevive indica un hueco en
los tests (o es un mutante equivalente: documéntalo y retíralo). Sale con código 1 si alguno sobrevive.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "public" / "py"))
from ragkit.labrunner import run_lab

LABS = ROOT / "src" / "content" / "labs"

# (lab, descripción, texto original, texto mutado)
MUTANTS = [
    (
        "rag-01-coseno-topk",
        "sin dividir por las normas (solo producto escalar)",
        "return float(a @ b / (norm_a * norm_b))",
        "return float(a @ b)",
    ),
    (
        "rag-01-coseno-topk",
        "orden ascendente en vez de descendente",
        'np.argsort(-scores, kind="stable")',
        'np.argsort(scores, kind="stable")',
    ),
    (
        "rag-01-coseno-topk",
        "desempate inestable / invertido",
        'np.argsort(-scores, kind="stable")',
        "np.argsort(-scores)[::-1][::-1][::-1][::-1][::-1]",
    ),
    (
        "rag-01-coseno-topk",
        "no controla filas de ceros (NaN)",
        "scores = np.divide(dots, norms, out=np.zeros_like(dots), where=norms > 0)",
        "scores = dots / norms",
    ),
    (
        "rag-01-coseno-topk",
        "modifica la matriz de entrada",
        "m = np.asarray(matrix, dtype=float)",
        "m = np.asarray(matrix, dtype=float)\n    matrix[:] = matrix / 2",
    ),
    ("rag-01-coseno-topk", "no recorta a k", "[: max(k, 0)]", "[:]"),
    (
        "rag-01-coseno-topk",
        "vector cero lanza excepción",
        "if norm_a == 0 or norm_b == 0:\n        return 0.0",
        "if False:\n        return 0.0",
    ),
    (
        "rag-05-bm25",
        "idf sin el 1+ (puede ser negativo)",
        "idf = math.log(1 + (n_docs - n + 0.5) / (n + 0.5))",
        "idf = math.log((n_docs - n + 0.5) / (n + 0.5))",
    ),
    (
        "rag-05-bm25",
        "sin normalización por longitud (b ignorado)",
        "norm = f + k1 * (1 - b + b * len(doc) / avgdl)",
        "norm = f + k1",
    ),
    (
        "rag-05-bm25",
        "cuenta los términos repetidos de la consulta",
        "for term in set(query_tokens):",
        "for term in query_tokens:",
    ),
    (
        "rag-05-bm25",
        "n cuenta apariciones totales en vez de documentos",
        "n = sum(1 for doc in docs_tokens if term in doc)",
        "n = sum(doc.count(term) for doc in docs_tokens)",
    ),
    (
        "rag-05-bm25",
        "la búsqueda ignora el título",
        'tokenize(d["title"] + " " + d["text"])',
        'tokenize(d["text"])',
    ),
    ("rag-05-bm25", "incluye resultados con puntuación 0", "if score > 0][:top_k]", "][:top_k]"),
    (
        "rag-05-bm25",
        "empate resuelto al revés",
        "key=lambda item: (-item[1], item[2])",
        "key=lambda item: (-item[1], -item[2])",
    ),
    (
        "rag-05-bm25",
        "k1 ignorado en el numerador",
        "idf * f * (k1 + 1) / norm",
        "idf * f * 2.5 / norm",
    ),
    (
        "agents-23-react",
        "sin límite de pasos útil (siempre 'final')",
        'return AgentResult(None, max_steps, "max_steps", trace)',
        "return AgentResult('', max_steps, \"final\", trace)",
    ),
    (
        "agents-23-react",
        "no añade el mensaje del asistente",
        'messages.append(Message("assistant", response.text, tool_calls=response.tool_calls))',
        "pass",
    ),
    (
        "agents-23-react",
        "la excepción de la herramienta se propaga",
        "except Exception as e:  # noqa: BLE001 - el error se devuelve al modelo",
        "except ZeroDivisionError as e:",
    ),
    # (retirado) "herramienta inexistente da KeyError" es un mutante EQUIVALENTE: el KeyError
    # lo captura la rama de excepciones y el resultado sigue empezando por "error:".
    (
        "agents-23-react",
        "resultados en orden inverso",
        "for call in response.tool_calls:",
        "for call in reversed(response.tool_calls):",
    ),
    (
        "agents-23-react",
        "el resultado no se convierte a texto",
        "result = str(tools[call.name](**call.arguments))",
        "result = tools[call.name](**call.arguments)",
    ),
    (
        "agents-23-react",
        "no registra la traza",
        'trace.append({"tool": call.name, "arguments": call.arguments, "result": result})',
        "pass",
    ),
    (
        "agents-23-react",
        "cuenta mal los pasos",
        'return AgentResult(response.text, step + 1, "final", trace)',
        'return AgentResult(response.text, step, "final", trace)',
    ),
    (
        "agents-23-react",
        "sin tool_call_id",
        'Message("tool", result, tool_call_id=call.id)',
        'Message("tool", result)',
    ),
    # --- rag-02-chunk-fijo ---
    (
        "rag-02-chunk-fijo",
        "sin condición de parada (fragmento final redundante)",
        "        if start + size >= len(words):\n            break\n",
        "",
    ),
    ("rag-02-chunk-fijo", "ignora el solape (paso = size)", "step = size - overlap", "step = size"),
    (
        "rag-02-chunk-fijo",
        "no valida los parámetros",
        "if size <= 0 or overlap < 0 or overlap >= size:",
        "if False:",
    ),
    ("rag-02-chunk-fijo", "split(' ') genera palabras vacías", "text.split()", 'text.split(" ")'),
    (
        "rag-02-chunk-fijo",
        "pierde la cola si no encaja exacto",
        "range(0, len(words), step)",
        "range(0, len(words) - size + 1, step)",
    ),
    (
        "rag-02-chunk-fijo",
        "solape de más (usa overlap + 1)",
        "step = size - overlap",
        "step = size - overlap - 1",
    ),
    # --- rag-03-chunk-recursivo ---
    (
        "rag-03-chunk-recursivo",
        "no fusiona piezas (una por fragmento)",
        "if len(candidate) <= max_chars:",
        "if False:",
    ),
    (
        "rag-03-chunk-recursivo",
        "no trocea las piezas demasiado grandes",
        "chunks.extend(chunk_recursive(piece, max_chars, remaining))",
        "chunks.append(piece)",
    ),
    (
        "rag-03-chunk-recursivo",
        "sin corte duro",
        "return [text[i : i + max_chars] for i in range(0, len(text), max_chars)]",
        "return [text]",
    ),
    (
        "rag-03-chunk-recursivo",
        "pierde el último fragmento acumulado",
        "        if current:\n            chunks.append(current)\n        return chunks",
        "        return chunks",
    ),
    (
        "rag-03-chunk-recursivo",
        "no descarta piezas vacías",
        "pieces = [p.strip() for p in text.split(sep) if p.strip()]",
        "pieces = text.split(sep)",
    ),
    (
        "rag-03-chunk-recursivo",
        "ignora los separadores indicados",
        "for i, sep in enumerate(separators):",
        'for i, sep in enumerate(("\\n\\n", "\\n", " ")):',
    ),
    (
        "rag-03-chunk-recursivo",
        "usa siempre todos los separadores al recursar",
        "chunk_recursive(piece, max_chars, remaining)",
        "chunk_recursive(piece, max_chars, ())",
    ),
    # --- rag-04-chunk-markdown ---
    (
        "rag-04-chunk-markdown",
        "no descarta títulos más profundos",
        "headers = headers[: level - 1] + [match.group(2)]",
        "headers = headers + [match.group(2)]",
    ),
    (
        "rag-04-chunk-markdown",
        "trata '#' de código como encabezado",
        "match = None if in_code else HEADER.match(line)",
        "match = HEADER.match(line)",
    ),
    (
        "rag-04-chunk-markdown",
        "incluye la línea del encabezado en el texto",
        "            flush()\n            level = len(match.group(1))",
        "            buffer.append(line)\n            flush()\n            level = len(match.group(1))",
    ),
    (
        "rag-04-chunk-markdown",
        "no divide secciones largas",
        "    if len(body) <= max_chars:\n        return [body]",
        "    return [body]",
    ),
    (
        "rag-04-chunk-markdown",
        "path con otro separador",
        '"path": " > ".join(headers)',
        '"path": "/".join(headers)',
    ),
    (
        "rag-04-chunk-markdown",
        "genera fragmentos vacíos",
        "        if not body:\n            return\n",
        "",
    ),
    (
        "rag-04-chunk-markdown",
        "los párrafos largos no se cortan",
        "chunks.extend(paragraph[i : i + max_chars] for i in range(0, len(paragraph), max_chars))",
        "chunks.append(paragraph)",
    ),
]

survivors = []
for lab, desc, old, new in MUTANTS:
    source = (LABS / lab / "solution.py").read_text(encoding="utf-8")
    if old not in source:
        print(f"!! NO SE PUDO APLICAR  [{lab}] {desc}")
        survivors.append((lab, desc, "no aplicable"))
        continue
    report = run_lab(
        source.replace(old, new, 1), (LABS / lab / "test_lab.py").read_text(encoding="utf-8")
    )
    failed = [r["name"] for r in report["results"] if not r["passed"]]
    killed = bool(report["load_error"]) or bool(failed)
    status = "detectado " if killed else "SOBREVIVE "
    print(f"{status} [{lab}] {desc}" + (f"  -> {len(failed)} test(s)" if killed and failed else ""))
    if not killed:
        survivors.append((lab, desc, "sobrevive"))

print(f"\n{len(MUTANTS) - len(survivors)}/{len(MUTANTS)} mutantes detectados")
sys.exit(1 if survivors else 0)
