# Decisiones de implementación

Desviaciones o elecciones respecto a `PLAN.md`, con fecha y motivo.

## 2026-10-05 · F0

- **Astro 7 en lugar de Astro 5.** `PLAN.md` decía Astro 5, pero la versión estable actual es la 7.3.5 y `@astrojs/mdx` 8 (la actual) la exige como peer. Se usa la versión vigente para no construir sobre una rama sin soporte. Cuando `PLAN.md` diga "Astro 5", léase "Astro vigente".
- **Node 22 en CI, Node 24 en local.** `.nvmrc` y los workflows fijan 22 (Astro exige >=22.12). El equipo local tiene Node 24; no hay diferencias relevantes para este proyecto.
- **pnpm 12.9.1** instalado con `npm install -g pnpm` (no `corepack enable`, que necesita permisos de administrador en Windows). Fijado en `packageManager`.
- **Scripts de build en pnpm 12:** la aprobación de scripts de dependencias va en `pnpm-workspace.yaml` (`allowBuilds`), no en `package.json`. Solo se aprueba `esbuild`, por su postinstall estándar.
- **Python 3.14 para los tests de labs.** Pyodide 314.x trae Python 3.14.x, así que pytest corre con 3.14. En local se usa el Python 3.14.3 ya instalado en el sistema: `uv python install 3.14` falló por un error de certificado TLS (`UnknownIssuer`, probablemente un proxy o antivirus) y no se desactivó la verificación. CI usa `actions/setup-python` con 3.14.
- **Versiones de las GitHub Actions** (últimas releases a 2026-10-05): checkout v7, withastro/action v6, deploy-pages v5, setup-node v7, setup-python v7, pnpm/action-setup v6.
- **`gh` no está instalado**, así que Pages no se puede activar por CLI: hay que hacerlo a mano en *Settings → Pages → Source: GitHub Actions*.
- **TypeScript 6.0.x, no 7.** `@astrojs/check` (`^5 || ^6`) y `typescript-eslint` (`<6.1`) no soportan aún TypeScript 7.x, que es la última. Fijado `typescript@~6.0.3`. Revisar cuando ambos amplíen su rango.
- **ESLint 10 con `defineConfig` de `eslint/config`** (`tseslint.config` está deprecado).
- **TLS en local:** `uv` falla con `UnknownIssuer` contra PyPI. Se resuelve con `uv sync --system-certs` (usa el almacén de certificados de Windows y mantiene la verificación). No se desactiva la verificación TLS en ningún caso. CI no lo necesita.
- **`docs/` excluido de Prettier** para que formatear el repo no reescriba el plan (tablas, comillas dentro de bloques de código).
- **README original en UTF-16** (lo creó PowerShell); Prettier lo corrompió, se reescribió en UTF-8 con el mismo título.
- **`.gitattributes` con `eol=lf`** para evitar CRLF en lockfiles, YAML y `.py` que se sirven a Pyodide.
- **CI se ejecuta en cada push** (cualquier rama), no en `pull_request`, para no duplicar ejecuciones; el repo lo usa una sola persona.
- **`astral-sh/setup-uv` se fija a `v10.2.0`:** el proyecto no publica la etiqueta mayor flotante `v10`.

## 2026-10-05 · F1

- **Plugins de Markdown en Astro 7:** el procesador por defecto ya no es remark. Para usar `remark-math` y `rehype-katex` hay que instalar `@astrojs/markdown-remark` (peer opcional de Astro) y configurar `markdown.processor: unified({ remarkPlugins, rehypePlugins })`. MDX 8 hereda esa configuración. Zod se importa de `astro/zod`.
- **`astro-pagefind` se importa con extensión:** `astro-pagefind/components/Search.astro` (el export sin extensión no resuelve en TypeScript).
- **Buscador en móvil:** en la cabecera el buscador solo se muestra desde `md`; en pantallas pequeñas hay un enlace a `/buscar/`. Pagefind solo indexa las páginas con `data-pagefind-body` (lecciones). El índice solo existe tras `pnpm build`, no en `pnpm dev`.
- **Aviso `MODULE_LEVEL_DIRECTIVE "use astro:head-inject"` en el build:** viene de Rolldown al procesar MDX. Se verificó en el HTML generado que los estilos, el KaTeX y los scripts de los componentes sí llegan a la página, así que se considera benigno. Si algún día faltan estilos o scripts en una lección, revisar esto primero.
- **Aviso de tamaño de chunk (>500 kB):** es Mermaid, que se carga en diferido solo cuando hay un diagrama visible.
- **`eslint-plugin-jsx-a11y` declara soporte hasta ESLint 9** y usamos ESLint 10 (`pnpm peers check`). El lint funciona; se mantiene porque la accesibilidad es requisito del plan. Revisar cuando el plugin amplíe su rango.
- **Astro 7 solo permite un `astro preview` por proyecto.** Si queda uno en marcha, `pnpm test:e2e` falla con "Another astro preview server is already running"; se para con `pnpm astro preview stop`.
- **Playwright con `workers: 1`.** Con varios workers (7 por defecto en esta máquina) aparecían parones de ~10 s por test y fallos aleatorios. Se descartó el servidor (30 peticiones simultáneas responden en ~9 ms), la concurrencia de navegadores (8 Chromium cargando en paralelo tardan ~160 ms) y procesos huérfanos. **No se identificó la causa raíz.** Con un worker la suite (7 tests) pasa en ~5 s y es estable. Revisar si la suite crece mucho.
- **Marcado de lecciones leídas** en el índice y la barra lateral: scripts del cliente que leen `localStorage` con `loadProgress()`; el estado vive en `src/lib/progress.ts` (puro y testeado) y el store de `nanostores` solo se usa en islas de React.
- **Validación de contenido (`pnpm validate`, en CI):** `scripts/validate-content.mjs` comprueba lo que Zod no ve: módulo ↔ carpeta, `order` únicos, prerequisitos existentes, estructura de lección (§9 del plan: sección de trade-offs, errores comunes, callout de entrevista, ideas clave), `<Snapshot>` obligatorio si `volatility: high`, longitud mínima de 1.500 palabras sin código y, cuando existan, quizzes (lección existente, ids únicos, anclas `ref` válidas). Las lecciones sin quiz o sin diagrama solo dan aviso.
- **Longitud mínima de lecciones:** al primer pase cinco lecciones de M00 quedaban en 1.250–1.400 palabras. Se amplió con contenido útil (medir variación, reintentos, diseño de herramientas, caso recorrido…) en lugar de bajar el umbral.
- **Código de las lecciones verificado ejecutándolo:** los fragmentos ejecutables de Python de M00 se extrajeron y se ejecutaron (cosine top-k, caching, softmax/top-p) y sus salidas coinciden con lo que afirma el texto. Las cifras de tokenización salen de `tiktoken` (cl100k_base y o200k_base) ejecutado el 2026-10-05.
- **TLS interceptado y `tiktoken`:** su descarga fallaba con el mismo error de certificado. Se resolvió con `truststore` (Python usa el almacén de Windows) sin desactivar la verificación; solo se usó en un script temporal fuera del repo.
- **Pagefind** indexa solo las páginas con `data-pagefind-body` (`page_count: 8` = las lecciones), aunque el log diga "indexed 18 pages" (son las páginas rastreadas). Hay un e2e que busca "caching" y espera la lección correcta.
- **Cifras de proveedor en M00 con `<Snapshot>`:** tamaños de ventana, multiplicadores y precios de caching, sobrecoste de herramientas, parámetros de sampling no admitidos en Sonnet 5.5, límites de salidas estructuradas. Todas verificadas el 2026-10-05 contra la documentación oficial.

## 2026-10-05 · F2

- **Islas de quiz con `client:only="react"`** (sin renderizado en servidor): las opciones se barajan con una semilla aleatoria y renderizar en servidor produciría un desajuste de hidratación. Los quizzes necesitan JavaScript de todos modos.
- **Banco de preguntas estático** en `/data/questions.json` (generado en build por un endpoint de Astro, ~86 kB con 65 preguntas) que cargan el examen y el repaso. El mini-test de cada lección recibe sus preguntas por props. Con 500+ preguntas rondará los 650 kB sin comprimir; GitHub Pages lo sirve comprimido.
- **Markdown de preguntas renderizado en build** con `marked`, con el HTML crudo **escapado** (si no, `<documents>` en una pregunta sobre prompts se interpretaría como etiqueta).
- **`updateProgress` parte siempre de `localStorage`**, no del store en memoria. Antes, una isla que grabara sin haberse hidratado habría **borrado todo el progreso guardado**. Hay un test de regresión que falla sin el arreglo.
- **Notas como porcentajes enteros (0-100)** en `quizScores` y `byModule`. Aprobado = 80 %.
- **Test de módulo:** con ~64 preguntas por módulo se ofrece un test rápido (muestra de 20 repartida entre lecciones con `buildExam`) y un test completo. La nota guardada (`module:<id>`) es la mejor de cualquiera de los dos.
- **Examen:** las preguntas `order` sin tocar cuentan como respondidas (su orden inicial nunca es la solución). Las falladas pasan al repaso espaciado y las acertadas que ya estaban en Leitner suben de caja. Sin respuesta cuenta como fallo.
- **Repaso espaciado (Leitner):** cajas 1-5 con intervalos de 1, 2, 4, 8 y 16 días. Un fallo vuelve a la caja 1; un acierto sube una; acertar una pregunta que no está en el sistema no crea tarjeta. El repaso graba cada respuesta al instante (no al terminar la sesión) y no altera las notas de los tests. Sesiones de hasta 20 preguntas.
- **Equilibrio de verdadero/falso como regla de CI.** Mi primer borrador de M00 tenía las 8 respuestas en "Falso"; ahora `pnpm validate` falla si en un módulo con ≥4 una respuesta supera el 80 %. La regla se probó con una mutación (0 V / 8 F falla; 4/4 pasa). *Lección aprendida:* mi primer intento de añadir la regla no se aplicó porque Prettier había reformateado el script y mi `replace` no encontró el texto; la prueba de mutación lo destapó.
- **Pruebas de mutación manuales** de los tests de F2: romper `isCorrect` hace fallar los e2e de fallo y examen; quitar el arreglo de `updateProgress` hace fallar su test unitario.
- **Sin referencias posicionales en las explicaciones de los quizzes (regla de CI).** Las opciones se barajan al mostrarlas, así que "(la primera opción)" o "las tres primeras" no significan nada para quien las ve en otro orden. Lo descubrí con una captura de pantalla (la "primera opción" aparecía en tercer lugar), no con los tests. `pnpm validate` ahora lo rechaza; al activarla marcó exactamente las 13 preguntas afectadas, que se reescribieron describiendo el contenido.
- **Pregunta de ordenar en móvil:** los botones Subir/Bajar pasan debajo del texto cuando no caben (antes dejaban el texto en una columna muy estrecha).
