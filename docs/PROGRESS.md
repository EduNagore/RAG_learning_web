# Progreso de la implementación (punto de reanudación)

> **Si retomas el trabajo, lee solo este archivo primero.** Resume qué está hecho, dónde se quedó y qué hacer a continuación, para no gastar contexto en reconstruirlo. Mantenlo actualizado al cerrar cada fase o bloque importante. Especificación completa: [`PLAN.md`](PLAN.md). Decisiones y desviaciones: [`DECISIONS.md`](DECISIONS.md). Estándares de contenido: [`CONTENT_GUIDELINES.md`](CONTENT_GUIDELINES.md). Fuentes verificadas: [`SOURCES.md`](SOURCES.md).

**Última actualización:** 2026-10-05 · **Sitio:** https://edunagore.github.io/RAG_learning_web/ · **Repo:** https://github.com/EduNagore/RAG_learning_web

## Estado por fases

| Fase | Estado | Notas |
| ---- | ------ | ----- |
| F0 Setup y despliegue | ✅ hecha, en `main` y desplegada | Astro 7, Tailwind 4, CI, deploy a Pages |
| F1 Núcleo de teoría | ✅ hecha, en `main` y desplegada | Layouts, Pagefind, KaTeX, Mermaid, progreso, **M00 completo (8 lecciones)** |
| F2 Motor de tests | ✅ hecha, en `main` y desplegada | Quiz, examen, Leitner, panel de progreso, **65 preguntas de M00** |
| F3 Laboratorios | 🟡 **código completo y verificado; falta CI, fusionar a `main` y el resumen al usuario** (rama `fase-3-labs`) | Ver "F3: dónde me quedé" |
| **Pausa de revisión tras F3** | ⏳ | **Detenerse y dar resumen al usuario antes de F4** (lo exige el prompt) |
| F4 Contenido Parte I (RAG, M01–M09) | ⬜ | |
| F5 Contenido Parte II (Agentes, M10–M17) | ⬜ | |
| F6 Profesional y extras (M18, entrevistas, glosario, proyectos) | ⬜ | |
| F7 Pulido (Lighthouse, a11y, freshness workflow, README) | ⬜ | |

Contadores a fecha de hoy: 19 módulos definidos (solo M00 con lecciones), 8 lecciones, 65 preguntas, 3 labs, 51 tests unitarios, 27 e2e, 16 tests de labs + 23 mutantes, `main` = `49a01f5` (F3 aún sin fusionar).

## F3: dónde me quedé

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
