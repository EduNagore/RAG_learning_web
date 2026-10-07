# RAG & Multi-Agent Academy

Web estática para aprender y practicar **RAG** y **sistemas de agentes y multiagente**, de los fundamentos a la preparación de entrevistas. Contenido en español, con los términos técnicos en inglés.

**Sitio publicado:** https://edunagore.github.io/RAG_learning_web/

## Qué contiene

| Sección                           | Qué hay                                                                                                                                                                                                                                                                     |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Teoría** (`/teoria/`)           | 19 módulos y 66 lecciones: fundamentos de LLM (M00), RAG (M01–M09), agentes y multiagente (M10–M17) y system design (M18). Cada lección cita fuentes que se abrieron y verificaron, indica su fecha de revisión y marca con `<Snapshot>` los datos que cambian con rapidez. |
| **Práctica** (`/practica/`)       | Más de 500 preguntas de test con corrección, modo examen, repaso espaciado (Leitner), 35 laboratorios de Python que se ejecutan en el navegador (Pyodide) con un modelo simulado, y un _playground_ opcional con tu propia clave de API.                                    |
| **Proyectos** (`/proyectos/`)     | 5 proyectos para construir en local con modelos y herramientas reales (código inicial en `projects/`).                                                                                                                                                                      |
| **Entrevistas** (`/entrevistas/`) | 80 preguntas con respuesta modelo en español e inglés (filtros y flashcards) y 6 casos de system design.                                                                                                                                                                    |
| **Glosario, fuentes y hojas**     | Glosario ES/EN, bibliografía agrupada por parte y hojas de resumen imprimibles.                                                                                                                                                                                             |
| **Progreso** (`/progreso/`)       | Lecciones leídas, notas y repaso. Todo se guarda en tu navegador; hay copia de seguridad (exportar e importar).                                                                                                                                                             |

Sin configurar nada, no hay servidor ni cuentas: todo el estado vive en `localStorage`. Opcionalmente se puede activar la **sincronización del progreso por usuario** (ver más abajo).

## Desarrollo local

Requisitos: Node ≥ 22.12, pnpm 12 (`npm install -g pnpm`), Python 3.14 y [uv](https://docs.astral.sh/uv/) (`python -m pip install --user uv`). En Windows, el PATH de Git Bash puede no incluir `uv`: usa `python -m uv ...`.

```bash
pnpm install
pnpm dev                     # http://localhost:4321/RAG_learning_web/
```

| Comando                                                   | Para qué                                                                                                                                              |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `pnpm check`                                              | Tipos (`astro check`)                                                                                                                                 |
| `pnpm lint` y `pnpm format:check`                         | ESLint y Prettier (`pnpm format` aplica el formato)                                                                                                   |
| `pnpm test`                                               | Tests unitarios (Vitest)                                                                                                                              |
| `pnpm validate`                                           | Validación del contenido (ver más abajo)                                                                                                              |
| `pnpm build`                                              | Construye `dist/` e indexa con Pagefind                                                                                                               |
| `pnpm test:e2e:sync`                                      | E2E de la sincronización (construye `dist-sync` con una URL de Supabase falsa y simula el backend; no llama a ningún servicio real)                   |
| `pnpm exec playwright install chromium` y `pnpm test:e2e` | Tests de extremo a extremo (necesitan `pnpm build` antes y usan `astro preview`; solo admite uno a la vez: `pnpm astro preview stop` si queda alguno) |
| `uv sync` y `uv run pytest`                               | Tests de los laboratorios (la solución pasa y el _starter_ falla)                                                                                     |
| `uv run ruff check .` y `uv run ruff format --check .`    | Lint y formato de Python                                                                                                                              |
| `uv run python scripts/mutate_labs.py`                    | Pruebas de mutación de los laboratorios                                                                                                               |
| `uv run python scripts/run_lesson_snippets.py`            | Ejecuta los bloques de Python de las lecciones y comprueba que no fallan                                                                              |
| `node scripts/check-freshness.mjs`                        | Lista las lecciones con la revisión vencida                                                                                                           |

Si `uv` falla con un error de certificado (red con inspección TLS), usa `uv sync --system-certs`.

## Estructura

```text
src/content/
  lessons/<modulo>/<NN-titulo>.mdx   Lecciones
  quizzes/<modulo>/<NN-titulo>.yaml  Preguntas de cada lección
  modules/<modulo>.yaml              Módulos (parte, orden, objetivos)
  labs/<id>/                         index.mdx, starter.py, solution.py, test_lab.py
  interview/<tema>.yaml              Preguntas de entrevista ES/EN
  cases/<caso>.mdx                   Casos de system design
  glossary/*.yaml                    Glosario ES/EN
  projects/<id>.mdx                  Guía de cada proyecto final
supabase/schema.sql                  Tabla, RLS y trigger de la sincronización del progreso (opcional)
projects/<id>/                       Código inicial de cada proyecto (proyectos uv independientes)
public/py/ragkit/                    Librería de los laboratorios (se ejecuta en Pyodide y en CI)
public/data/nimbus/                  Corpus ficticio (42 documentos) y conjunto de oro (31 preguntas)
src/components/                      content, quiz, lab, widgets, interview, playground, layout
src/lib/                             Lógica pura y testeada (quiz, srs, progreso, rrf, topología...)
scripts/                             validate-content, check-freshness, mutate_labs, run_lesson_snippets
tests/                               unit (Vitest), e2e (Playwright), labs (pytest)
docs/                                PLAN, PROGRESS, DECISIONS, SOURCES, CONTENT_GUIDELINES
```

Todas las rutas internas se construyen con el helper `url()` de `src/lib/url.ts` (respeta el `base` de GitHub Pages). No escribas enlaces absolutos `"/..."` a mano.

## Cómo añadir contenido

Lee primero [`docs/CONTENT_GUIDELINES.md`](docs/CONTENT_GUIDELINES.md). `pnpm validate` comprueba casi todo lo que sigue.

### Una lección

1. Crea `src/content/lessons/<modulo>/<NN-titulo>.mdx` con el frontmatter: `title`, `description`, `module`, `order`, `level`, `estimatedMinutes`, entre 3 y 5 `objectives`, `prerequisites` (opcional), `volatility` (`low`, `medium` o `high`), `lastReviewed`, al menos 2 `sources` (título, URL, tipo, autores y año) y `relatedLabs` (opcional).
2. Estructura: intuición, cómo funciona, **Trade-offs**, **Errores comunes**, un bloque `<Callout type="entrevista">` y `<KeyTakeaways>`. Mínimo 1.500 palabras sin contar código. Si `volatility` es `high`, incluye un `<Snapshot date="AAAA-MM">`.
3. **Abre cada fuente antes de citarla** y comprueba título, autores, año y la cifra que citas. No inventes URLs ni autores. Si dudas de algo, di que no está verificado.
4. Todo número que salga de código debe poder reproducirse: pon el código en la lección. Los bloques ejecutables de Python se prueban con `run_lesson_snippets.py`.
5. Crea el quiz `src/content/quizzes/<modulo>/<mismo-nombre>.yaml` (unas 8 preguntas: `single`, `multiple`, `truefalse`, `order` o `code-output`; cada una con `explanation` y `ref` a un ancla real de la lección; las explicaciones no pueden referirse a opciones por su posición porque se barajan; en cada módulo las verdadero/falso deben estar equilibradas).
6. Registra la lección en el módulo si procede y ejecuta `pnpm validate`.

### Un laboratorio

Carpeta `src/content/labs/<id>/` (prefijos `rag-` y `agents-`) con `index.mdx` (frontmatter y enunciado), `starter.py` (firmas y docstrings), `solution.py` y `test_lab.py` con al menos 4 tests y uno o más ocultos (`test_hidden_*`). Usa `ragkit` (`MockLLM`, `HashingEmbedder`, `load_corpus`...). Después:

```bash
uv run pytest tests/labs                  # la solución pasa y el starter falla
uv run python scripts/mutate_labs.py      # añade antes los mutantes de tu lab: errores típicos que los tests deben detectar
```

### Entrevistas, glosario y proyectos

- Preguntas: añade entradas a `src/content/interview/<tema>.yaml` (`id` único, `level`, `kind`, `es` y `en` con `q` y `a`, y `lessons`).
- Casos: `src/content/cases/NN-nombre.mdx` con las ocho secciones obligatorias y un diagrama.
- Glosario: `src/content/glossary/*.yaml` (`id`, `es`, `en`, `def`, `lessons`).
- Proyectos: guía en `src/content/projects/<id>.mdx` y carpeta `projects/<id>/` con `README.md`, `pyproject.toml` y `.env.example`. Nunca subas un `.env`. Comprueba versiones y APIs contra la documentación vigente y anota la fecha en `verified`.

## Sincronización del progreso por usuario (opcional)

Con la función activada, cada persona puede iniciar sesión con su correo (enlace mágico o código de 6 dígitos) y recuperar su progreso en cualquier dispositivo. **Sin sesión, o sin configurar el backend, la web funciona exactamente igual** y el progreso se guarda solo en el navegador. Funciona con [Supabase](https://supabase.com) (Auth y Postgres con Row Level Security).

Cómo está montada:

- **Local primero:** el progreso se guarda siempre en `localStorage`; la nube se sincroniza en segundo plano (con espera de unos segundos tras cada cambio y al ocultar la pestaña). Sin red, nada se pierde y se sube al volver.
- **Fusión, nunca sobrescritura:** `src/lib/merge.ts` fusiona dos copias campo a campo (lecciones leídas con la marca más reciente, mejor nota = máximo, lab superado no vuelve atrás, repaso espaciado por la respuesta más reciente, exámenes sin duplicados). Es una función pura, conmutativa, idempotente y asociativa (con una excepción documentada en `docs/DECISIONS.md` tras un «reiniciar»), y se prueba con propiedades.
- **Concurrencia:** cada fila tiene una `revision`; la subida solo se acepta si nadie cambió la fila entre medias, y si no, se vuelve a fusionar y se reintenta.
- **Esquema v2** del progreso, con migración automática desde la v1 (la clave de `localStorage` no cambia).

### Puesta en marcha (una vez)

1. Crea un proyecto en [supabase.com](https://supabase.com). En el plan gratuito (a octubre de 2026): 500 MB de base de datos, 50 000 usuarios activos al mes, 2 proyectos activos y **los proyectos gratuitos se pausan tras una semana sin actividad** (se reactivan a mano desde el panel).
2. En _SQL Editor_, pega y ejecuta [`supabase/schema.sql`](supabase/schema.sql): crea la tabla `progress`, activa RLS (cada persona solo accede a su fila), el trigger de revisión y un tope de tamaño.
3. En _Authentication → URL Configuration_: pon como _Site URL_ `https://edunagore.github.io/RAG_learning_web/` y añade a _Redirect URLs_ `https://edunagore.github.io/RAG_learning_web/progreso/` y, para desarrollo, `http://localhost:4321/RAG_learning_web/progreso/`.
4. En _Authentication → Email Templates → Magic Link_, incluye también `{{ .Token }}` en el mensaje (por ejemplo «Tu código: {{ .Token }}»). Así las personas pueden entrar con el código si el escáner de su correo ha gastado el enlace (los enlaces son de un solo uso, caducan a la hora y se puede pedir uno nuevo cada 60 segundos). El correo que envía Supabase por defecto tiene límites bajos; para uso real conviene configurar un SMTP propio.
5. Copia la _Project URL_ y la clave pública (`anon`/_publishable_, **nunca la `service_role`**) de _Project Settings → API_:
   - En local: `cp .env.example .env` y rellena `PUBLIC_SUPABASE_URL` y `PUBLIC_SUPABASE_ANON_KEY`.
   - En el despliegue: _Settings → Secrets and variables → Actions → Variables_ del repositorio, con esos mismos dos nombres. `deploy.yml` las lee al construir.
6. Comprueba las políticas RLS con el bloque de comentarios del final de `supabase/schema.sql` (un usuario no debe ver la fila de otro).

### Privacidad

Se guarda el correo (en el sistema de acceso de Supabase) y el progreso (lecciones leídas, notas, repaso, exámenes y el código de los laboratorios). No se guardan claves de API. La persona puede cerrar sesión (conservando o borrando el progreso de ese dispositivo) y «borrar mi copia en la nube». Eliminar también el correo del sistema de acceso lo hace quien administra el proyecto (panel de Supabase, _Authentication → Users_): el cliente no puede borrar usuarios.

## Calidad

- **CI** (`.github/workflows/ci.yml`, en cada _push_): `astro check`, ESLint, Prettier, Vitest, validación de contenido, build, Playwright (también el de sincronización), y por otro lado Ruff y pytest de los laboratorios.
- **Validación de contenido** (`pnpm validate`): módulos, orden y prerrequisitos; frontmatter de las lecciones y longitud mínima; anclas de los quizzes y equilibrio de respuestas; laboratorios completos; entrevistas (≥ 80, ids únicos, niveles repartidos), casos (secciones, longitud y diagrama), glosario y proyectos.
- **Accesibilidad**: `tests/e2e/a11y.spec.ts` ejecuta axe (WCAG A y AA) sobre las páginas representativas con tema claro y oscuro, y comprueba `prefers-reduced-motion`.
- **Rendimiento**: Lighthouse en local (octubre de 2026) sobre lecciones, laboratorios, entrevistas y fuentes: en móvil, Performance entre 92 y 100 y 100 en Accessibility, Best Practices y SEO; en escritorio, 100 en todo. Pyodide solo se descarga en los laboratorios (hay un test que lo comprueba).
- **Frescura**: `.github/workflows/content-freshness.yml` (el día 1 de cada mes y a demanda) revisa los enlaces externos y las lecciones con `lastReviewed` de hace más de 6 meses (3 si su volatilidad es alta) y abre o actualiza un issue con el informe.

## Despliegue

El sitio se publica en GitHub Pages con `.github/workflows/deploy.yml` en cada _push_ a `main`. En el repositorio: _Settings → Pages → Source: GitHub Actions_. El prefijo `base: '/RAG_learning_web'` y el `site` están en `astro.config.mjs`; si cambia el nombre del repositorio, cámbialos y revisa los enlaces de `README.md`.

Flujo de trabajo: una rama por cambio importante, puerta completa en verde y fusión a `main` con `--no-ff`.

## Más documentación

- [`docs/PLAN.md`](docs/PLAN.md): especificación completa.
- [`docs/PROGRESS.md`](docs/PROGRESS.md): estado y trampas conocidas.
- [`docs/DECISIONS.md`](docs/DECISIONS.md): decisiones y desviaciones del plan, con motivo.
- [`docs/SOURCES.md`](docs/SOURCES.md): fuentes verificadas y cuándo.

## Licencia

Todavía no se ha elegido una licencia: hasta que se añada un archivo `LICENSE`, todos los derechos están reservados. Los datos del corpus de Nimbus son ficticios.
