/** Cliente del worker de Pyodide: arranque perezoso, temporizador y recuperación de bucles infinitos. */

export interface RunReport {
  stdout: string;
  error: string | null;
}

export interface TestResult {
  name: string;
  title: string;
  hidden: boolean;
  passed: boolean;
  message: string;
  stdout: string;
}

export interface CheckReport {
  load_error: string | null;
  results: TestResult[];
}

/** El código del alumno tardó demasiado: se terminó el worker. */
export class RunTimeoutError extends Error {
  constructor(seconds: number) {
    super(`Tu código tardó más de ${seconds} s y se detuvo (¿hay un bucle infinito?).`);
    this.name = 'RunTimeoutError';
  }
}

const RUN_TIMEOUT_MS = 10_000;
const INIT_TIMEOUT_MS = 120_000; // incluye descargar Pyodide la primera vez

interface Pending {
  resolve: (value: unknown) => void;
  reject: (reason: Error) => void;
  onStatus?: (text: string) => void;
  timer: ReturnType<typeof setTimeout>;
}

export class PyRunner {
  private worker: Worker | null = null;
  private ready: Promise<void> | null = null;
  private nextId = 1;
  private pending = new Map<number, Pending>();

  /**
   * @param base ruta base del sitio con barra final (p. ej. `/RAG_learning_web/`), de donde el
   *   worker descarga ragkit y los datos.
   * @param packages paquetes de Pyodide que necesita el laboratorio además de numpy.
   */
  constructor(
    private readonly base: string,
    private readonly packages: string[] = [],
  ) {}

  private spawn(): Worker {
    const worker = new Worker(new URL('./worker.ts', import.meta.url), { type: 'module' });
    worker.onmessage = (event: MessageEvent) => {
      const { id, type } = event.data as { id: number; type: string };
      const entry = this.pending.get(id);
      if (!entry) return;
      if (type === 'status') return entry.onStatus?.(event.data.text);
      clearTimeout(entry.timer);
      this.pending.delete(id);
      if (type === 'error') entry.reject(new Error(event.data.message));
      else entry.resolve(event.data.value);
    };
    worker.onerror = (event) =>
      this.fail(new Error(event.message || 'Error en el worker de Python'));
    return worker;
  }

  private call<T>(
    message: Record<string, unknown>,
    timeoutMs: number,
    timeoutError: () => Error,
    onStatus?: (text: string) => void,
  ): Promise<T> {
    const worker = this.worker;
    if (!worker) return Promise.reject(new Error('El worker de Python no está iniciado.'));
    const id = this.nextId++;
    return new Promise<T>((resolve, reject) => {
      const timer = setTimeout(() => {
        // Un bucle infinito no se puede interrumpir desde dentro: se mata el worker entero.
        this.fail(timeoutError());
      }, timeoutMs);
      this.pending.set(id, { resolve: resolve as (v: unknown) => void, reject, onStatus, timer });
      worker.postMessage({ ...message, id });
    });
  }

  /** Termina el worker y rechaza todo lo pendiente. La siguiente llamada vuelve a arrancarlo. */
  private fail(error: Error): void {
    this.worker?.terminate();
    this.worker = null;
    this.ready = null;
    for (const entry of this.pending.values()) {
      clearTimeout(entry.timer);
      entry.reject(error);
    }
    this.pending.clear();
  }

  /** Arranca Pyodide si hace falta (la primera vez descarga el intérprete). */
  ensureReady(onStatus?: (text: string) => void): Promise<void> {
    if (this.ready) return this.ready;
    this.worker = this.spawn();
    const ready = this.call<void>(
      { type: 'init', base: this.base, packages: this.packages },
      INIT_TIMEOUT_MS,
      () =>
        new Error('Python tardó demasiado en cargar. Comprueba tu conexión e inténtalo de nuevo.'),
      onStatus,
    ).then(
      () => undefined,
      (e: Error) => {
        this.fail(e);
        throw e;
      },
    );
    this.ready = ready;
    return ready;
  }

  async run(code: string, onStatus?: (text: string) => void): Promise<RunReport> {
    await this.ensureReady(onStatus);
    return this.call<RunReport>(
      { type: 'run', code },
      RUN_TIMEOUT_MS,
      () => new RunTimeoutError(RUN_TIMEOUT_MS / 1000),
    );
  }

  async check(
    code: string,
    tests: string,
    onStatus?: (text: string) => void,
  ): Promise<CheckReport> {
    await this.ensureReady(onStatus);
    return this.call<CheckReport>(
      { type: 'check', code, tests },
      RUN_TIMEOUT_MS,
      () => new RunTimeoutError(RUN_TIMEOUT_MS / 1000),
    );
  }

  dispose(): void {
    this.fail(new Error('Ejecución cancelada.'));
  }
}
