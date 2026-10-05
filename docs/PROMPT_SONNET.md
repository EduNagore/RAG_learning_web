Vas a construir y desplegar una web de aprendizaje sobre RAG y sistemas multi-agente. La especificación completa está en `docs/PLAN.md`: léela entera antes de empezar y trátala como fuente de verdad. Si algo no está especificado, elige la opción más simple coherente con el plan y anótala en `docs/DECISIONS.md`.

Contexto:
- Repo: `C:\dev\RAG_learning_web` (Windows 11). Usuario de GitHub: `EduNagore`. Se despliega en GitHub Pages con GitHub Actions (`site: https://edunagore.github.io`, `base: /RAG_learning_web`).
- Web 100 % estática: Astro 5 + MDX + React (islas) + TypeScript strict + Tailwind 4; ejercicios de Python ejecutados en el navegador con Pyodide en un Web Worker. Sin backend y sin claves de API en el repo.
- Contenido en español, manteniendo los términos técnicos en inglés como se usan en la industria.

Cómo trabajar:
1. Sigue las fases de §12 del plan en orden (F0 → F7). Antes de cada fase, crea una lista de tareas. Al terminar cada fase, ejecuta `astro check`, lint, vitest, pytest de labs y build; arregla lo que falle y haz commit. Trabaja en una rama por fase y fusiona a `main` solo cuando todo esté en verde.
2. En F0, lo primero es desplegar un "hello world" en GitHub Pages para validar el `base` y el workflow. Todas las rutas internas y assets deben pasar por el helper `url()` basado en `import.meta.env.BASE_URL`.
3. Antes de instalar dependencias, comprueba en la documentación oficial las versiones estables actuales (Astro, Tailwind, Pyodide, etc.) y fíjalas. La versión de Python para pytest debe coincidir con la versión menor de Python que trae la versión de Pyodide que fijes.
4. Para la teoría, sigue la sección §8 (fuentes) y §9 (estructura de lección) **estrictamente**:
   - Antes de redactar cada lección, usa la búsqueda web para consultar las fuentes primarias (papers, specs, documentación oficial, blogs de ingeniería de los laboratorios) y no te fíes solo de tu memoria.
   - Todo lo que cambie con el tiempo (frameworks, versiones de MCP/A2A, benchmarks, nombres de modelos, precios) debe verificarse en la fuente oficial, ir en un callout `<Snapshot>` con la fecha y no contener cifras inventadas.
   - Cada lección lleva al menos 2 fuentes reales en el frontmatter, con `lastReviewed` puesto a la fecha real. Nunca inventes URLs, autores ni títulos de papers: si no puedes verificar una referencia, no la pongas.
   - Profundidad: nivel suficiente para superar entrevistas técnicas en empresas de IA (mid/senior), no un resumen superficial.
5. Cada lab debe tener `starter.py`, `solution.py` y `test_lab.py`. La solución debe pasar todos los tests y el starter debe fallarlos; verifícalo con pytest en local y en CI.
6. Haz commits pequeños y descriptivos. No hagas force-push ni reescribas el historial de `main`.

Punto de control obligatorio: al terminar F3, **detente** y dame un resumen con la URL desplegada, lo que funciona, las decisiones tomadas y cualquier problema, para que lo revise antes de que generes el contenido masivo (F4–F7). Cuando te dé el visto bueno, continúa con F4 y en adelante. Haz también una pausa breve con resumen al final de cada fase siguiente.

Al final, el README debe explicar cómo arrancar el proyecto en local en Windows, cómo añadir una lección, un quiz y un lab, y cómo funciona el despliegue.
