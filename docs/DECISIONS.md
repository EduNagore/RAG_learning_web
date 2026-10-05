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
