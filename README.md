# RAG_learning_web

RAG & Multi-Agent Academy: web para aprender y practicar RAG y sistemas multi-agente (teoría, tests y laboratorios de código).

- Especificación completa: [`docs/PLAN.md`](docs/PLAN.md)
- Estado de la implementación (punto de reanudación): [`docs/PROGRESS.md`](docs/PROGRESS.md)
- Decisiones de implementación: [`docs/DECISIONS.md`](docs/DECISIONS.md)
- Sitio publicado: https://edunagore.github.io/RAG_learning_web/

## Desarrollo local (Windows)

Requisitos: Node >= 22.12, pnpm 12 (`npm install -g pnpm`), Python 3.14 y [uv](https://docs.astral.sh/uv/) (`python -m pip install --user uv`).

```powershell
pnpm install
pnpm dev          # http://localhost:4321/RAG_learning_web/
pnpm check        # astro check (tipos)
pnpm lint
pnpm test         # vitest
pnpm build && pnpm test:e2e   # Playwright (necesita: pnpm exec playwright install chromium)
uv sync; uv run pytest        # tests de laboratorios
```

El README completo (cómo añadir lecciones, quizzes y labs, y cómo funciona el despliegue) se escribe en la fase F7.
