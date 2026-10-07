import { describe, expect, it } from 'vitest';
import { mergeProgress } from '../../src/lib/merge';
import {
  emptyProgress,
  withLessonRead,
  withQuizOutcome,
  type Progress,
} from '../../src/lib/progress';
import {
  NetworkError,
  SyncEngine,
  type PushResult,
  type RemoteSnapshot,
  type SyncBackend,
  type SyncStatus,
} from '../../src/lib/sync';

const at = (n: number) => new Date(Date.UTC(2026, 9, 1, 0, 0, n));

/** Servidor en memoria con control de versiones y fallos inyectables. */
class FakeServer {
  data: Progress | null = null;
  revision = 0;
  pushes = 0;
  fetches = 0;
  failNext: Error[] = [];
  /** Hook que se ejecuta justo antes de aceptar una subida (para simular otro dispositivo). */
  beforePush: (() => void) | null = null;

  backend(): SyncBackend {
    return {
      fetch: async (): Promise<RemoteSnapshot> => {
        this.fetches++;
        const err = this.failNext.shift();
        if (err) throw err;
        return {
          data: this.data ? structuredClone(this.data) : null,
          version: this.data ? String(this.revision) : null,
        };
      },
      push: async (data, base): Promise<PushResult> => {
        this.pushes++;
        this.beforePush?.();
        this.beforePush = null;
        const current = this.data ? String(this.revision) : null;
        if (current !== base) return { ok: false, conflict: true };
        this.data = structuredClone(data);
        this.revision++;
        return { ok: true, version: String(this.revision) };
      },
      deleteRemote: async () => {
        this.data = null;
      },
    };
  }
}

function setup(server: FakeServer, initial: Progress = emptyProgress()) {
  let local = initial;
  const timers: { fn: () => void; ms: number }[] = [];
  const statuses: Partial<SyncStatus>[] = [];
  const engine = new SyncEngine({
    backend: server.backend(),
    getLocal: () => local,
    applyRemote: (remote) => {
      local = mergeProgress(local, remote);
    },
    now: () => at(100),
    setTimer: (fn, ms) => {
      timers.push({ fn, ms });
      return timers.length - 1;
    },
    clearTimer: (id) => {
      if (typeof id === 'number') timers[id] = { fn: () => {}, ms: -1 };
    },
    onStatus: (patch) => statuses.push(patch),
  });
  return {
    engine,
    timers,
    statuses,
    get local() {
      return local;
    },
    set local(p: Progress) {
      local = p;
    },
  };
}

describe('SyncEngine', () => {
  it('la primera sincronización sube el progreso local si no había nada en el servidor', async () => {
    const server = new FakeServer();
    const t = setup(server, withLessonRead(emptyProgress(), 'a', at(1)));
    await t.engine.syncNow();
    expect(Object.keys(server.data!.lessonsRead)).toEqual(['a']);
    expect(t.statuses.at(-1)).toMatchObject({ state: 'idle', lastSyncedAt: at(100).toISOString() });
  });

  it('un dispositivo nuevo recibe el progreso del servidor y no lo vacía', async () => {
    const server = new FakeServer();
    server.data = withLessonRead(emptyProgress(), 'a', at(1));
    server.revision = 1;
    const t = setup(server);
    await t.engine.syncNow();
    expect(Object.keys(t.local.lessonsRead)).toEqual(['a']);
    expect(server.pushes).toBe(0); // ya era idéntico: no hace falta subir
  });

  it('fusiona lo de los dos lados y sube el resultado', async () => {
    const server = new FakeServer();
    server.data = withLessonRead(emptyProgress(), 'remota', at(1));
    server.revision = 1;
    const t = setup(server, withLessonRead(emptyProgress(), 'local', at(2)));
    await t.engine.syncNow();
    expect(Object.keys(t.local.lessonsRead).sort()).toEqual(['local', 'remota']);
    expect(Object.keys(server.data!.lessonsRead).sort()).toEqual(['local', 'remota']);
  });

  it('si otro dispositivo sube a mitad, vuelve a fusionar y no pierde ninguno de los dos', async () => {
    const server = new FakeServer();
    const t = setup(server, withLessonRead(emptyProgress(), 'portatil', at(1)));
    server.beforePush = () => {
      server.data = withQuizOutcome(
        emptyProgress(),
        { quizId: 'q', results: [{ id: '1', correct: true }] },
        at(2),
      );
      server.revision++;
    };
    await t.engine.syncNow();
    expect(server.pushes).toBe(2); // el primero chocó; el segundo, ya fusionado, entró
    expect(Object.keys(server.data!.lessonsRead)).toEqual(['portatil']);
    expect(server.data!.quizScores.q.best).toBe(100);
    expect(t.local.quizScores.q.best).toBe(100);
  });

  it('un cambio local hecho mientras se esperaba a la red no se pisa', async () => {
    const server = new FakeServer();
    server.data = withLessonRead(emptyProgress(), 'remota', at(1));
    server.revision = 1;
    const t = setup(server);
    const original = server.backend().fetch;
    const backend = server.backend();
    backend.fetch = async () => {
      const snapshot = await original();
      t.local = withLessonRead(t.local, 'mientras-tanto', at(5)); // el usuario sigue estudiando
      return snapshot;
    };
    const engine = new SyncEngine({
      backend,
      getLocal: () => t.local,
      applyRemote: (r) => (t.local = mergeProgress(t.local, r)),
    });
    await engine.syncNow();
    expect(Object.keys(t.local.lessonsRead).sort()).toEqual(['mientras-tanto', 'remota']);
    expect(Object.keys(server.data!.lessonsRead).sort()).toEqual(['mientras-tanto', 'remota']);
  });

  it('sin red marca «sin conexión», conserva lo local y reintenta con retroceso', async () => {
    const server = new FakeServer();
    server.failNext = [new NetworkError('sin red'), new NetworkError('sin red')];
    const t = setup(server, withLessonRead(emptyProgress(), 'a', at(1)));
    await t.engine.syncNow();
    expect(t.statuses.at(-1)).toMatchObject({ state: 'offline', error: null });
    expect(Object.keys(t.local.lessonsRead)).toEqual(['a']);
    expect(t.timers.at(-1)!.ms).toBe(2000);
    t.timers.at(-1)!.fn(); // segundo intento: falla otra vez
    await Promise.resolve();
    await new Promise((r) => setTimeout(r, 0));
    expect(t.timers.at(-1)!.ms).toBe(8000);
    t.timers.at(-1)!.fn(); // tercero: ya hay red
    await new Promise((r) => setTimeout(r, 0));
    expect(Object.keys(server.data!.lessonsRead)).toEqual(['a']);
    expect(t.statuses.at(-1)).toMatchObject({ state: 'idle' });
  });

  it('un error del servidor se muestra como error con su mensaje', async () => {
    const server = new FakeServer();
    server.failNext = [new Error('permission denied')];
    const t = setup(server);
    await t.engine.syncNow();
    expect(t.statuses.at(-1)).toMatchObject({ state: 'error', error: 'permission denied' });
  });

  it('los cambios locales seguidos se agrupan con un solo temporizador (debounce)', async () => {
    const server = new FakeServer();
    const t = setup(server, withLessonRead(emptyProgress(), 'a', at(1)));
    t.engine.notifyLocalChange();
    t.engine.notifyLocalChange();
    t.engine.notifyLocalChange();
    expect(t.timers.filter((x) => x.ms === 3000)).toHaveLength(1); // solo queda el último
    expect(t.timers.filter((x) => x.ms === -1)).toHaveLength(2); // los anteriores se cancelaron
    expect(t.statuses.at(-1)).toMatchObject({ state: 'pending' });
    t.timers.at(-1)!.fn();
    await new Promise((r) => setTimeout(r, 0));
    expect(server.pushes).toBe(1);
  });

  it('flush sube de inmediato lo pendiente', async () => {
    const server = new FakeServer();
    const t = setup(server, withLessonRead(emptyProgress(), 'a', at(1)));
    t.engine.notifyLocalChange();
    t.engine.flush();
    await new Promise((r) => setTimeout(r, 0));
    expect(server.pushes).toBe(1);
  });

  it('una sincronización pedida durante otra se encadena y no se pierde', async () => {
    const server = new FakeServer();
    const t = setup(server, withLessonRead(emptyProgress(), 'a', at(1)));
    const first = t.engine.syncNow();
    t.local = withLessonRead(t.local, 'b', at(2));
    void t.engine.syncNow();
    await first;
    await new Promise((r) => setTimeout(r, 0));
    expect(Object.keys(server.data!.lessonsRead).sort()).toEqual(['a', 'b']);
  });

  it('tras stop() no sincroniza más', async () => {
    const server = new FakeServer();
    const t = setup(server, withLessonRead(emptyProgress(), 'a', at(1)));
    t.engine.stop();
    await t.engine.syncNow();
    t.engine.notifyLocalChange();
    expect(server.fetches).toBe(0);
  });

  it('si el servidor cambia sin parar, desiste con un error y no entra en bucle', async () => {
    const server = new FakeServer();
    const backend = server.backend();
    const t = setup(server, withLessonRead(emptyProgress(), 'a', at(1)));
    backend.push = async () => ({ ok: false, conflict: true });
    const engine = new SyncEngine({
      backend,
      getLocal: () => t.local,
      applyRemote: () => {},
      maxConflicts: 3,
      setTimer: () => 0,
      onStatus: (p) => t.statuses.push(p),
    });
    await engine.syncNow();
    expect(t.statuses.at(-1)).toMatchObject({ state: 'error' });
  });

  it('deleteRemote borra la copia de la nube y no toca lo local', async () => {
    const server = new FakeServer();
    const t = setup(server, withLessonRead(emptyProgress(), 'a', at(1)));
    await t.engine.syncNow();
    await t.engine.deleteRemote();
    expect(server.data).toBeNull();
    expect(Object.keys(t.local.lessonsRead)).toEqual(['a']);
  });
});
