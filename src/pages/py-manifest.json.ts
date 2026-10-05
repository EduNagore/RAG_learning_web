import { readdirSync } from 'node:fs';
import { join } from 'node:path';
import type { APIRoute } from 'astro';

// Lista los archivos de `public/py/ragkit` y `public/data/nimbus` para que el worker de Pyodide
// los descargue y los monte en su sistema de archivos. Se genera en build: así, añadir un
// módulo a ragkit no obliga a mantener una lista a mano.
// Se resuelve desde la raíz del proyecto: durante el build `import.meta.url` apunta al bundle.
const list = (dir: string, ext: string) =>
  readdirSync(join(process.cwd(), 'public', dir))
    .filter((f) => f.endsWith(ext))
    .sort();

export const GET: APIRoute = () =>
  new Response(
    JSON.stringify({ ragkit: list('py/ragkit', '.py'), data: list('data/nimbus', '.json') }),
    { headers: { 'Content-Type': 'application/json' } },
  );
