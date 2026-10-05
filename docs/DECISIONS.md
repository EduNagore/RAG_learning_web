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
