# Progreso de la implementación (punto de reanudación)

> **Si retomas el trabajo, lee solo este archivo primero.** Resume qué está hecho, dónde se quedó y qué hacer a continuación, para no gastar contexto en reconstruirlo. Mantenlo actualizado al cerrar cada fase o bloque importante. Especificación completa: [`PLAN.md`](PLAN.md). Decisiones y desviaciones: [`DECISIONS.md`](DECISIONS.md). Estándares de contenido: [`CONTENT_GUIDELINES.md`](CONTENT_GUIDELINES.md). Fuentes verificadas: [`SOURCES.md`](SOURCES.md).

**Última actualización:** 2026-10-06 · **Sitio:** https://edunagore.github.io/RAG_learning_web/ · **Repo:** https://github.com/EduNagore/RAG_learning_web

## Estado por fases

| Fase | Estado | Notas |
| ---- | ------ | ----- |
| F0 Setup y despliegue | ✅ hecha, en `main` y desplegada | Astro 7, Tailwind 4, CI, deploy a Pages |
| F1 Núcleo de teoría | ✅ hecha, en `main` y desplegada | Layouts, Pagefind, KaTeX, Mermaid, progreso, **M00 completo (8 lecciones)** |
| F2 Motor de tests | ✅ hecha, en `main` y desplegada | Quiz, examen, Leitner, panel de progreso, **65 preguntas de M00** |
| F3 Laboratorios | ✅ hecha, en `main` y desplegada (verificada en producción) | 3 labs, Pyodide, CodeMirror, e2e en navegador real |
| **Pausa de revisión tras F3** | ✅ superada | El usuario aprobó (2026-10-05, "haz todo lo que queda"): hacer F4–F7 completas |
| F4 Contenido Parte I (RAG, M01–M09) | ✅ hecha, en `main` y desplegada | 37 lecciones, 22 labs, 287 preguntas |
| F5 Contenido Parte II (Agentes, M10–M17) | ✅ hecha (en `main` y desplegada) | 63 lecciones en total, 35 labs, 495 preguntas |
| F6 Profesional y extras (M18, entrevistas, glosario, proyectos) | ✅ hecha, en `main` y desplegada | 66 lecciones, 80 preguntas de entrevista, 6 casos, 69 términos, 5 proyectos |
| F7 Pulido (Lighthouse, a11y, freshness workflow, README) | ✅ hecha, en `main` y desplegada | axe en e2e, Lighthouse ≥92, workflow de frescura, README completo |
| F8 Sincronización del progreso por usuario (opcional, `docs/PROMPT_SYNC.md`) | 🟡 implementada en `fase-8-sync` con backend simulado; falta crear el proyecto de Supabase y probarla en real | Desactivada por ausencia de variables |

Contadores finales (F7): 66 lecciones, 519 preguntas de quiz, 35 labs, 108 tests unitarios, 176 tests pytest, 310 mutantes, 46 e2e, 80 preguntas de entrevista, 6 casos, 69 términos, 5 proyectos. Contadores (fin de F5: 63 lecciones, 495 preguntas, 35 labs, 92 tests unitarios, 176 tests pytest, 310 mutantes, 32 e2e). Contadores (fin de F4): 19 módulos definidos, 37 lecciones (M00–M09), 287 preguntas, 22 labs, 76 tests unitarios, 111 tests pytest de labs, 184 mutantes de labs (todos detectados), 30 e2e, `main` = merge de `fase-4-rag` (6d54145), desplegado y verificado en producción.

## F4: HECHA (rama `fase-4-rag` fusionada en `main`)

- M01–M09 completos (lecciones, quizzes, labs rag-01…rag-21 más agents-23; widgets ChunkingVisualizer, SimilarityPlayground y RRFCalculator). `docs/SOURCES.md` (68 fuentes nuevas) y `docs/DECISIONS.md` (sección F4) actualizados.
- Puerta pasada: prettier, eslint, astro check, vitest, `pnpm validate`, build (83 páginas), ruff, pytest, mutación, snippets de lecciones (29 bloques), 30 e2e (también contra producción: smoke, widgets y diagramas), CI y despliegue en verde.
- Cambios de infraestructura de tests hechos en F4: los e2e ya no dependen del volumen de contenido (totales de lecciones, preguntas y labs calculados desde los ficheros) y hay un test (`diagrams.spec.ts`) que comprueba que **todos** los diagramas Mermaid de todas las lecciones se renderizan (cazó un diagrama roto en M05: poner entre comillas las etiquetas con paréntesis).
- Resultados medidos (no repetir experimentos): ver `docs/DECISIONS.md` (F4) y las propias lecciones.

### Siguiente paso
Hecho: ver «F5: HECHA».

## F5: HECHA (rama `fase-5-agentes` fusionada en `main`, merge ea1ed1c; CI y despliegue en verde, URLs verificadas en producción)

- M10–M17 completos: 26 lecciones nuevas (63 en total con M00–M09), quizzes de 8 preguntas por lección (495 preguntas en total), labs `agents-22` a `agents-35` (más `agents-23` de F3; 35 labs en total), widgets `AgentLoopStepper` (M10 L2) y `TopologyExplorer` (M12 L2).
- Puerta pasada (2026-10-06): prettier, eslint, astro check (0 errores), vitest (92), `validate` (63 lecciones, 495 preguntas, 35 labs), build (130 páginas), ruff, pytest (176), mutación (310/310), snippets de lecciones (55 bloques), 32 e2e.
- `docs/SOURCES.md` (60 fuentes de F5) y `docs/DECISIONS.md` (sección F5) actualizados. Hallazgo importante: **OWASP publicó la edición 2026 del LLM Top 10 el 2026-08-03**; M09 L2 y M17 usan la numeración 2025 con `<Snapshot>`.
- Notas de trabajo: lecciones ≥1500 palabras sin código (apuntar a ≈1800 desde el principio); `description`/`objectives` sin «: » sin comillas; mutantes añadidos con Edit anclando en el cierre `]` de `MUTANTS`; Mermaid no admite `;` en notas; `ruff format` cambia el texto de las soluciones (formatea antes de escribir mutantes); `uv` no está en el PATH (usar `.venv/Scripts/…`).

### Siguiente paso
Hecho: ver «F6: HECHA».

## F6: HECHA (rama `fase-6-profesional` fusionada en `main`, merge 46e99c2; CI y despliegue en verde, URLs verificadas en producción)

- ✅ M18 (3 lecciones). ✅ `/entrevistas/` (80 preguntas ES/EN, navegador con filtros, idioma y flashcards; 6 casos en `/entrevistas/system-design/<caso>/`). ✅ `/glosario/` (69 términos). ✅ `/fuentes/` (agregada de las lecciones). ✅ `/hojas/<parte>/` (hojas imprimibles). ✅ 5 proyectos (`projects/<id>/` + `/proyectos/<id>/`). ✅ Playground opcional `/practica/playground/`.
- Contadores: 66 lecciones, 519 preguntas de quiz, 35 labs, 80 preguntas de entrevista, 6 casos, 69 términos, 5 proyectos.
- Puerta pasada (2026-10-06): prettier, eslint, astro check, vitest (105), validate, build (151 páginas), ruff, pytest (176), mutación (310/310), snippets (57 bloques) y 40 e2e.

## F7: HECHA (rama `fase-7-pulido` fusionada en `main`, merge a06f7be; CI y despliegue en verde; a11y, calidad, entrevistas, playground y widgets verificados contra producción)

- ✅ Accesibilidad: `tests/e2e/a11y.spec.ts` (axe WCAG A/AA en 18 páginas, tema claro y oscuro, y `prefers-reduced-motion`). Arreglos: contraste de los comentarios de código y del texto secundario en oscuro, números de línea y fondo del editor en oscuro, foco del teclado en el editor y enlaces subrayados dentro de texto.
- ✅ Lighthouse en local (móvil: Performance 92–100, el resto 100; escritorio: 100 en todo).
- ✅ `scripts/check-freshness.mjs` (con tests) y `.github/workflows/content-freshness.yml` (mensual y manual: lychee sobre enlaces externos más el informe de frescura, y un issue único que se abre, actualiza o cierra).
- ✅ `tests/e2e/quality.spec.ts` (Pyodide solo en labs, SEO y sitemap). ✅ README completo.
- Puerta final (2026-10-06): prettier, eslint, astro check, vitest (108), validate, build (151 páginas), ruff, pytest (176), mutación (310/310), snippets (57 bloques) y 46 e2e. **Todas las fases F0–F7 están hechas.**
- Pendiente fuera de plan: elegir una licencia (`LICENSE`) y lanzar una vez `content-freshness.yml` a mano (_Actions → Run workflow_) para ver su primer informe real.
- Una vez, tras el despliegue, `quality.spec.ts` (Pyodide) falló contra producción y no se pudo reproducir en cinco ejecuciones más; se acotó el patrón de URL del test. Si reaparece, mira qué URL imprime el fallo.

### Mantenimiento
Cada mes llega el informe de frescura; al revisar una lección actualiza sus fuentes y `lastReviewed`. Si aparece una nueva edición de un estándar (como OWASP), mira primero si hay `<Snapshot>` que actualizar.

## F8: sincronización del progreso (rama `fase-8-sync`)

- ✅ Implementado: esquema v2 con migración desde la v1 (`src/lib/progress.ts`), fusión pura y probada por propiedades (`src/lib/merge.ts`), motor de sincronización con backend inyectable (`src/lib/sync.ts`), adaptador de Supabase (`src/lib/supabase.ts`), orquestación (`src/lib/syncClient.ts`), panel en `/progreso/` (`SyncPanel`) e indicador en la cabecera (`SyncBadge`), `supabase/schema.sql`, `.env.example`, variables en `deploy.yml`, `pnpm test:e2e:sync` (9 e2e con backend HTTP simulado; build aparte `dist-sync`; también en CI), README y `docs/DECISIONS.md` (sección F8) y `docs/SOURCES.md`.
- **Lo que falta y solo puede hacer el usuario** (no se fusiona con la función activa hasta entonces; ahora está desactivada por ausencia de variables): 1) crear el proyecto en Supabase; 2) ejecutar `supabase/schema.sql` en el editor SQL; 3) configurar *Site URL* y *Redirect URLs* y añadir `{{ .Token }}` a la plantilla del correo; 4) darme la *Project URL* y la clave pública (nunca la `service_role`) para ponerlas en `.env` y en las variables del repositorio; 5) probar juntos: iniciar sesión, dos navegadores, sin red, borrar la copia, y comprobar las políticas RLS con el bloque de comentarios de `schema.sql`.
- Riesgos abiertos: lo simulado en los e2e (cabeceras y códigos de PostgREST) se escribió de memoria; RLS, trigger y correos no están probados en real; el plan gratuito pausa el proyecto tras 1 semana sin actividad; no se puede borrar la cuenta desde el cliente (se explica en la web).

## F3: HECHA (referencia histórica)

### Detalle de F3 (histórico)

Rama `fase-3-labs` (creada desde `main`). Archivos ya escritos (commit WIP):

- `pyproject.toml`: dependencias fijadas a las versiones de Pyodide 314.0.7: `numpy==2.4.6`, `networkx==3.6.1` (`uv.lock` actualizado).
- `public/py/ragkit/`: `__init__.py`, `text.py`, `data.py`, `embeddings.py` (HashingEmbedder), `llm.py` (MockLLM, Message, ToolCall, LLMResponse), `agents.py` (ToolSpec, AgentResult), `testing.py`, `labrunner.py` (**contrato central**, ver abajo).
- `public/data/nimbus/corpus.json` (42 documentos ficticios, niveles public/internal/restricted) y `golden.json` (31 preguntas, 3 no respondibles, 1 restringida).

**Verificado (2026-10-05):** `ragkit` pasa ruff, importa y funciona (tokenize, HashingEmbedder, MockLLM, labrunner con número de línea del error). Corpus: 42 docs únicos (25 public, 15 internal, 2 restricted), golden de 31 preguntas sin referencias rotas y con `requires_access` coherente con la evidencia. **Commit WIP en la rama `fase-3-labs`** (no fusionar a `main` hasta terminar F3).

### Contrato del ejecutor de labs (`ragkit/labrunner.py`)
- Un lab = `index.mdx` + `starter.py` + `solution.py` + `test_lab.py` en `src/content/labs/<id>/`.
- Cada `def test_xxx(student)` de `test_lab.py` recibe el **módulo del alumno**; usa `assert`/`ragkit.testing.expect_*` con mensajes en español. Docstring = título visible. Prefijo `test_hidden` = test oculto (la UI lo muestra con nombre genérico).
- `run_lab(student_src, test_src) -> {"load_error": str|None, "results": [{name,title,hidden,passed,message,stdout}]}` y `run_code(src) -> {"stdout","error"}`. Es **el mismo código** en navegador (Pyodide) y en CI (CPython).
- En Pyodide: escribir `ragkit/*.py` en `/home/pyodide/py/ragkit/` y los datos en `/home/pyodide/data/nimbus/`; añadir `/home/pyodide/py` a `sys.path` (la estructura `py/ragkit` + `data/nimbus` es la que asume `ragkit.data`).

### Pendiente de F3, en orden

> **Actualización:** los pasos 4–7 están **HECHOS y verificados** (colección `labs`, worker/cliente de Pyodide, `CodeLab` con CodeMirror, páginas `/practica/labs/` y `/practica/labs/[id]/`, `relatedLabs` en las lecciones 5 y 6 de M00, validación de labs en `pnpm validate`, `tests/e2e/labs.spec.ts` con 8 tests en navegador real). **Solo quedan los pasos 8 y 9** (CI en verde, fusionar a `main`, verificar despliegue —incluido que un lab se resuelve en el sitio público— y **parar para resumir al usuario**). El detalle original de los pasos se conserva abajo por referencia.

1. ~~Verificar `ragkit`~~ (hecho).
2. ~~Tres labs de punta a punta~~ **HECHO** (ids `rag-01-coseno-topk`, `rag-05-bm25`, `agents-23-react`): enunciado, starter, solution, test_lab. Diseño acordado: lab 1 `cosine_top_k(query, matrix, k)`; lab 5 `bm25_scores(...)` con idf `ln(1+(N-n+0.5)/(n+0.5))` + búsqueda sobre el corpus (calcular los valores esperados con la solución y fijarlos en los tests); lab 23 bucle ReAct `run_agent(llm, tools, question, max_steps)` con `MockLLM` guionizado, errores de herramienta devueltos al modelo y límite de pasos.
3. ~~`tests/labs/test_all_labs.py` real~~ **HECHO** (16 tests en verde; además `scripts/mutate_labs.py`: 23 mutantes de error típico, todos detectados; ejecútalo al añadir labs: `uv run python scripts/mutate_labs.py`). Criterio original: por cada lab, `run_lab(solution)` pasa **todo** y `run_lab(starter)` **no** pasa todo (usa `ragkit.labrunner`, no reimplementar). Añadir `pythonpath = ["public/py"]` ya está en `pyproject.toml`.
4. Colección `labs` en `src/content.config.ts` (glob `**/index.mdx`, `generateId` = nombre de la carpeta; frontmatter del PLAN §6) y carga de los `.py` hermanos con `import.meta.glob('...?raw')`.
5. Web: `src/lib/pyodide/{client.ts,worker.ts}` (worker de tipo módulo; importar Pyodide con `import(/* @vite-ignore */ 'https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.mjs')`; cargar numpy/networkx con `loadPackage`; timeout 10 s con `worker.terminate()` y recrear; carga **solo** al abrir un lab), `CodeLab.tsx` con CodeMirror 6 (paquetes sueltos, no el wrapper), consola, resultados, pistas, reiniciar, ver solución (tras 3 intentos o confirmación), autoguardado en `progress.labs[id]` (estado `started`/`passed`), páginas `/practica/labs/` (lista con filtros) y `/practica/labs/[id]/`. Enlazar desde `/practica/` (hoy muestra "En construcción · F3").
6. `scripts/validate-content.mjs`: validar labs (archivos presentes, `relatedLabs` de lecciones, ids). Ya comprueba `relatedLabs` si existen carpetas.
7. e2e: abrir un lab en el navegador, ejecutar la solución y ver los tests en verde (requiere red a jsDelivr); también comprobar que el starter falla.
8. Documentar en `DECISIONS.md`, commit, push, esperar CI verde, fusionar a `main`, verificar despliegue.
9. **PARAR y resumir al usuario** (URL, qué funciona, decisiones, problemas) antes de F4.

**Estado tras el WIP (2026-10-05):** pasos 1–3 hechos. CodeMirror ya instalado (`codemirror`, `@codemirror/{state,view,lang-python,commands,language,theme-one-dark}`). En `labrunner.run_code` el código del alumno corre con `__name__ == "__main__"` (botón Ejecutar) y en `run_lab` con `student` (Comprobar), así los starters usan `if __name__ == "__main__":` para su demo. Falta desde el **paso 4**. Los labs usan `part: agentes` (no `agents`) para coincidir con las partes de los módulos; lab 1 → `m03-embeddings`, lab 5 → `m05-recuperacion-avanzada`, lab 23 → `m10-fundamentos-agentes`. Falta añadir `relatedLabs` al frontmatter de las lecciones correspondientes (la lección 6 de M00 → `rag-01-coseno-topk`, `rag-05-bm25`; la 5 → `agents-23-react`) y validar que `relatedLessons` de cada lab existe.

## Cómo trabajar (flujo por fase)
Rama por fase → `pnpm format` → `pnpm check` → `pnpm lint` → `pnpm test` → `pnpm validate` → `pnpm build` → `pnpm test:e2e` → `uv run ruff check . && uv run ruff format --check . && uv run pytest` → commit (con la línea `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`) → push → esperar CI (API de GitHub, ver abajo) → `git merge --no-ff` a `main` → push → verificar deploy y URLs.

Esperar CI sin `gh`: bucle en segundo plano con `curl -s https://api.github.com/repos/EduNagore/RAG_learning_web/actions/runs?branch=<rama>&per_page=1` hasta `status=completed` (el repo es público; no hace falta token).

## Trampas conocidas (no repetir)
- **TLS interceptado en esta máquina** (`UnknownIssuer`): `uv` necesita `--system-certs`; Python con `truststore` (`truststore.inject_into_ssl()`) para scripts sueltos. Nunca desactivar la verificación.
- **`uv` y `pnpm` no están en el PATH de Git Bash como `uv`:** usar `python -m uv ...`. `pnpm` sí funciona.
- **Heredocs múltiples en un solo comando de Bash fallan** ("unexpected EOF"): crear archivos con la herramienta Write (o un script de Node en el scratchpad).
- **`pnpm format` reformatea `scripts/` y `src/`:** si luego haces `replace` por texto, puede no encontrarse y fallar en silencio. Usa Edit o comprueba que el cambio se aplicó. `docs/` está excluido de Prettier.
- **Rutas en Node/Windows:** `/tmp` no es `C:\tmp`; para ficheros temporales usa el directorio scratchpad con ruta Windows.
- **Playwright `workers: 1`** (varios workers dan parones de ~10 s sin causa identificada). **Astro 7 solo permite un `astro preview`**: antes de `pnpm test:e2e` ejecuta `pnpm astro preview stop` si dejaste uno.
- **Quizzes:** las opciones se barajan, así que las explicaciones no pueden decir "la primera opción" (regla de CI); verdadero/falso equilibradas (regla de CI); `ref` debe ser un ancla real.
- **Lecciones:** mínimo 1.500 palabras sin código, sección "Trade-offs", "Errores comunes", `<Callout type="entrevista">`, `<KeyTakeaways>`, `<Snapshot>` si `volatility: high` (todo en CI vía `pnpm validate`). Verificar cada fuente abriéndola y **ejecutar** todo código/cálculo que se cite.
- **Pruebas de mutación:** cuando añadas una regla o un test importante, rómpelo a propósito para comprobar que falla (ya cazó dos reglas que no se aplicaban).

## Versiones fijadas (verificadas 2026-10-05)
Astro 7.3.5, `@astrojs/mdx` 8, React 19.3, Tailwind 4.3, TypeScript 6.0.x (la 7 rompe `@astrojs/check`), ESLint 10, Vitest 5, Playwright 1.63, pnpm 12.9.1, Node 22 en CI (24 en local), Python 3.14. Pyodide **314.0.7** (CDN `https://cdn.jsdelivr.net/pyodide/v314.0.7/full/`): numpy 2.4.6, networkx 3.6.1, scipy 1.18.0, pydantic 2.12.5. Actions: checkout v7, withastro/action v6, deploy-pages v5, setup-node v7, pnpm/action-setup v6, `astral-sh/setup-uv@v10.2.0` (sin etiqueta mayor).

## Contenido existente
- **M00 Fundamentos de LLMs** (8 lecciones en `src/content/lessons/m00-fundamentos-llm/`, quizzes en `src/content/quizzes/m00-fundamentos-llm/`): tokens y contexto, sampling, prompting, salidas estructuradas, tool calling, embeddings, coste/caching, limitaciones. Todas con fuentes verificadas (ver `SOURCES.md`).
- Los otros 18 módulos existen como YAML en `src/content/modules/` pero **sin lecciones** (aparecen como "próximamente").
- Páginas "En construcción" que se rellenan en F6: `/proyectos/`, `/entrevistas/`, `/glosario/`, `/fuentes/`.
