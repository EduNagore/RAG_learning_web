import { describe, expect, it } from 'vitest';
import {
  STORAGE_KEY,
  emptyProgress,
  exportProgress,
  importProgress,
  loadProgress,
  moduleCompletion,
  parseProgress,
  saveProgress,
  withLessonRead,
  withLessonUnread,
} from '../../src/lib/progress';

/** Storage en memoria; `broken` simula modo privado / almacenamiento bloqueado. */
function fakeStorage(initial: Record<string, string> = {}, broken = false): Storage {
  const data = new Map(Object.entries(initial));
  return {
    get length() {
      return data.size;
    },
    clear: () => data.clear(),
    getItem: (k) => {
      if (broken) throw new Error('bloqueado');
      return data.get(k) ?? null;
    },
    key: (i) => [...data.keys()][i] ?? null,
    removeItem: (k) => void data.delete(k),
    setItem: (k, v) => {
      if (broken) throw new Error('cuota');
      data.set(k, v);
    },
  };
}

describe('parseProgress', () => {
  it('devuelve progreso vacío con null, vacío o JSON roto', () => {
    expect(parseProgress(null)).toEqual(emptyProgress());
    expect(parseProgress('')).toEqual(emptyProgress());
    expect(parseProgress('{no es json')).toEqual(emptyProgress());
    expect(parseProgress('[1,2]')).toEqual(emptyProgress());
  });

  it('aprovecha las claves válidas y descarta las de tipo incorrecto', () => {
    const p = parseProgress(
      JSON.stringify({ lessonsRead: { a: '2026-01-01T00:00:00.000Z' }, labs: 'roto', exams: {} }),
    );
    expect(p.lessonsRead).toEqual({ a: '2026-01-01T00:00:00.000Z' });
    expect(p.labs).toEqual({});
    expect(p.exams).toEqual([]);
  });
});

describe('persistencia', () => {
  it('guarda y recarga', () => {
    const storage = fakeStorage();
    const p = withLessonRead(emptyProgress(), 'm00/01', new Date('2026-10-05T10:00:00Z'));
    saveProgress(p, storage);
    expect(JSON.parse(storage.getItem(STORAGE_KEY)!).lessonsRead['m00/01']).toBe(
      '2026-10-05T10:00:00.000Z',
    );
    expect(loadProgress(storage)).toEqual(p);
  });

  it('no lanza si el almacenamiento está bloqueado o no existe', () => {
    const broken = fakeStorage({}, true);
    expect(() => saveProgress(emptyProgress(), broken)).not.toThrow();
    expect(loadProgress(broken)).toEqual(emptyProgress());
    expect(loadProgress(null)).toEqual(emptyProgress());
  });
});

describe('lecciones y módulos', () => {
  it('marca y desmarca sin mutar el original', () => {
    const base = emptyProgress();
    const read = withLessonRead(base, 'x');
    expect(base.lessonsRead).toEqual({});
    expect('x' in read.lessonsRead).toBe(true);
    expect(withLessonUnread(read, 'x').lessonsRead).toEqual({});
    expect(withLessonUnread(read, 'no-existe').lessonsRead).toEqual(read.lessonsRead);
  });

  it('calcula el avance de un módulo', () => {
    const p = withLessonRead(withLessonRead(emptyProgress(), 'a'), 'c');
    expect(moduleCompletion(p, ['a', 'b', 'c'])).toEqual({ done: 2, total: 3 });
    expect(moduleCompletion(p, [])).toEqual({ done: 0, total: 0 });
  });
});

describe('exportar / importar', () => {
  it('hace ida y vuelta', () => {
    const p = withLessonRead(emptyProgress(), 'a', new Date('2026-01-01T00:00:00Z'));
    expect(importProgress(exportProgress(p))).toEqual(p);
  });

  it('rechaza archivos que no son un progreso', () => {
    expect(() => importProgress('no json')).toThrow(/JSON válido/);
    expect(() => importProgress('{"foo": 1}')).toThrow(/copia de seguridad/);
    expect(() => importProgress('[]')).toThrow(/copia de seguridad/);
  });
});

describe('updateProgress', () => {
  it('parte de lo guardado y no pisa el progreso con un store vacío', async () => {
    const { vi } = await import('vitest');
    const storage = fakeStorage({
      [STORAGE_KEY]: JSON.stringify(
        withLessonRead(emptyProgress(), 'ya-leida', new Date('2026-01-01T00:00:00Z')),
      ),
    });
    vi.stubGlobal('localStorage', storage);
    try {
      // Módulo importado de nuevo: su store en memoria empieza vacío (isla sin hidratar).
      vi.resetModules();
      const mod = await import('../../src/lib/progress');
      mod.markLessonRead('nueva');
      const saved = JSON.parse(storage.getItem(STORAGE_KEY)!);
      expect(Object.keys(saved.lessonsRead).sort()).toEqual(['nueva', 'ya-leida']);
    } finally {
      vi.unstubAllGlobals();
    }
  });
});

describe('laboratorios', () => {
  const T = new Date('2026-10-05T10:00:00Z');

  it('guardar código crea el laboratorio como "started"', async () => {
    const { withLabCode } = await import('../../src/lib/progress');
    const p = withLabCode(emptyProgress(), 'lab-1', 'print(1)', T);
    expect(p.labs['lab-1']).toEqual({
      status: 'started',
      code: 'print(1)',
      updatedAt: T.toISOString(),
    });
  });

  it('un laboratorio superado no vuelve a "started" al seguir editando', async () => {
    const { withLabCode, withLabPassed } = await import('../../src/lib/progress');
    let p = withLabPassed(emptyProgress(), 'lab-1', 'solución', T);
    expect(p.labs['lab-1'].status).toBe('passed');
    p = withLabCode(p, 'lab-1', 'otra cosa', new Date(T.getTime() + 1000));
    expect(p.labs['lab-1']).toMatchObject({ status: 'passed', code: 'otra cosa' });
  });

  it('no modifica el progreso original', async () => {
    const { withLabCode } = await import('../../src/lib/progress');
    const base = emptyProgress();
    withLabCode(base, 'lab-1', 'x', T);
    expect(base.labs).toEqual({});
  });
});
