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
    # --- rag-06-indice-vectorial ---
    (
        "rag-06-indice-vectorial",
        "postfiltrado en lugar de prefiltrado",
        (
            "if not where or _cumple(meta, where)",
            (
                'orden = np.argsort(-scores, kind="stable")[:k]\n'
                "        return [(ids[i], float(scores[i])) for i in orden]"
            ),
        ),
        (
            "if True",
            (
                'orden = np.argsort(-scores, kind="stable")[:k]\n'
                "        return [(ids[i], float(scores[i])) for i in orden"
                " if not where or _cumple(self._entries[ids[i]][1], where)]"
            ),
        ),
    ),
    (
        "rag-06-indice-vectorial",
        "no normaliza al añadir",
        "self._entries[id] = (v / norm, dict(metadata or {}))",
        "self._entries[id] = (v, dict(metadata or {}))",
    ),
    (
        "rag-06-indice-vectorial",
        "las condiciones se combinan con OR",
        (
            "            if valor not in esperado:\n                return False\n"
            "        elif valor != esperado:\n            return False\n    return True"
        ),
        (
            "            if valor in esperado:\n                return True\n"
            "        elif valor == esperado:\n            return True\n    return False"
        ),
    ),
    (
        "rag-06-indice-vectorial",
        "where no admite listas",
        "if isinstance(esperado, (list, tuple, set, frozenset)):",
        "if False:",
    ),
    (
        "rag-06-indice-vectorial",
        "delete no elimina",
        "return self._entries.pop(id, None) is not None",
        "return id in self._entries",
    ),
    (
        "rag-06-indice-vectorial",
        "add no reemplaza un id existente",
        "self._entries[id] = (v / norm, dict(metadata or {}))",
        "self._entries.setdefault(id, (v / norm, dict(metadata or {})))",
    ),
    (
        "rag-06-indice-vectorial",
        "los empates favorecen al insertado después",
        'np.argsort(-scores, kind="stable")',
        "np.lexsort((-np.arange(len(scores)), -scores))",
    ),
    (
        "rag-06-indice-vectorial",
        "no valida la dimensión",
        "if v.shape != (self.dim,):",
        "if False:",
    ),
    ("rag-06-indice-vectorial", "modifica la consulta", "q = q / norm", "q /= norm"),
    (
        "rag-06-indice-vectorial",
        "acepta el vector cero",
        'if norm == 0:\n            raise ValueError("no se puede indexar el vector cero")',
        "if norm == 0:\n            norm = 1",
    ),
    # --- rag-07-mini-ivf ---
    ("rag-07-mini-ivf", "n_probe ignorado (siempre 1)", "[:n_probe]", "[:1]"),
    (
        "rag-07-mini-ivf",
        "visita los centroides más lejanos",
        'np.argsort(-(index["centroids"] @ q), kind="stable")[:n_probe]',
        'np.argsort((index["centroids"] @ q), kind="stable")[:n_probe]',
    ),
    (
        "rag-07-mini-ivf",
        "solo mira la primera lista",
        'np.concatenate([index["lists"][j] for j in nearest_lists])',
        'index["lists"][nearest_lists[0]]',
    ),
    (
        "rag-07-mini-ivf",
        "centroides sin normalizar",
        "                    centroids[j] = mean / norm",
        "                    centroids[j] = mean",
    ),
    (
        "rag-07-mini-ivf",
        "resultado sin ordenar por similitud",
        'order = np.argsort(-(X[candidates] @ q), kind="stable")[:k]',
        "order = np.arange(len(candidates))[:k]",
    ),
    (
        "rag-07-mini-ivf",
        "recall con denominador erróneo",
        "return len(exact & {int(i) for i in approx_ids}) / len(exact)",
        "return len(exact & {int(i) for i in approx_ids}) / max(len(approx_ids), 1)",
    ),
    (
        "rag-07-mini-ivf",
        "las listas pierden un vector",
        "lists = [np.flatnonzero(assignment == j) for j in range(n_lists)]",
        "lists = [np.flatnonzero(assignment[:-1] == j) for j in range(n_lists)]",
    ),
    (
        "rag-07-mini-ivf",
        "devuelve un número de candidatos falso",
        "return candidates[order], len(candidates)",
        "return candidates[order], len(X)",
    ),
    (
        "rag-07-mini-ivf",
        "ignora la semilla",
        "    rng = np.random.default_rng(seed)\n    centroids = _normalize_rows",
        "    rng = np.random.default_rng()\n    centroids = _normalize_rows",
    ),
    # --- rag-08-rrf ---
    (
        "rag-08-rrf",
        "posiciones desde 0",
        "enumerate(ranking, start=1)",
        "enumerate(ranking, start=0)",
    ),
    ("rag-08-rrf", "ignora los pesos", "peso / (k + posicion)", "1 / (k + posicion)"),
    (
        "rag-08-rrf",
        "cuenta los duplicados de un ranking",
        "            if doc_id in vistos:\n                continue\n",
        "",
    ),
    ("rag-08-rrf", "empate por última aparición", "orden[par[0]]", "-orden[par[0]]"),
    ("rag-08-rrf", "no valida k", "if k < 0:", "if k < -1000:"),
    (
        "rag-08-rrf",
        "no valida los pesos",
        ("if len(weights) != len(rankings):", "strict=True"),
        ("if False:", "strict=False"),
    ),
    ("rag-08-rrf", "no recorta a candidates", "[:candidates]", "[:1000]"),
    (
        "rag-08-rrf",
        "devuelve tuplas en vez de ids",
        "return [doc_id for doc_id, _ in rrf_fuse(rankings, k=k)[:top_k]]",
        "return rrf_fuse(rankings, k=k)[:top_k]",
    ),
    ("rag-08-rrf", "hybrid ignora k", "rrf_fuse(rankings, k=k)", "rrf_fuse(rankings)"),
    # --- rag-09-reranking ---
    ("rag-09-reranking", "descuento sin desplazar", "math.log2(i + 2)", "math.log2(i + 3)"),
    (
        "rag-09-reranking",
        "IDCG con ganancias ascendentes",
        "sorted(relevance.values(), reverse=True), k)",
        "sorted(relevance.values()), k)",
    ),
    (
        "rag-09-reranking",
        "IDCG sin recortar a k",
        "sorted(relevance.values(), reverse=True), k)",
        "sorted(relevance.values(), reverse=True), 10**9)",
    ),
    ("rag-09-reranking", "no valorados valen 1", "relevance.get(d, 0)", "relevance.get(d, 1)"),
    ("rag-09-reranking", "sin guarda de IDCG cero", "if ideal == 0:", "if False:"),
    ("rag-09-reranking", "orden ascendente", "-score_fn(query", "score_fn(query"),
    (
        "rag-09-reranking",
        "ignora top_k",
        "return ids if top_k is None else ids[:top_k]",
        "return ids",
    ),
    ("rag-09-reranking", "ignora n_candidates", "[:n_candidates]", "[:1000]"),
    ("rag-09-reranking", "no filtra ids desconocidos", " if i in docs_by_id", ""),
    # --- rag-11-multi-query ---
    ("rag-11-multi-query", "no quita viñetas", "|[-*•])", ")"),
    (
        "rag-11-multi-query",
        "no quita duplicados",
        "if not limpia or limpia.lower() in vistas:",
        "if not limpia:",
    ),
    (
        "rag-11-multi-query",
        "duplicados sensibles a mayúsculas",
        ("limpia.lower() in vistas", "vistas.add(limpia.lower())"),
        ("limpia in vistas", "vistas.add(limpia)"),
    ),
    ("rag-11-multi-query", "no respeta n", "return variantes[:n]", "return variantes"),
    ("rag-11-multi-query", "pierde la original", "consultas = [question]", "consultas = []"),
    (
        "rag-11-multi-query",
        "duplica la original",
        "if variante.lower() != question.lower():",
        "if True:",
    ),
    (
        "rag-11-multi-query",
        "no recorta a top_k",
        "rrf_ids(rankings, k=k)[:top_k]",
        "rrf_ids(rankings, k=k)",
    ),
    (
        "rag-11-multi-query",
        "solo busca con la original",
        "for consulta in expand_queries(llm, question, n)",
        "for consulta in [question]",
    ),
    (
        "rag-11-multi-query",
        "el prompt no dice cuántas",
        "Escribe {n} reformulaciones",
        "Escribe reformulaciones",
    ),
    # --- rag-12-hyde ---
    ("rag-12-hyde", "sin plan B", "if respuesta is None or not respuesta.strip():", "if False:"),
    (
        "rag-12-hyde",
        "mezcla invertida",
        "(1 - mix) * embed(respuesta) + mix * embed(question)",
        "mix * embed(respuesta) + (1 - mix) * embed(question)",
    ),
    (
        "rag-12-hyde",
        "no normaliza",
        "return vector / norma if norma > 0 else vector",
        "return vector",
    ),
    ("rag-12-hyde", "orden ascendente", "np.argsort(-puntuaciones", "np.argsort(puntuaciones"),
    ("rag-12-hyde", "ignora top_k", "[:top_k]", "[:3]"),
    (
        "rag-12-hyde",
        "el prompt no incluye la pregunta",
        'f"que responda a esta pregunta: {question}"',
        '"que responda a esta pregunta"',
    ),
    (
        "rag-12-hyde",
        "hyde_search ignora mix",
        "hyde_vector(question, llm, embed, mix=mix)",
        "hyde_vector(question, llm, embed)",
    ),
    # --- rag-15-parent-document ---
    (
        "rag-15-parent-document",
        "posición desde 1",
        'enumerate(split_sentences(doc["text"]))',
        'enumerate(split_sentences(doc["text"]), start=1)',
    ),
    (
        "rag-15-parent-document",
        "repite padres",
        "if parent_id is None or parent_id in seen:",
        "if parent_id is None:",
    ),
    (
        "rag-15-parent-document",
        "no ignora ids desconocidos",
        "if parent_id is None or",
        "if False or",
    ),
    (
        "rag-15-parent-document",
        "ignora max_parents",
        "return parents if max_parents is None else parents[:max_parents]",
        "return parents",
    ),
    ("rag-15-parent-document", "acepta puntuaciones nulas", "if s[0] > 0", "if s[0] >= 0"),
    ("rag-15-parent-document", "ignora top_k_children", "ranked[:top_k_children]", "ranked[:100]"),
    ("rag-15-parent-document", "orden ascendente", "key=lambda x: -x[0])", "key=lambda x: x[0])"),
    (
        "rag-15-parent-document",
        "entrega el hijo en vez del padre",
        'docs_by_id[parent_id]["text"]',
        'children[0]["text"]',
    ),
    # --- rag-16-ventana-de-frases ---
    ("rag-16-ventana-de-frases", "ventana sin recorte inicial", "max(0, p - w)", "p - w"),
    (
        "rag-16-ventana-de-frases",
        "ventana sin recorte final",
        "min(n_sentences, p + w + 1)",
        "p + w + 1",
    ),
    (
        "rag-16-ventana-de-frases",
        "no fusiona contiguas",
        "if merged and start <= merged[-1][1]:",
        "if merged and start < merged[-1][1]:",
    ),
    (
        "rag-16-ventana-de-frases",
        "no fusiona nada",
        "if merged and start <= merged[-1][1]:",
        "if False:",
    ),
    (
        "rag-16-ventana-de-frases",
        "no ordena",
        "ranges = sorted(\n        (max(0, p - w), min(n_sentences, p + w + 1)) for p in positions if 0 <= p < n_sentences\n    )",
        "ranges = list(\n        (max(0, p - w), min(n_sentences, p + w + 1)) for p in positions if 0 <= p < n_sentences\n    )",
    ),
    (
        "rag-16-ventana-de-frases",
        "acepta posiciones fuera de rango",
        " if 0 <= p < n_sentences",
        "",
    ),
    (
        "rag-16-ventana-de-frases",
        "no ignora documentos desconocidos",
        "        if doc_id in sentences_by_doc:\n            positions_by_doc",
        "        if True:\n            positions_by_doc",
    ),
    (
        "rag-16-ventana-de-frases",
        "texto con salto en vez de espacio",
        '" ".join(sentences[start:end])',
        '"\\n".join(sentences[start:end])',
    ),
    # --- rag-13-prompt-con-citas ---
    (
        "rag-13-prompt-con-citas",
        "no escapa el cierre de etiqueta",
        'doc["text"].replace("</documento>", "&lt;/documento&gt;")',
        'doc["text"]',
    ),
    (
        "rag-13-prompt-con-citas",
        "la pregunta va antes de los documentos",
        'partes = [instructions, *bloques, f"Pregunta: {question}"]',
        'partes = [instructions, f"Pregunta: {question}", *bloques]',
    ),
    (
        "rag-13-prompt-con-citas",
        "citas repetidas",
        "            if doc_id not in vistas:\n                vistas.append(doc_id)",
        "            vistas.append(doc_id)",
    ),
    (
        "rag-13-prompt-con-citas",
        "no admite grupos",
        "(?:\\s*,\\s*doc-\\d+)*",
        "(?:\\s*,\\s*doc-\\d+){0}",
    ),
    ("rag-13-prompt-con-citas", "no detecta inventadas", "if c not in allowed_ids", "if False"),
    (
        "rag-13-prompt-con-citas",
        "ok ignora las frases sin cita",
        "bool(citations) and not invented and not uncited",
        "bool(citations) and not invented",
    ),
    (
        "rag-13-prompt-con-citas",
        "ok sin exigir una cita",
        "bool(citations) and not invented and not uncited",
        "not invented and not uncited",
    ),
    (
        "rag-13-prompt-con-citas",
        "la abstención no se reconoce",
        'answer.strip() == "NO_LO_SE"',
        'answer == "NO_LO_SE"',
    ),
    # --- rag-14-orden-del-contexto ---
    ("rag-14-orden-del-contexto", "impares sin invertir", "ranking[1::2][::-1]", "ranking[1::2]"),
    (
        "rag-14-orden-del-contexto",
        "solo pares",
        "ranking[0::2] + ranking[1::2][::-1]",
        "ranking[0::2]",
    ),
    (
        "rag-14-orden-del-contexto",
        "la evidencia no se acota",
        "max(0, min(position, len(result)))",
        "position",
    ),
    (
        "rag-14-orden-del-contexto",
        "modifica la entrada",
        "result = list(distractors)",
        "result = distractors",
    ),
    (
        "rag-14-orden-del-contexto",
        "se pasa del presupuesto",
        "if used + cost <= budget_tokens:",
        "if used <= budget_tokens:",
    ),
    (
        "rag-14-orden-del-contexto",
        "se detiene al primero que no cabe",
        '            kept.append(doc["id"])\n            used += cost',
        '            kept.append(doc["id"])\n            used += cost\n        else:\n            break',
    ),
    ("rag-14-orden-del-contexto", "zona inicio desplazada", "if i < n / 3:", "if i <= n / 3:"),
    (
        "rag-14-orden-del-contexto",
        "zona final desplazada",
        "if i >= 2 * n / 3:",
        "if i > 2 * n / 3:",
    ),
    # --- rag-20-mini-graphrag ---
    (
        "rag-20-mini-graphrag",
        "no quita acentos",
        "strip_accents(name).casefold().split()",
        "name.casefold().split()",
    ),
    (
        "rag-20-mini-graphrag",
        "no colapsa espacios",
        '" ".join(strip_accents(name).casefold().split())',
        "strip_accents(name).casefold().strip()",
    ),
    (
        "rag-20-mini-graphrag",
        "el grafo no normaliza",
        "graph.add_edge(normalize_entity(subject), normalize_entity(obj), key=relation)",
        "graph.add_edge(subject, obj, key=relation)",
    ),
    (
        "rag-20-mini-graphrag",
        "vecinos solo en el sentido de las aristas",
        "graph.to_undirected(as_view=True), start, cutoff=hops",
        "graph, start, cutoff=hops",
    ),
    ("rag-20-mini-graphrag", "incluye la propia entidad", "if node != start", "if True"),
    (
        "rag-20-mini-graphrag",
        "vecinos sin ordenar",
        "return sorted(node for node in reachable if node != start)",
        "return list(node for node in reachable if node != start)",
    ),
    ("rag-20-mini-graphrag", "un salto de más", "cutoff=hops", "cutoff=hops + 1"),
    (
        "rag-20-mini-graphrag",
        "elige el último destino",
        "current = targets[0]",
        "current = targets[-1]",
    ),
    ("rag-20-mini-graphrag", "ignora la relación", "if key == relation", "if True"),
    (
        "rag-20-mini-graphrag",
        "comunidades de menor a mayor",
        "key=lambda c: (-len(c), c[0])",
        "key=lambda c: (len(c), c[0])",
    ),
    # --- rag-21-crag-simplificado ---
    (
        "rag-21-crag-simplificado",
        "raíz de 4 letras",
        (
            "{t[:5] for t in tokenize(question)}",
            '{t[:5] for doc in docs for t in tokenize(doc["text"])}',
        ),
        (
            "{t[:4] for t in tokenize(question)}",
            '{t[:4] for doc in docs for t in tokenize(doc["text"])}',
        ),
    ),
    ("rag-21-crag-simplificado", "sin guarda de pregunta vacía", "if not wanted:", "if False:"),
    ("rag-21-crag-simplificado", "límite alto exclusivo", "if score >= high:", "if score > high:"),
    ("rag-21-crag-simplificado", "límite bajo inclusivo", "if score < low:", "if score <= low:"),
    (
        "rag-21-crag-simplificado",
        "un reintento de más",
        "retries < max_retries",
        "retries <= max_retries",
    ),
    (
        "rag-21-crag-simplificado",
        "nunca reformula",
        'verdict == "ambiguo" and retries < max_retries',
        "False",
    ),
    (
        "rag-21-crag-simplificado",
        "responde con la pregunta original",
        "answer_fn(current, docs)",
        "answer_fn(question, docs)",
    ),
    (
        "rag-21-crag-simplificado",
        "no registra la traza",
        "trace.append((current, verdict))",
        "pass",
    ),
    (
        "rag-21-crag-simplificado",
        "devuelve la pregunta original al abstenerse",
        '"answer": None, "question": current',
        '"answer": None, "question": question',
    ),
    (
        "rag-21-crag-simplificado",
        "ignora los umbrales de crag_answer",
        "evaluate_retrieval(current, docs, high=high, low=low)",
        "evaluate_retrieval(current, docs)",
    ),
    # --- rag-10-metricas-recuperacion ---
    (
        "rag-10-metricas-recuperacion",
        "hit mira un resultado de más",
        "any(d in relevant for d in ranked[:k])",
        "any(d in relevant for d in ranked[: k + 1])",
    ),
    (
        "rag-10-metricas-recuperacion",
        "recall divide entre k",
        "len(set(ranked[:k]) & set(relevant)) / len(relevant)",
        "len(set(ranked[:k]) & set(relevant)) / k",
    ),
    ("rag-10-metricas-recuperacion", "recall sin None", "if not relevant:", "if False:"),
    (
        "rag-10-metricas-recuperacion",
        "precision divide entre los devueltos",
        "if d in relevant]) / k",
        "if d in relevant]) / max(len(ranked[:k]), 1)",
    ),
    (
        "rag-10-metricas-recuperacion",
        "posición desde 0",
        "enumerate(ranked[:k], start=1)",
        "enumerate(ranked[:k], start=0)",
    ),
    (
        "rag-10-metricas-recuperacion",
        "nDCG ideal sin recortar a k",
        "range(min(len(relevant), k))",
        "range(len(relevant))",
    ),
    (
        "rag-10-metricas-recuperacion",
        "nDCG sin recortar a k",
        "enumerate(ranked[:k]) if d in relevant",
        "enumerate(ranked) if d in relevant",
    ),
    (
        "rag-10-metricas-recuperacion",
        "nDCG sin guarda de ideal cero",
        "return dcg / ideal if ideal else 0.0",
        "return dcg / ideal",
    ),
    (
        "rag-10-metricas-recuperacion",
        "evaluate cuenta preguntas sin relevantes",
        'rows = [q for q in golden if q["relevant_ids"]]',
        "rows = list(golden)",
    ),
    (
        "rag-10-metricas-recuperacion",
        "evaluate falla si falta un ranking",
        'run.get(q["id"], [])',
        'run[q["id"]]',
    ),
    # --- rag-19-faithfulness ---
    (
        "rag-19-faithfulness",
        "la abstención cuenta como afirmación",
        'if answer.strip() == "NO_LO_SE":',
        "if False:",
    ),
    (
        "rag-19-faithfulness",
        "no quita las citas",
        'claims = [" ".join(_CITA.sub("", s).split()) for s in sentences]',
        'claims = [" ".join(s.split()) for s in sentences]',
    ),
    (
        "rag-19-faithfulness",
        "deja espacio antes de la puntuación",
        'claims = [re.sub(r"\\s+([.!?])", r"\\1", c) for c in claims]',
        "claims = list(claims)",
    ),
    (
        "rag-19-faithfulness",
        "conserva frases vacías",
        'return [c for c in claims if re.search(r"\\w", c)]',
        "return claims",
    ),
    (
        "rag-19-faithfulness",
        "ignora los números",
        "if any(n not in _NUMERO.findall(context) for n in _NUMERO.findall(claim)):",
        "if False:",
    ),
    (
        "rag-19-faithfulness",
        "raíz de 4 letras",
        "{t[:5] for t in tokenize(claim)}",
        "{t[:4] for t in tokenize(claim)}",
    ),
    (
        "rag-19-faithfulness",
        "umbral exclusivo",
        "len(words & available) / len(words) >= threshold",
        "len(words & available) / len(words) > threshold",
    ),
    (
        "rag-19-faithfulness",
        "afirmación sin palabras respaldada",
        "if not words:\n        return False",
        "if not words:\n        return True",
    ),
    (
        "rag-19-faithfulness",
        "score 0 si no hay afirmaciones",
        "if results else None",
        "if results else 0.0",
    ),
    (
        "rag-19-faithfulness",
        "context_recall sin umbral",
        "claim_supported(c, context_texts, threshold) for c in claims) / len(claims)",
        "claim_supported(c, context_texts) for c in claims) / len(claims)",
    ),
    # --- rag-17-cache-semantica ---
    (
        "rag-17-cache-semantica",
        "umbral exclusivo",
        "best_score >= self.threshold",
        "best_score > self.threshold",
    ),
    (
        "rag-17-cache-semantica",
        "ttl inclusivo",
        'now - entry["created"] > self.ttl',
        'now - entry["created"] >= self.ttl',
    ),
    (
        "rag-17-cache-semantica",
        "no caduca nada",
        "return self.ttl is not None and",
        "return False and",
    ),
    (
        "rag-17-cache-semantica",
        "un acierto no refresca el LRU",
        "            best = self.entries.pop(best_index)\n            self.entries.append(best)",
        "            best = self.entries[best_index]",
    ),
    (
        "rag-17-cache-semantica",
        "expulsa la más reciente",
        "self.entries.pop(0)",
        "self.entries.pop()",
    ),
    (
        "rag-17-cache-semantica",
        "elige la primera por encima del umbral",
        "if score > best_score:",
        "if score >= self.threshold:",
    ),
    (
        "rag-17-cache-semantica",
        "no cuenta los fallos",
        "        self.misses += 1\n        return None",
        "        return None",
    ),
    (
        "rag-17-cache-semantica",
        "vector sin normalizar",
        "return vector / norm if norm > 0 else vector",
        "return vector",
    ),
    # --- rag-18-recuperacion-con-acl ---
    (
        "rag-18-recuperacion-con-acl",
        "nivel de documento desconocido permitido",
        "if required is None:",
        "if False:",
    ),
    (
        "rag-18-recuperacion-con-acl",
        "usuario sin nivel es restringido",
        'LEVELS.get(user.get("level"), 0)',
        'LEVELS.get(user.get("level"), 2)',
    ),
    (
        "rag-18-recuperacion-con-acl",
        "restringido sin departamento",
        'return granted >= required and doc.get("department") in user.get("departments", [])',
        "return granted >= required",
    ),
    (
        "rag-18-recuperacion-con-acl",
        "interno exige más nivel",
        "    return granted >= required\n\n\ndef filter_docs",
        "    return granted > required\n\n\ndef filter_docs",
    ),
    (
        "rag-18-recuperacion-con-acl",
        "no filtra antes de puntuar",
        "allowed = filter_docs(user, docs)",
        "allowed = docs",
    ),
    (
        "rag-18-recuperacion-con-acl",
        "acepta puntuaciones nulas",
        "if s[0] > 0",
        "if s[0] >= 0",
    ),
    (
        "rag-18-recuperacion-con-acl",
        "empate por el último",
        "key=lambda s: (-s[0], s[1])",
        "key=lambda s: (-s[0], -s[1])",
    ),
    (
        "rag-18-recuperacion-con-acl",
        "la auditoría ignora ids inexistentes",
        "i not in docs_by_id or ",
        "",
    ),
    # --- agents-22-registro-de-tools ---
    (
        "agents-22-registro-de-tools",
        "permite nombres duplicados",
        "if name in self._tools:",
        "if False:",
    ),
    (
        "agents-22-registro-de-tools",
        "herramienta desconocida sin controlar",
        "if name not in self._tools:",
        "if False:",
    ),
    (
        "agents-22-registro-de-tools",
        "no exige los obligatorios",
        'for required in schema.get("required", []):',
        "for required in []:",
    ),
    (
        "agents-22-registro-de-tools",
        "acepta argumentos no declarados",
        'errors.append(f"argumento no esperado: {key}")',
        "pass",
    ),
    (
        "agents-22-registro-de-tools",
        "un booleano vale como entero",
        '"integer": lambda v: isinstance(v, int) and not isinstance(v, bool),',
        '"integer": lambda v: isinstance(v, int),',
    ),
    (
        "agents-22-registro-de-tools",
        "un booleano vale como número",
        '"number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),',
        '"number": lambda v: isinstance(v, (int, float)),',
    ),
    (
        "agents-22-registro-de-tools",
        "ignora el enum",
        'elif "enum" in prop and value not in prop["enum"]:',
        "elif False:",
    ),
    (
        "agents-22-registro-de-tools",
        "separador de errores distinto",
        '"; ".join(errors)',
        '", ".join(errors)',
    ),
    (
        "agents-22-registro-de-tools",
        "mensaje de excepción sin tipo",
        'f"{type(e).__name__}: {e}"',
        "str(e)",
    ),
    (
        "agents-22-registro-de-tools",
        "ejecuta aunque haya errores",
        "if errors:\n            return",
        "if False:\n            return",
    ),
    # --- agents-24-routing ---
    (
        "agents-24-routing",
        "no es palabra completa",
        'rf"\\b{re.escape(name)}\\b"',
        'rf"{re.escape(name)}"',
    ),
    ("agents-24-routing", "distingue mayúsculas", "flags=re.IGNORECASE", "flags=0"),
    (
        "agents-24-routing",
        "sin ruta por defecto",
        "    return default\n\n\ndef route_and_run",
        "    return None\n\n\ndef route_and_run",
    ),
    ("agents-24-routing", "texto None rompe", '.text or ""', ".text"),
    (
        "agents-24-routing",
        "ruta sin manejador no cae en default",
        "    if route not in handlers:\n        route = default\n",
        "",
    ),
    ("agents-24-routing", "el prompt no lleva la consulta", "\\n\\nConsulta: {query}", ""),
    # --- agents-25-votacion ---
    ("agents-25-votacion", "no normaliza", "key = normalize(answer)", "key = answer"),
    (
        "agents-25-votacion",
        "empate por el último",
        "-list(counts).index(k)",
        "list(counts).index(k)",
    ),
    (
        "agents-25-votacion",
        "devuelve el texto normalizado",
        "first_seen.setdefault(key, answer)",
        "first_seen.setdefault(key, key)",
    ),
    (
        "agents-25-votacion",
        "acuerdo sin guarda",
        "if winner is None:\n        return 0.0",
        "if False:\n        return 0.0",
    ),
    ("agents-25-votacion", "la coma no se convierte", '.replace(",", ".")', ""),
    ("agents-25-votacion", "primer número en vez del último", "numbers[-1]", "numbers[0]"),
    ("agents-25-votacion", "no descarta los None", "if e is not None]", "]"),
    (
        "agents-25-votacion",
        "umbral de acuerdo exclusivo",
        "share < min_agreement",
        "share <= min_agreement",
    ),
    ("agents-25-votacion", "ignora el umbral", "or share < min_agreement", ""),
    # --- agents-26-orquestador-workers ---
    ("agents-26-orquestador-workers", "no quita viñetas", "|[-*•])", ")"),
    (
        "agents-26-orquestador-workers",
        "conserva duplicados",
        "if clean and clean.lower() not in seen:",
        "if clean:",
    ),
    (
        "agents-26-orquestador-workers",
        "no limita las subtareas",
        "return subtasks[:max_subtasks]",
        "return subtasks",
    ),
    (
        "agents-26-orquestador-workers",
        "mensaje de error sin tipo",
        'f"error: {type(e).__name__}: {e}"',
        'f"error: {e}"',
    ),
    (
        "agents-26-orquestador-workers",
        "el prompt no lleva el máximo",
        "como máximo {max_subtasks} subtareas independientes",
        "subtareas independientes",
    ),
    (
        "agents-26-orquestador-workers",
        "el sintetizador recibe resultados y no pares",
        "list(zip(subtasks, results, strict=True))",
        "results",
    ),
    # --- agents-27-evaluador-optimizador ---
    (
        "agents-27-evaluador-optimizador",
        "empate sustituye al mejor",
        "if score > best_score:",
        "if score >= best_score:",
    ),
    (
        "agents-27-evaluador-optimizador",
        "objetivo exclusivo",
        "if score >= target:",
        "if score > target:",
    ),
    (
        "agents-27-evaluador-optimizador",
        "la mejora no reinicia la paciencia",
        "best, best_score, stale = draft, score, 0",
        "best, best_score = draft, score",
    ),
    (
        "agents-27-evaluador-optimizador",
        "paciencia exclusiva",
        "stale >= patience",
        "stale > patience",
    ),
    (
        "agents-27-evaluador-optimizador",
        "presupuesto exclusivo",
        "tokens >= budget_tokens",
        "tokens > budget_tokens",
    ),
    (
        "agents-27-evaluador-optimizador",
        "no cuenta el feedback en los tokens",
        "approx_tokens(draft) + approx_tokens(feedback)",
        "approx_tokens(draft)",
    ),
    (
        "agents-27-evaluador-optimizador",
        "el feedback no llega al generador",
        "draft = generate(task, feedback)",
        "draft = generate(task, None)",
    ),
]

survivors = []
for lab, desc, old, new in MUTANTS:
    source = (LABS / lab / "solution.py").read_text(encoding="utf-8")
    # `old`/`new` pueden ser textos o tuplas de textos (varias sustituciones en una mutación).
    pairs = list(zip(old, new)) if isinstance(old, tuple) else [(old, new)]
    # El texto debe aparecer UNA sola vez: si aparece también en un docstring, la mutación podría
    # aplicarse a un comentario y no al código, y el mutante sería ineficaz sin avisar.
    if any(source.count(o) != 1 for o, _ in pairs):
        print(f"!! NO SE PUDO APLICAR  [{lab}] {desc}")
        survivors.append((lab, desc, "no aplicable"))
        continue
    mutated = source
    for o, n in pairs:
        mutated = mutated.replace(o, n, 1)
    report = run_lab(mutated, (LABS / lab / "test_lab.py").read_text(encoding="utf-8"))
    failed = [r["name"] for r in report["results"] if not r["passed"]]
    killed = bool(report["load_error"]) or bool(failed)
    status = "detectado " if killed else "SOBREVIVE "
    print(f"{status} [{lab}] {desc}" + (f"  -> {len(failed)} test(s)" if killed and failed else ""))
    if not killed:
        survivors.append((lab, desc, "sobrevive"))

print(f"\n{len(MUTANTS) - len(survivors)}/{len(MUTANTS)} mutantes detectados")
sys.exit(1 if survivors else 0)
