/**
 * Motor de sincronización del progreso. No sabe nada de Supabase ni del navegador: recibe un
 * `SyncBackend` y funciones para leer y fusionar el progreso local, así que se prueba entero con
 * un backend en memoria.
 *
 * Reglas: local primero (nada espera a la red), fusionar siempre antes de subir (nunca pisar), y
 * concurrencia optimista (si el servidor cambió mientras tanto, se vuelve a fusionar y se reintenta).
 */
import { atom } from 'nanostores';
import { sameProgress } from './merge';
import type { Progress } from './progress';

export interface RemoteSnapshot {
  data: Progress | null;
  /** Identificador de la versión del servidor (para la concurrencia optimista). */
  version: string | null;
}

export type PushResult = { ok: true; version: string } | { ok: false; conflict: true };

export interface SyncBackend {
  fetch(): Promise<RemoteSnapshot>;
  /** Sube `data` si el servidor sigue en `baseVersion` (`null` = aún no había fila). */
  push(data: Progress, baseVersion: string | null): Promise<PushResult>;
  deleteRemote(): Promise<void>;
}

export type SyncState =
  'disabled' | 'signed-out' | 'idle' | 'pending' | 'syncing' | 'offline' | 'error';

export interface SyncStatus {
  state: SyncState;
  lastSyncedAt: string | null;
  email: string | null;
  error: string | null;
}

export const initialSyncStatus: SyncStatus = {
  state: 'disabled',
  lastSyncedAt: null,
  email: null,
  error: null,
};

export const $sync = atom<SyncStatus>(initialSyncStatus);
export const setSyncStatus = (patch: Partial<SyncStatus>) =>
  $sync.set({ ...$sync.get(), ...patch });

/** Error de red (sin conexión, DNS, CORS...): se reintenta y no se enseña como fallo. */
export class NetworkError extends Error {}

export interface EngineOptions {
  backend: SyncBackend;
  /** Progreso local actual (siempre desde localStorage, la fuente de verdad). */
  getLocal: () => Progress;
  /** Fusiona un progreso remoto con el local actual y lo guarda. */
  applyRemote: (remote: Progress) => void;
  now?: () => Date;
  setTimer?: (fn: () => void, ms: number) => unknown;
  clearTimer?: (id: unknown) => void;
  debounceMs?: number;
  /** Esperas entre reintentos tras un fallo (ms); al agotarse se espera a un nuevo cambio. */
  retryDelaysMs?: number[];
  /** Intentos máximos por sincronización cuando el servidor cambia a mitad de la subida. */
  maxConflicts?: number;
  onStatus?: (patch: Partial<SyncStatus>) => void;
}

export class SyncEngine {
  private timer: unknown = null;
  private running = false;
  private again = false;
  private stopped = false;
  private failures = 0;
  private readonly o: Required<Omit<EngineOptions, 'onStatus'>> & Pick<EngineOptions, 'onStatus'>;

  constructor(options: EngineOptions) {
    this.o = {
      now: () => new Date(),
      setTimer: (fn, ms) => setTimeout(fn, ms),
      clearTimer: (id) => clearTimeout(id as ReturnType<typeof setTimeout>),
      debounceMs: 3000,
      retryDelaysMs: [2000, 8000, 30000, 120000],
      maxConflicts: 5,
      ...options,
    };
  }

  private status(patch: Partial<SyncStatus>) {
    this.o.onStatus?.(patch);
  }

  private clear() {
    if (this.timer !== null) this.o.clearTimer(this.timer);
    this.timer = null;
  }

  private schedule(ms: number) {
    this.clear();
    this.timer = this.o.setTimer(() => {
      this.timer = null;
      void this.syncNow();
    }, ms);
  }

  /** Hay un cambio local sin subir: se sube pasado el debounce. */
  notifyLocalChange(): void {
    if (this.stopped) return;
    this.status({ state: 'pending' });
    this.schedule(this.o.debounceMs);
  }

  /** Sube ya lo pendiente (por ejemplo, al ocultarse la pestaña). */
  flush(): void {
    if (this.stopped || this.timer === null) return;
    this.clear();
    void this.syncNow();
  }

  stop(): void {
    this.stopped = true;
    this.clear();
  }

  /** Una sincronización completa: bajar, fusionar, guardar y subir. Nunca lanza. */
  async syncNow(): Promise<void> {
    if (this.stopped) return;
    if (this.running) {
      this.again = true;
      return;
    }
    this.running = true;
    this.clear();
    this.status({ state: 'syncing', error: null });
    try {
      await this.cycle();
      this.failures = 0;
      this.status({ state: 'idle', lastSyncedAt: this.o.now().toISOString(), error: null });
    } catch (e) {
      this.handleFailure(e);
    } finally {
      this.running = false;
      if (this.again && !this.stopped) {
        this.again = false;
        void this.syncNow();
      }
    }
  }

  private async cycle(): Promise<void> {
    for (let attempt = 0; attempt < this.o.maxConflicts; attempt++) {
      const remote = await this.o.backend.fetch();
      // Se fusiona contra lo local DE AHORA: un cambio hecho mientras se esperaba a la red no se pisa.
      if (remote.data) this.o.applyRemote(remote.data);
      const local = this.o.getLocal();
      if (remote.data && sameProgress(local, remote.data)) return;
      const result = await this.o.backend.push(local, remote.version);
      if (result.ok) return;
    }
    throw new Error('El servidor cambia sin parar; se reintentará más tarde.');
  }

  private handleFailure(e: unknown): void {
    const offline =
      e instanceof NetworkError || (typeof navigator !== 'undefined' && navigator.onLine === false);
    this.status({
      state: offline ? 'offline' : 'error',
      error: offline ? null : e instanceof Error ? e.message : 'Error desconocido',
    });
    const delay = this.o.retryDelaysMs[this.failures];
    this.failures++;
    if (delay !== undefined && !this.stopped) this.schedule(delay);
  }

  /** Borra la copia de la nube (no toca el progreso local). */
  async deleteRemote(): Promise<void> {
    this.clear();
    await this.o.backend.deleteRemote();
    this.status({ lastSyncedAt: null });
  }
}
