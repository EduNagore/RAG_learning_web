# PLAN — RAG & Multi-Agent Academy

Especificación completa para construir y desplegar una web de aprendizaje y práctica sobre **RAG (Retrieval-Augmented Generation)** y **sistemas de agentes / multi-agentes**. El objetivo final del usuario es llegar a una empresa de IA con nivel sólido (teoría + práctica + system design + entrevistas).

Este documento es la **fuente de verdad**. Si algo no está especificado aquí, elige la opción más simple que sea coherente con el resto del plan y documéntala en `docs/DECISIONS.md`.

---

## 1. Objetivos y principios

1. **Teoría estructurada por partes**, de cero a nivel avanzado/producción, con fuentes primarias citadas en cada lección.
2. **Práctica real**: ejercicios de código Python ejecutables y corregidos automáticamente en el navegador + tests tipo test sobre la teoría + proyectos finales para hacer en local con LLMs reales.
3. **Preparación para empresa**: system design de RAG/agentes, preguntas de entrevista, casos de estudio, glosario ES/EN.
4. **Actualizada y fiable**: cada lección tiene `sources` y `lastReviewed`; un workflow mensual detecta contenido caducado y enlaces rotos.
5. **100 % estática**: sin backend, sin base de datos, sin claves de API obligatorias. Se despliega en **GitHub Pages** con GitHub Actions.
6. **Idioma**: contenido en **español**, manteniendo los términos técnicos en inglés cuando así se usan en la industria (chunking, reranking, embeddings, handoff…). La primera vez que aparece un término: "fragmentación (*chunking*)". Glosario bilingüe. Preguntas de entrevista disponibles también en inglés.

---

## 2. Stack técnico

| Capa | Elección | Motivo |
|---|---|---|
| Framework web | **Astro 5** (`output: 'static'`) + **MDX** | Ideal para sitios de contenido; genera HTML estático; islas interactivas solo donde hacen falta. |
| Componentes interactivos | **React 19** como islas (`client:visible` / `client:load`) | Quizzes, laboratorio de código, widgets. |
| Lenguaje | **TypeScript** (strict) para la web; **Python** para ejercicios | Python es el lenguaje estándar en IA. |
| Estilos | **Tailwind CSS 4** + `@tailwindcss/typography` | Rápido, consistente, modo oscuro. |
| Contenido | **Astro Content Collections** con esquemas **Zod** | Valida frontmatter, quizzes y ejercicios en build. |
| Ejecución Python en navegador | **Pyodide** (última versión estable, fijada) en un **Web Worker**, cargado desde jsDelivr | Ejecuta Python + numpy en el cliente; funciona en GitHub Pages. |
| Editor de código | **CodeMirror 6** (`@uiw/react-codemirror` + `@codemirror/lang-python`) | Más ligero que Monaco. |
| Fórmulas | `remark-math` + `rehype-katex` | Coseno, BM25, RRF, nDCG… |
| Diagramas | **Mermaid** renderizado en cliente (lazy) dentro de un componente `<Diagram>` | Arquitecturas RAG, topologías multi-agente. |
| Resaltado de código | Shiki (integrado en Astro) | — |
| Búsqueda | **Pagefind** (`astro-pagefind`) | Búsqueda estática, sin servidor. |
| Estado / progreso | `nanostores` + `localStorage` (con export/import JSON) | Sin backend. |
| Tests web | **Vitest** (unit) + **Playwright** (e2e smoke) | — |
| Tests contenido Python | **pytest** con CPython (misma versión menor que Pyodide) | Valida que cada solución de referencia pasa sus tests. |
| Calidad | ESLint (flat config) + Prettier + `astro check`; **ruff** para Python | — |
| Gestor de paquetes | **pnpm**, Node **22 LTS** (`.nvmrc`); **uv** para Python | — |
| Despliegue | **GitHub Pages** vía `withastro/action` + `actions/deploy-pages` | Requisito del usuario. |

### Entorno de desarrollo (Windows 11)
- Node 22 LTS (`nvm-windows` o instalador oficial), `corepack enable` para pnpm.
- Python 3.x igual a la versión menor que trae la versión de Pyodide fijada (compruébalo en el changelog de Pyodide), gestionado con `uv`.
- VS Code con extensiones: Astro, Tailwind CSS IntelliSense, ESLint, Prettier, Python, Ruff, MDX.
- Scripts multiplataforma (nada de bash-only en `package.json`; usar Node o Python para scripts).

---

## 3. Despliegue en GitHub Pages

- `astro.config.mjs`:
  - `site: 'https://edunagore.github.io'`
  - `base: '/RAG_learning_web'` (nombre del repo; ajustar si cambia)
  - `trailingSlash: 'always'` (consistencia con Pages)
- **Todas** las rutas internas y assets deben construirse con un helper `url(path)` basado en `import.meta.env.BASE_URL`. Nunca enlaces absolutos `"/..."` a mano. Pyodide debe cargar los archivos de `public/py` y `public/data` usando ese helper.
- En GitHub: *Settings → Pages → Source: GitHub Actions*.
- Workflows en `.github/workflows/`:
  1. `ci.yml` (en PR y push): install → `astro check` → lint → vitest → `pytest` de ejercicios → validación de contenido → build → Playwright smoke contra `astro preview`.
  2. `deploy.yml` (push a `main` + manual): build con `withastro/action` y despliegue con `actions/deploy-pages`. Permisos: `pages: write`, `id-token: write`.
  3. `content-freshness.yml` (cron mensual + manual): `lychee` para enlaces rotos + script `scripts/check-freshness.mjs` que lista lecciones con `lastReviewed` > 6 meses o con `volatility: high` > 3 meses, y abre/actualiza un issue con la lista.
- **Primera tarea de la Fase 0**: desplegar un "hello world" para validar `base` y el workflow antes de construir nada más.

---

## 4. Arquitectura de la web (mapa de rutas)

```
/                         Inicio: qué es, ruta de aprendizaje, progreso global, "continuar donde lo dejaste"
/teoria/                  Índice de partes y módulos con % completado
/teoria/<modulo>/<leccion>/   Lección (MDX) + TOC + fuentes + mini-quiz al final + "siguiente"
/practica/                Hub de práctica: tests, laboratorios, examen, repaso
/practica/tests/          Lista de tests por módulo
/practica/tests/<modulo>/     Test del módulo (preguntas de todas sus lecciones)
/practica/labs/           Lista de laboratorios (filtros: parte, dificultad, estado)
/practica/labs/<id>/          Laboratorio: enunciado | editor | consola | tests | pistas | solución
/practica/examen/         Modo examen: N preguntas aleatorias, temporizador, informe final por módulo
/practica/repaso/         Repaso espaciado (Leitner) de preguntas falladas
/proyectos/               Proyectos finales para hacer en local con LLMs reales
/proyectos/<id>/
/entrevistas/             Preguntas de entrevista (ES/EN), system design, casos de estudio
/entrevistas/system-design/<caso>/
/glosario/                Glosario ES/EN con enlaces a lecciones
/fuentes/                 Bibliografía global agrupada por tema y tipo (paper/docs/blog)
/progreso/                Panel de progreso, export/import JSON, reset
```

Layout común: cabecera (logo, Teoría, Práctica, Proyectos, Entrevistas, buscador, toggle tema), sidebar con árbol de módulos en teoría, TOC lateral en lecciones, responsive (sidebar colapsable en móvil).

---

## 5. Estructura de archivos

```
RAG_learning_web/
├─ .github/workflows/{ci.yml, deploy.yml, content-freshness.yml}
├─ .nvmrc  .editorconfig  .prettierrc  eslint.config.js  tsconfig.json
├─ astro.config.mjs  package.json  pnpm-lock.yaml
├─ pyproject.toml                 # uv: pytest, ruff, numpy (versiones alineadas con Pyodide)
├─ docs/
│  ├─ PLAN.md                     # este documento
│  ├─ CONTENT_GUIDELINES.md       # reglas de redacción, fuentes y formato (ver §9)
│  ├─ SOURCES.md                  # lista curada de fuentes (ver §8)
│  └─ DECISIONS.md                # decisiones tomadas durante la implementación
├─ public/
│  ├─ py/ragkit/                  # librería didáctica Python (ver §7.3), servida estática a Pyodide
│  └─ data/                       # corpus de ejemplo, golden sets, embeddings precalculados
├─ src/
│  ├─ content.config.ts           # colecciones + esquemas Zod
│  ├─ content/
│  │  ├─ modules/<modulo>.yaml    # metadatos de módulo: id, parte, orden, título, descripción, objetivos
│  │  ├─ lessons/<modulo>/<NN-slug>.mdx
│  │  ├─ quizzes/<modulo>/<NN-slug>.yaml    # mismo slug que la lección
│  │  ├─ labs/<id>/
│  │  │  ├─ index.mdx             # frontmatter + enunciado
│  │  │  ├─ starter.py
│  │  │  ├─ solution.py
│  │  │  └─ test_lab.py           # tests visibles y ocultos (marcados)
│  │  ├─ projects/<id>.mdx
│  │  ├─ interview/questions.yaml
│  │  ├─ interview/cases/<caso>.mdx
│  │  └─ glossary/terms.yaml
│  ├─ components/
│  │  ├─ layout/ (Header, Sidebar, Toc, Footer, ThemeToggle, Breadcrumbs)
│  │  ├─ content/ (Callout, Diagram, SourceList, KeyTakeaways, Snapshot, Term)
│  │  ├─ quiz/ (Quiz.tsx, Question*.tsx, QuizResult.tsx)
│  │  ├─ lab/ (CodeLab.tsx, Editor.tsx, Console.tsx, TestResults.tsx)
│  │  ├─ widgets/ (ChunkingVisualizer, SimilarityPlayground, RRFCalculator, AgentLoopStepper, TopologyExplorer)
│  │  └─ progress/ (ProgressBar, ModuleProgress, ProgressPanel)
│  ├─ layouts/ (BaseLayout.astro, LessonLayout.astro, LabLayout.astro)
│  ├─ lib/
│  │  ├─ url.ts                   # helper base path
│  │  ├─ progress.ts              # nanostores + localStorage (versionado del esquema)
│  │  ├─ quiz.ts                  # corrección, puntuación, barajado con seed
│  │  ├─ srs.ts                   # Leitner (5 cajas)
│  │  └─ pyodide/{client.ts, worker.ts, runner.py}
│  ├─ pages/                      # rutas de §4
│  └─ styles/global.css
├─ projects/                      # código inicial de los proyectos locales (ver §7.4)
├─ scripts/
│  ├─ validate-content.mjs        # quiz ↔ lección existentes, ids únicos, enlaces internos válidos
│  ├─ check-freshness.mjs
│  └─ build_embeddings.py         # (opcional) precalcula embeddings reales del corpus
└─ tests/
   ├─ unit/                       # vitest: quiz.ts, srs.ts, progress.ts, url.ts
   ├─ e2e/                        # playwright: navegación, quiz, lab ejecuta y pasa
   └─ labs/test_all_labs.py       # pytest: cada solution.py pasa su test_lab.py; cada starter.py NO pasa
```

---

## 6. Esquemas de contenido (Zod)

**Lección** (`lessons`):
```ts
{
  title: string; description: string;
  module: string;            // id del módulo
  order: number;
  level: 'básico' | 'intermedio' | 'avanzado';
  estimatedMinutes: number;
  objectives: string[];      // 3-5 objetivos de aprendizaje
  prerequisites?: string[];  // ids de lecciones
  volatility: 'low' | 'medium' | 'high';   // high = frameworks, versiones, benchmarks
  lastReviewed: date;        // fecha de verificación de fuentes
  sources: { title: string; url: string; type: 'paper'|'docs'|'blog'|'spec'|'book'|'video'; authors?: string; year: number }[];  // mínimo 2
  relatedLabs?: string[];
}
```

**Quiz** (`quizzes`), un YAML por lección:
```yaml
lesson: rag-intro/01-que-es-rag
questions:
  - id: rag-intro-01-q1          # único global
    type: single                 # single | multiple | truefalse | order | code-output
    difficulty: 1                # 1-3
    prompt: "..."                # markdown permitido
    code: "..."                  # opcional (para code-output)
    options: ["...", "..."]      # para single/multiple/order (en order: orden correcto)
    answer: [1]                  # índices correctos (truefalse: [0]=verdadero)
    explanation: "..."           # por qué la correcta lo es Y por qué las otras no
    ref: "#seccion-ancla"        # ancla de la lección donde se explica
```

**Lab** (`labs`, frontmatter de `index.mdx`):
```ts
{
  title; description; part: 'rag'|'agents'|'fundamentos';
  module: string; difficulty: 1|2|3; estimatedMinutes: number;
  concepts: string[]; packages: string[];   // paquetes Pyodide extra (p.ej. 'networkx')
  hints: string[];                          // se revelan de una en una
  relatedLessons: string[];
}
```

**Progreso** (localStorage, clave `rma:progress:v1`):
```ts
{ lessonsRead: Record<lessonId, isoDate>;
  quizScores: Record<quizOrLessonId, { best: number; last: number; attempts: number }>;
  labs: Record<labId, { status: 'started'|'passed'; code: string; updatedAt: isoDate }>;
  srs: Record<questionId, { box: 1|2|3|4|5; due: isoDate }>;
  exams: { date; score; total; byModule: Record<string, number> }[]; }
```

---

## 7. Contenido

### 7.1 Teoría — partes, módulos y lecciones

Cada lección: 1.500–3.000 palabras, estructura fija (ver §9). Cada módulo ≥ 1 diagrama y ≥ 1 lab asociado.

**Parte 0 — Fundamentos**
- **M00 Fundamentos de LLMs para RAG y agentes**: tokens y ventana de contexto; sampling (temperature, top-p); prompting y system prompts; salidas estructuradas (JSON Schema); tool/function calling; embeddings (intuición); coste, latencia y prompt caching; limitaciones (alucinaciones, conocimiento congelado).

**Parte I — RAG**
- **M01 Introducción a RAG**: por qué RAG; RAG vs fine-tuning vs contexto largo; pipeline indexación → recuperación → generación; historia (REALM, RAG de Lewis et al. 2020, RETRO, Atlas); taxonomía Naive / Advanced / Modular / Agentic RAG.
- **M02 Ingesta y chunking**: parsing de PDF/HTML/tablas/imágenes (Docling, Unstructured, OCR, VLMs); limpieza, deduplicación, metadatos; estrategias de chunking (tamaño fijo, recursivo, por estructura, semántico, *late chunking*, *contextual chunking*); tamaño y solapamiento; PII.
- **M03 Embeddings y representaciones**: denso vs disperso (BM25, SPLADE); bi-encoders; MTEB y cómo leerlo; dimensión, Matryoshka, cuantización (int8/binaria); multilingüe; fine-tuning de embeddings; multimodal (CLIP, ColPali).
- **M04 Índices y bases de datos vectoriales**: búsqueda exacta vs ANN; HNSW, IVF, PQ, DiskANN; métricas (coseno, dot, L2); filtrado por metadatos (pre/post); comparativa pgvector, Qdrant, Weaviate, Milvus, Pinecone, Chroma, LanceDB, Elasticsearch/OpenSearch; criterios de elección.
- **M05 Recuperación avanzada**: búsqueda híbrida + Reciprocal Rank Fusion; reranking (cross-encoders, ColBERT/late interaction, rerankers LLM); transformación de consulta (rewriting, multi-query, HyDE, step-back, descomposición); routing; parent-document / small-to-big / sentence window; Contextual Retrieval (Anthropic); RAPTOR.
- **M06 Generación y gestión del contexto**: construcción del prompt; citas y grounding; "lost in the middle"; compresión de contexto; contexto largo vs RAG; prompt caching; responder "no lo sé" sin evidencia.
- **M07 RAG avanzado**: GraphRAG (Microsoft) y LightRAG; Self-RAG, CRAG, Adaptive-RAG; Agentic RAG; RAG multimodal; RAG sobre datos estructurados (text-to-SQL); RAG conversacional y memoria.
- **M08 Evaluación de RAG**: métricas de recuperación (hit rate, recall@k, precision@k, MRR, nDCG); métricas de generación (faithfulness, answer relevancy, context precision/recall); LLM-as-a-judge y sus sesgos; RAGAS, ARES, TruLens, DeepEval; golden sets y generación sintética; benchmarks (BEIR, MTEB, KILT, MultiHop-RAG, FRAMES); evaluación online y A/B.
- **M09 RAG en producción**: latencia y coste; caché semántica; actualización incremental de índices; seguridad (inyección indirecta vía documentos, recuperación con permisos/ACL, fuga de datos); observabilidad (trazas, OpenTelemetry GenAI semantic conventions, Langfuse, Arize Phoenix, LangSmith); guardrails; escalado.

**Parte II — Agentes y multi-agentes**
- **M10 Fundamentos de agentes**: qué es un agente; *workflows vs agents* (Anthropic, "Building effective agents"); el bucle del agente; ReAct; tool use; planificación; reflexión (Reflexion); memoria; context engineering.
- **M11 Patrones de workflows agénticos**: prompt chaining, routing, paralelización (sectioning/voting), orchestrator-workers, evaluator-optimizer; plan-and-execute, ReWOO, LLMCompiler.
- **M12 Arquitecturas multi-agente**: cuándo SÍ y cuándo NO (Anthropic multi-agent research system vs Cognition "Don't build multi-agents"); topologías (supervisor/jerárquica, red/peer-to-peer, handoffs/swarm, blackboard, pipeline secuencial); estado compartido vs paso de mensajes; debate multi-agente; role-playing (CAMEL), SOPs (MetaGPT, ChatDev); Generative Agents; economía de tokens; modos de fallo (taxonomía MAST, "Why Do Multi-Agent LLM Systems Fail?").
- **M13 Protocolos e interoperabilidad**: esquemas de tool calling; **MCP** (host/client/server, tools/resources/prompts, transportes stdio y Streamable HTTP, autorización, seguridad); **A2A** (Agent Card, tasks, messages, artifacts, streaming); Agent Skills; cómo encajan MCP + A2A.
- **M14 Frameworks**: LangGraph, OpenAI Agents SDK, Claude Agent SDK, Microsoft Agent Framework (sucesor de AutoGen), CrewAI, Google ADK, LlamaIndex Workflows, PydanticAI, smolagents; tabla comparativa (modelo mental, estado, durabilidad, multi-agente, MCP/A2A, observabilidad); cuándo no usar framework. **volatility: high**.
- **M15 Memoria, estado y control**: checkpointing y ejecución duradera; human-in-the-loop; memoria a largo plazo (MemGPT/Letta, Mem0); compactación de contexto; aislamiento de contexto con sub-agentes.
- **M16 Evaluación de agentes**: éxito de tarea, evaluación de trayectorias, precisión de tool calls; pass@k vs pass^k; benchmarks (SWE-bench Verified, GAIA, τ-bench/τ²-bench, WebArena, OSWorld, BFCL, Terminal-Bench); tracing y harness de evaluación.
- **M17 Fiabilidad y seguridad en producción**: prompt injection directa e indirecta; "lethal trifecta" (Simon Willison); sandboxing y mínimo privilegio; aprobación humana; control de coste y bucles infinitos; OWASP Top 10 for LLM Applications y OWASP Agentic AI; observabilidad.

**Parte III — Preparación profesional**
- **M18 System design y entrevistas**: método para responder un system design de RAG/agentes (requisitos → datos → recuperación → generación → evaluación → operación → coste/riesgos); casos de estudio (ver §7.5); errores típicos; cómo hablar de trade-offs.

### 7.2 Tests tipo test
- **Por lección**: 6–10 preguntas (mezcla de tipos y dificultades) al final de la lección.
- **Por módulo**: agrega todas las preguntas del módulo; aprobado ≥ 80 %.
- **Modo examen** (`/practica/examen/`): elige partes/módulos, nº de preguntas (20/40/60) y temporizador opcional; informe por módulo con enlaces a repasar.
- **Repaso espaciado**: toda pregunta fallada entra en la caja 1 del sistema Leitner; intervalos 1, 2, 4, 8, 16 días.
- Cada explicación justifica la correcta **y** las incorrectas, y enlaza a la sección de la lección.
- Objetivo de volumen: ≥ 500 preguntas en total.

### 7.3 Laboratorios de código (Pyodide, autocorregidos)

**Diseño del runtime**
- `src/lib/pyodide/worker.ts`: carga Pyodide, instala `numpy` (+ paquetes de `packages`), monta `public/py/ragkit` en el FS virtual, ejecuta el código del alumno y luego `test_lab.py` con un mini-runner (`runner.py`) que devuelve JSON `{name, passed, message, hidden}` por test. Captura stdout/stderr.
- Timeout: si el worker no responde en 10 s, se termina (`worker.terminate()`) y se recrea. Pyodide se carga **solo** al abrir un lab (lazy) con indicador de progreso.
- UI: enunciado (izquierda) | editor + botones *Ejecutar*, *Comprobar*, *Pista*, *Reiniciar*, *Ver solución* (tras 3 intentos o confirmación) | consola y resultados. El código se autoguarda en el progreso.

**`ragkit` (librería didáctica)** — todo determinista, sin red:
- `ragkit.llm.MockLLM`: LLM simulado con respuestas guionizadas (lista o reglas por patrón) y soporte de *tool calls* en formato tipo OpenAI/Anthropic; cuenta tokens aproximados y "coste".
- `ragkit.embeddings.HashingEmbedder` (determinista) y `PrecomputedEmbedder` (carga `public/data/*.npy` si existen).
- `ragkit.text`: tokenizador simple, normalización, stopwords ES/EN.
- `ragkit.data`: carga del corpus de ejemplo y golden set.
- `ragkit.agents`: utilidades mínimas (Message, ToolSpec, Trace) para que los labs de agentes se centren en la lógica.
- `ragkit.testing`: helpers de aserción con mensajes en español.

**Corpus de ejemplo** (`public/data/`): ~80–120 documentos ficticios en español de una empresa inventada ("Nimbus Logística": políticas, FAQ, manuales, incidencias), con metadatos (departamento, fecha, nivel de acceso) + golden set de ~50 preguntas con documentos relevantes y respuesta de referencia. Totalmente ficticio.

**Lista de labs (≥ 30)** — dificultad 1–3:

RAG:
1. Similitud coseno y top-k desde cero (numpy).
2. Chunker de tamaño fijo con solapamiento.
3. Chunker recursivo por separadores respetando tamaño máximo.
4. Chunking por estructura (Markdown headers) con metadatos de sección.
5. BM25 desde cero.
6. Índice vectorial brute-force con filtrado por metadatos.
7. Mini IVF (k-means + búsqueda en n clusters) y comparación de recall vs brute-force.
8. Búsqueda híbrida con Reciprocal Rank Fusion.
9. Reranking: reordenar candidatos con un scorer dado y medir mejora de nDCG.
10. Métricas de recuperación: hit rate, recall@k, MRR, nDCG@k.
11. Multi-query + fusión de resultados.
12. HyDE con `MockLLM`.
13. Construcción de prompt con citas `[doc_id]` y verificación de que cada cita existe en el contexto.
14. Reordenación de contexto contra "lost in the middle".
15. Parent-document retrieval (small-to-big).
16. Contextual chunk headers (prepend de contexto del documento).
17. Caché semántica con umbral.
18. Recuperación con permisos (ACL) — el usuario no debe ver documentos no autorizados.
19. Faithfulness simplificada: dividir respuesta en afirmaciones y comprobar soporte en el contexto.
20. Mini GraphRAG: grafo de entidades con `networkx` y respuesta multi-hop.
21. CRAG simplificado: evaluar relevancia y decidir reformular / responder / abstenerse.

Agentes y multi-agentes:
22. Registro de tools con validación de argumentos contra JSON Schema.
23. Bucle ReAct con `MockLLM` (observación → acción → resultado) y límite de pasos.
24. Workflow de routing (clasificar y enviar al handler correcto).
25. Paralelización con voting.
26. Orchestrator-workers: descomponer tarea, repartir, sintetizar.
27. Evaluator-optimizer con criterio de parada y presupuesto.
28. Supervisor multi-agente con handoffs y estado compartido.
29. Blackboard: agentes que leen/escriben en una pizarra común hasta consenso.
30. Mini grafo de estados tipo LangGraph con checkpoint y reanudación (human-in-the-loop).
31. Servidor MCP de juguete: manejar mensajes JSON-RPC `initialize`, `tools/list`, `tools/call`.
32. A2A: parsear Agent Cards y delegar una tarea al agente con la skill adecuada.
33. Guardas: detectar bucles, límite de coste/tokens, timeouts.
34. Defensa ante inyección indirecta: tool outputs con instrucciones maliciosas; aplicar allow-list y separación de datos/instrucciones.
35. Evaluación de trayectorias: comparar la traza del agente con una trayectoria de referencia y calcular métricas.

Cada lab: `starter.py` con firmas y docstrings, `solution.py` comentada, `test_lab.py` con ≥ 4 tests (al menos 1 oculto) y mensajes de error didácticos.

**Modo "LLM real" (opcional, Fase 6)**: un *playground* no evaluado donde el usuario puede poner su propia API key (se guarda solo en `localStorage`, con aviso claro) para probar prompts RAG sobre el corpus. Verificar en la documentación oficial actual cómo llamar a la API desde el navegador y qué modelos están vigentes. Nunca hay claves en el repo.

### 7.4 Proyectos finales (en local, con LLMs y herramientas reales)
Carpeta `projects/<id>/` con `README.md` (objetivos, arquitectura, pasos, criterios de evaluación, extensiones), `pyproject.toml` (uv), código inicial con TODOs y `.env.example`. Página en `/proyectos/<id>/`.
1. **RAG de producción sobre documentación**: ingesta (Docling), Qdrant o pgvector, búsqueda híbrida + reranker, citas, evaluación con RAGAS sobre golden set, trazas con Langfuse/Phoenix.
2. **Agentic RAG**: agente que decide cuándo recuperar, reformula y verifica (LangGraph).
3. **Sistema multi-agente de investigación**: orquestador + sub-agentes de búsqueda en paralelo + sintetizador con citas (LangGraph u OpenAI Agents SDK / Claude Agent SDK).
4. **Servidor MCP propio** con el SDK oficial (Python) exponiendo el índice RAG como tool/resource, y consumirlo desde un cliente MCP.
5. **Harness de evaluación de agentes**: dataset de tareas, ejecución repetida, pass@k / pass^k, análisis de fallos.

Las versiones de librerías y APIs de estos proyectos deben verificarse contra la documentación oficial vigente en el momento de implementarlos.

### 7.5 Zona de entrevistas
- `questions.yaml`: ≥ 80 preguntas (conceptuales, de diseño y de debugging) con respuesta modelo, en ES y EN, etiquetadas por tema y nivel (junior/mid/senior). Vista con "mostrar respuesta" y modo flashcard.
- Casos de system design (≥ 6): chatbot de soporte sobre documentación interna; buscador legal/regulatorio con citas; asistente de código sobre un monorepo; agente de investigación multi-agente; asistente de e-commerce con catálogo + políticas; copiloto interno con permisos por usuario. Cada caso: requisitos, preguntas de aclaración, arquitectura (diagrama), decisiones y trade-offs, evaluación, riesgos, coste, "qué diría un senior".
- Cheat sheets descargables (página imprimible) por parte.

---

## 8. Fuentes de información (fiabilidad y actualidad)

Regla general: **fuentes primarias primero**. Toda afirmación técnica no trivial debe poder rastrearse a una fuente de nivel 1 o 2. Las fuentes de nivel 3 están prohibidas como única fuente.

**Nivel 1 — Primarias**
- Papers (arXiv, ACL Anthology, NeurIPS/ICLR/ICML/EMNLP). Imprescindibles: RAG (Lewis et al. 2020), REALM, DPR, ColBERT/ColBERTv2, RETRO, HyDE, Lost in the Middle, Self-RAG, CRAG, RAPTOR, GraphRAG (Edge et al. 2024), LightRAG, RAGAS, ARES, BEIR, MTEB, SPLADE, Matryoshka Representation Learning, Late Chunking, ColPali; ReAct, Toolformer, Reflexion, Generative Agents, CAMEL, MetaGPT, ChatDev, AutoGen, multi-agent debate (Du et al.), "Why Do Multi-Agent LLM Systems Fail?" (MAST), surveys de Agentic RAG (Singh et al., arXiv 2501.09136) y de agentes LLM.
- Especificaciones: Model Context Protocol (modelcontextprotocol.io, spec y changelog), A2A Protocol (a2a-protocol.org / repositorio oficial), OpenTelemetry GenAI semantic conventions, JSON Schema.
- Documentación oficial: Anthropic (docs + Engineering blog: "Building effective agents", "Contextual Retrieval", "How we built our multi-agent research system", "Effective context engineering for AI agents", Agent Skills), OpenAI (docs, Agents SDK, Cookbook), Google (ADK, Gemini docs), Microsoft (Agent Framework, GraphRAG), LangChain/LangGraph, LlamaIndex, CrewAI, PydanticAI, Hugging Face (smolagents, Agents Course), bases vectoriales (Qdrant, Weaviate, Milvus, pgvector, Pinecone), RAGAS, DeepEval, Langfuse, Arize Phoenix, Pyodide.
- Leaderboards/benchmarks oficiales: MTEB (Hugging Face), SWE-bench, GAIA, τ-bench, BFCL, Terminal-Bench.

**Nivel 2 — Expertos reconocidos y blogs técnicos de empresas**
- Lilian Weng (LLM Powered Autonomous Agents), Chip Huyen (*AI Engineering*, O'Reilly 2025), Simon Willison (prompt injection, lethal trifecta), Hamel Husain y Shreya Shankar (evals), Eugene Yan (patterns for LLM systems), Jason Liu (RAG), Jerry Liu, Harrison Chase; Cognition ("Don't Build Multi-Agents"); blogs técnicos de Pinecone Learn, Weaviate, Qdrant, Cohere, Jina AI, Vespa; OWASP GenAI Security Project; cursos de DeepLearning.AI.

**Nivel 3 — No usar como fuente única**: blogs SEO, listados "Top 10 frameworks 2026", Medium/LinkedIn sin autoría experta, contenido generado sin referencias.

**Procedimiento al redactar cada lección**
1. Consultar con búsqueda web las fuentes de nivel 1–2 del tema **en el momento de redactar** (no fiarse solo de la memoria del modelo).
2. Para contenido `volatility: high` (frameworks, versiones de specs, rankings de benchmarks, precios, nombres de modelos): verificar en la fuente oficial, indicar la fecha ("a fecha de AAAA-MM") en un callout `<Snapshot>`, y nunca inventar cifras.
3. Separar conceptos estables (*evergreen*) de la foto del momento (*snapshot*).
4. Registrar todas las fuentes en el frontmatter y en `docs/SOURCES.md`; poner `lastReviewed` a la fecha real.
5. Si una afirmación no se puede verificar, eliminarla o marcarla explícitamente como opinión/tendencia citando quién la sostiene.

---

## 9. Guía de contenido (resumen; detallar en `docs/CONTENT_GUIDELINES.md`)

Estructura de cada lección:
1. **Objetivos** (del frontmatter).
2. **Intuición**: el problema que resuelve, con un ejemplo concreto.
3. **Cómo funciona**: explicación técnica, fórmulas (KaTeX) y diagrama.
4. **En código**: snippet Python mínimo (no ejecutable, de lectura) o enlace al lab.
5. **Trade-offs y cuándo usarlo / cuándo no.**
6. **Errores comunes en producción.**
7. **En una entrevista**: 2–3 preguntas típicas sobre el tema con pistas de respuesta.
8. **Ideas clave** (`<KeyTakeaways>`).
9. **Fuentes** (renderizadas automáticamente desde el frontmatter).
10. **Mini-quiz** (renderizado automáticamente desde el YAML).

Estilo: claro, directo, sin relleno; ejemplos con el corpus "Nimbus Logística" cuando sea posible; términos en inglés en cursiva la primera vez; sin emojis decorativos.

---

## 10. Widgets interactivos de teoría
- **ChunkingVisualizer** (M02): pegar texto, elegir estrategia/tamaño/solape, ver chunks coloreados.
- **SimilarityPlayground** (M03): frases + matriz de similitud (con `HashingEmbedder` portado a TS, o embeddings precalculados).
- **RRFCalculator** (M05): dos rankings → ranking fusionado paso a paso con la fórmula.
- **AgentLoopStepper** (M10): traza ReAct paso a paso (pensamiento → acción → observación).
- **TopologyExplorer** (M12): alternar entre topologías multi-agente y ver flujo de mensajes animado.

---

## 11. Calidad, accesibilidad y rendimiento
- Lighthouse ≥ 90 en Performance/Accessibility/Best Practices/SEO en páginas de teoría.
- Pyodide nunca se carga fuera de labs. Mermaid y widgets en `client:visible`.
- Accesibilidad: navegación por teclado en quizzes y editor, `aria-live` en resultados, contraste AA en ambos temas, `prefers-reduced-motion`.
- SEO: títulos, meta description, Open Graph, `sitemap` (`@astrojs/sitemap`).
- Validación de contenido en CI: todo quiz apunta a una lección existente; ids únicos; anclas `ref` existen; cada lección ≥ 2 fuentes; cada lab pasa con `solution.py` y falla con `starter.py`.

---

## 12. Fases de implementación

| Fase | Entregable | Criterio de "hecho" |
|---|---|---|
| **F0 Setup y despliegue** | Proyecto Astro + TS + Tailwind + lint + tests vacíos + workflows; hello world desplegado en Pages | URL pública funciona con `base` correcto; CI en verde. |
| **F1 Núcleo de teoría** | Layouts, header, sidebar, TOC, tema oscuro, componentes de contenido, búsqueda Pagefind, colecciones Zod, progreso; M00 completo como lección modelo | Navegación completa; lección modelo cumple §9. |
| **F2 Motor de tests** | Quiz por lección y por módulo, modo examen, repaso Leitner, panel de progreso con export/import | Tests unitarios de `quiz.ts`/`srs.ts`; e2e de un quiz. |
| **F3 Laboratorios** | Worker Pyodide, `ragkit`, corpus + golden set, UI de lab, labs 1, 5, 23 de punta a punta, `tests/labs/test_all_labs.py` en CI | Un lab se resuelve en el navegador desplegado; pytest en verde. |
| **— Pausa de revisión —** | Resumen al usuario y URL desplegada | El usuario valida antes de generar contenido masivo. |
| **F4 Contenido Parte I (RAG)** | M01–M09: lecciones, quizzes, labs 2–21, widgets de M02/M03/M05 | Validación de contenido en verde. |
| **F5 Contenido Parte II (Agentes)** | M10–M17: lecciones, quizzes, labs 22–35, widgets de M10/M12 | Ídem. |
| **F6 Profesional y extras** | M18, zona de entrevistas, casos de system design, glosario, fuentes, proyectos en `projects/`, playground "LLM real" opcional | Ídem. |
| **F7 Pulido** | Lighthouse, accesibilidad, workflow de frescura, README completo (cómo desarrollar, añadir lecciones/labs, desplegar) | Checklist §11 cumplido. |

Hacer **commit al final de cada fase** (y commits intermedios lógicos) con mensajes claros. Trabajar en ramas por fase y fusionar a `main` cuando la fase esté en verde, para que el despliegue solo ocurra con contenido validado.
