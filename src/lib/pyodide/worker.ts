/**
 * Web Worker que ejecuta Python con Pyodide. Se carga solo al abrir un laboratorio.
 *
 * Protocolo (todos los mensajes llevan `id`):
 *   → { type: 'init', base, packages }   carga Pyodide, paquetes, ragkit y los datos
 *   → { type: 'run', code }              ejecuta el código del alumno (botón «Ejecutar»)
 *   → { type: 'check', code, tests }     ejecuta los tests sobre el código (botón «Comprobar»)
 *   ← { id, type: 'status', text }       progreso de la inicialización
 *   ← { id, type: 'result', value }      resultado (el JSON que devuelve ragkit.labrunner)
 *   ← { id, type: 'error', message }     fallo de infraestructura (no del código del alumno)
 */

// Versión fijada: debe coincidir con la que usa `pyproject.toml` para los tests de CI.
const PYODIDE_VERSION = '314.0.7';
const PYODIDE_BASE = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

interface PyodideApi {
  loadPackage(names: string[]): Promise<unknown>;
  runPython(code: string): unknown;
  globals: { set(name: string, value: unknown): void };
  FS: {
    mkdirTree(path: string): void;
    writeFile(path: string, data: string): void;
  };
}

type WorkerRequest =
  | { id: number; type: 'init'; base: string; packages: string[] }
  | { id: number; type: 'run'; code: string }
  | { id: number; type: 'check'; code: string; tests: string };

// `self` se tipa a mano para no mezclar la librería de DOM con la de WebWorker.
const ctx = self as unknown as {
  postMessage(message: unknown): void;
  onmessage: ((event: MessageEvent<WorkerRequest>) => void) | null;
};

let pyodide: PyodideApi | null = null;
let initPromise: Promise<void> | null = null;

async function fetchText(url: string): Promise<string> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`No se pudo descargar ${url} (${res.status})`);
  return res.text();
}

async function init(id: number, base: string, packages: string[]): Promise<void> {
  const status = (text: string) => ctx.postMessage({ id, type: 'status', text });

  status('Descargando el intérprete de Python…');
  // La URL es externa y se importa en tiempo de ejecución: el bundler no debe resolverla.
  const mod = await import(/* @vite-ignore */ `${PYODIDE_BASE}pyodide.mjs`);
  const py: PyodideApi = await mod.loadPyodide({ indexURL: PYODIDE_BASE });

  status('Cargando paquetes de Python…');
  await py.loadPackage(['numpy', ...packages.filter((p) => p !== 'numpy')]);

  status('Preparando ragkit y los datos de Nimbus Logística…');
  const manifest: { ragkit: string[]; data: string[] } = await (
    await fetch(`${base}py-manifest.json`)
  ).json();
  py.FS.mkdirTree('/home/pyodide/py/ragkit');
  py.FS.mkdirTree('/home/pyodide/data/nimbus');
  await Promise.all([
    ...manifest.ragkit.map(async (f) =>
      py.FS.writeFile(`/home/pyodide/py/ragkit/${f}`, await fetchText(`${base}py/ragkit/${f}`)),
    ),
    ...manifest.data.map(async (f) =>
      py.FS.writeFile(`/home/pyodide/data/nimbus/${f}`, await fetchText(`${base}data/nimbus/${f}`)),
    ),
  ]);
  py.runPython("import sys\nsys.path.insert(0, '/home/pyodide/py')");
  pyodide = py;
}

function runJson(py: PyodideApi, vars: Record<string, string>, expression: string): unknown {
  for (const [name, value] of Object.entries(vars)) py.globals.set(name, value);
  const json = py.runPython(`import json\nfrom ragkit import labrunner\njson.dumps(${expression})`);
  return JSON.parse(String(json));
}

ctx.onmessage = async (event) => {
  const msg = event.data;
  try {
    if (msg.type === 'init') {
      initPromise ??= init(msg.id, msg.base, msg.packages);
      await initPromise;
      ctx.postMessage({ id: msg.id, type: 'result', value: true });
      return;
    }
    if (!pyodide) throw new Error('Python todavía no está inicializado.');
    const value =
      msg.type === 'run'
        ? runJson(pyodide, { _src: msg.code }, 'labrunner.run_code(_src)')
        : runJson(
            pyodide,
            { _src: msg.code, _tests: msg.tests },
            'labrunner.run_lab(_src, _tests)',
          );
    ctx.postMessage({ id: msg.id, type: 'result', value });
  } catch (e) {
    ctx.postMessage({
      id: msg.id,
      type: 'error',
      message: e instanceof Error ? e.message : String(e),
    });
  }
};
