# Prompt: sincronizar el progreso por usuario (F8)

Lee primero `docs/PROGRESS.md`, `docs/DECISIONS.md` y `src/lib/progress.ts`. Sigue el mismo flujo de trabajo de las fases anteriores: rama `fase-8-sync`, puerta completa en verde (prettier, eslint, astro check, vitest, validate, build, Playwright, ruff, pytest), CI en verde antes de fusionar a `main` con `--no-ff`, commits con el trailer de coautoría, `docs/PROGRESS.md` actualizado como punto de reanudación y decisiones en `docs/DECISIONS.md`. Ahorra tokens: no narres la ejecución.

## Objetivo

Hoy el progreso (lecciones leídas, notas de quizzes, labs, repaso Leitner y exámenes) vive en `localStorage` (`rma:progress:v1`) y se puede exportar e importar en JSON. Queremos que **cada usuario pueda iniciar sesión y recuperar su progreso en cualquier dispositivo**, sin que el curso deje de funcionar sin cuenta.

Requisitos no negociables:

1. **Local primero.** Sin sesión, todo funciona como ahora. Con sesión, el progreso se sigue guardando primero en local y se sincroniza en segundo plano; sin red, nada se rompe.
2. **Nunca perder progreso.** La sincronización **fusiona**; jamás sobrescribe un lado con el otro.
3. **Opcional y configurable.** Si no están definidas las variables públicas del backend, la función no aparece y el sitio se construye igual.
4. **Sin secretos en el repo.** Solo claves públicas pensadas para el navegador; la seguridad la dan las reglas del servidor.
5. **Privacidad.** Solo se guarda el progreso y lo mínimo para identificar la cuenta. El usuario puede ver qué se guarda, borrar sus datos y cerrar sesión.

## Arquitectura propuesta (verifícala antes de implementar)

El sitio es estático (GitHub Pages), así que hace falta un backend gestionado. Propuesta: **Supabase** (Auth con enlace mágico por correo y, opcionalmente, GitHub; Postgres con Row Level Security). Antes de escribir código, **abre la documentación vigente** de Supabase (cliente JS, Auth con redirecciones en sitios estáticos, RLS, límites del plan gratuito, borrado de cuenta) y comprueba que encaja; si algo no encaja, propón una alternativa (por ejemplo Firebase) con su motivo en `DECISIONS.md` y **pregunta antes de cambiar de proveedor**. Registra versiones y fuentes en `docs/SOURCES.md`.

- Tabla `progress`: `user_id` (clave, referencia al usuario de Auth), `data` (jsonb con el progreso), `schema_version`, `updated_at`. RLS: cada usuario solo puede leer, crear y actualizar **su** fila. Guarda el SQL de la tabla y de las políticas en `supabase/schema.sql`.
- Variables públicas de build: `PUBLIC_SUPABASE_URL` y `PUBLIC_SUPABASE_ANON_KEY` (en GitHub como variables del repositorio para `deploy.yml`; en local, `.env` ignorado por git). Documenta en el README cómo crear el proyecto, aplicar el SQL y configurar las URL de redirección con el prefijo `/RAG_learning_web/`.
- **No puedes crear la cuenta de Supabase.** Implementa y prueba todo con un backend simulado; cuando llegue el momento, **para y pide** al usuario que cree el proyecto y te dé la URL y la clave pública.

## Modelo de datos y fusión (la parte delicada)

La fusión debe ser una **función pura** en `src/lib/sync.ts`: conmutativa, asociativa e idempotente (fusionar A con B da lo mismo que B con A, y fusionar dos veces no cambia nada). Para eso hace falta un **esquema v2** con marcas de tiempo por entrada y una **migración** desde v1 (la v1 sigue leyéndose):

- `lessonsRead`: por lección, `{ read: boolean, updatedAt }`; gana la marca más reciente (así «marcar como no leída» no la resucita la otra copia).
- `quizScores`: `best` = máximo; `last` y `attempts` de la entrada con `updatedAt` más reciente (no sumes intentos: no se sabe si se solapan).
- `labs`: `passed` gana a `started`; el código, el de `updatedAt` más reciente.
- `srs`: por tarjeta, gana la de `reviewedAt` más reciente.
- `exams`: unión sin duplicados (por fecha y resultado).

Prueba la fusión con tests de propiedades (conmutatividad, idempotencia, no perder lecciones leídas ni notas máximas) además de casos concretos, y la migración v1 → v2. La importación de JSON existente debe pasar a usar la misma fusión.

## Sincronización

- Al iniciar sesión y al cargar la página con sesión: descargar la fila remota, fusionar con la local, guardar en local y subir el resultado.
- Tras cada cambio: subir con *debounce* (unos segundos) y al ocultarse la pestaña. Reintentos con retroceso; sin red, se marca como pendiente.
- Concurrencia: dos pestañas o dispositivos a la vez no deben perder datos (fusionar antes de cada subida; si el servidor tiene una versión más nueva, volver a fusionar).
- Mantén `updateProgress` como único punto de escritura; la sincronización escucha el store, no toca los componentes.

## Interfaz

En `/progreso/`: iniciar sesión (correo con enlace mágico), estado de sincronización («sincronizado hace X», «pendiente», «sin conexión»), cerrar sesión (preguntando si se conserva la copia local), «borrar mis datos de la nube» y una nota breve de privacidad (qué se guarda, dónde y cómo borrarlo). Un indicador discreto en la cabecera cuando hay sesión. Accesible (teclado, `aria-live` para el estado, contraste AA en ambos temas: el test de axe debe seguir en verde).

## Pruebas

- Unitarias: fusión (propiedades y casos), migración, cola de sincronización y reintentos con un cliente simulado.
- e2e con el backend **simulado** (`page.route` o un adaptador en memoria): dos «dispositivos» (dos contextos de navegador) que progresan por separado y acaban con el progreso fusionado; sin red no se pierde nada; con la función desactivada (sin variables) la página de progreso funciona como hoy.
- Ningún test de CI llama al Supabase real. Opcional y documentado: un script de prueba contra un proyecto real para verificar las políticas RLS (un usuario no puede leer la fila de otro).

## Entrega

Al terminar: resumen al usuario con qué falta que haga él (crear el proyecto de Supabase, aplicar `supabase/schema.sql`, configurar redirecciones y variables), cómo comprobarlo en producción y los riesgos o decisiones abiertas. No fusiones a `main` con la función activa hasta que el usuario haya configurado el backend y lo hayáis probado juntos; mientras tanto, la función queda desactivada por ausencia de variables.
