import { describe, expect, it } from 'vitest';
import { mergeProgress, restampAfter, sameProgress } from '../../src/lib/merge';
import {
  SCHEMA_VERSION,
  emptyProgress,
  parseProgress,
  withExam,
  withLabCode,
  withLabPassed,
  withLessonRead,
  withLessonUnread,
  withQuizOutcome,
  withReview,
  type Progress,
} from '../../src/lib/progress';

const at = (n: number) => new Date(Date.UTC(2026, 9, 1, 0, 0, n));
const correct = (id: string) => ({ id, correct: true });
const wrong = (id: string) => ({ id, correct: false });

// Generador pseudoaleatorio con semilla (xorshift) para pruebas de propiedades reproducibles.
function rng(seed: number) {
  let s = seed || 1;
  return () => {
    s ^= s << 13;
    s ^= s >>> 17;
    s ^= s << 5;
    return (s >>> 0) / 4294967296;
  };
}

function randomProgress(seed: number, withReset = false): Progress {
  const r = rng(seed);
  const int = (n: number) => Math.floor(r() * n);
  let p = emptyProgress();
  for (let i = 0; i < 14; i++) {
    const when = at(int(60));
    const lesson = `m0/${int(5)}`;
    switch (int(7)) {
      case 0:
        p = withLessonRead(p, lesson, when);
        break;
      case 1:
        p = withLessonUnread(p, lesson, when);
        break;
      case 2:
        p = withQuizOutcome(
          p,
          { quizId: `q${int(3)}`, results: [correct('a'), int(2) ? correct('b') : wrong('b')] },
          when,
        );
        break;
      case 3:
        p = withLabCode(p, `lab${int(3)}`, `codigo-${int(4)}`, when);
        break;
      case 4:
        p = withLabPassed(p, `lab${int(3)}`, `codigo-${int(4)}`, when);
        break;
      case 5:
        p = withReview(p, [int(2) ? correct(`p${int(4)}`) : wrong(`p${int(4)}`)], when);
        break;
      default:
        p = withExam(p, { date: when.toISOString(), score: int(10), total: 10, byModule: {} });
    }
  }
  if (withReset && int(3) === 0) p = { ...p, resetAt: at(30).toISOString() };
  return p;
}

describe('esquema', () => {
  it('la versión de merge.ts coincide con la del esquema', () => {
    expect(mergeProgress(emptyProgress(), emptyProgress()).version).toBe(SCHEMA_VERSION);
  });

  it('migra la v1 (sin unread ni marcas de tiempo) a la v2 sin perder nada', () => {
    const v1 = JSON.stringify({
      version: 1,
      lessonsRead: { 'm00/01': '2026-10-01T10:00:00.000Z' },
      quizScores: { 'm00/01': { best: 90, last: 80, attempts: 2 } },
      labs: { l1: { status: 'passed', code: 'x', updatedAt: '2026-10-02T00:00:00.000Z' } },
      srs: { q1: { box: 2, due: '2026-10-03T00:00:00.000Z' } },
      exams: [{ date: '2026-10-04T00:00:00.000Z', score: 5, total: 10, byModule: {} }],
    });
    const p = parseProgress(v1);
    expect(p.version).toBe(2);
    expect(p.unread).toEqual({});
    expect(p.quizScores['m00/01'].best).toBe(90);
    expect(p.exams).toHaveLength(1);
    // Y una copia de la v1 se puede fusionar con una v2 sin perder lo de ninguna.
    const v2 = withLessonRead(emptyProgress(), 'm00/02', at(5));
    const merged = mergeProgress(p, v2);
    expect(Object.keys(merged.lessonsRead).sort()).toEqual(['m00/01', 'm00/02']);
    expect(merged.quizScores['m00/01'].best).toBe(90);
  });
});

describe('mergeProgress: casos concretos', () => {
  it('une lecciones leídas de dos dispositivos', () => {
    const a = withLessonRead(emptyProgress(), 'a', at(1));
    const b = withLessonRead(emptyProgress(), 'b', at(2));
    expect(Object.keys(mergeProgress(a, b).lessonsRead).sort()).toEqual(['a', 'b']);
  });

  it('«no leída» posterior gana a una lectura antigua; una lectura posterior la recupera', () => {
    const leida = withLessonRead(emptyProgress(), 'a', at(1));
    const desmarcada = withLessonUnread(leida, 'a', at(5));
    expect(mergeProgress(leida, desmarcada).lessonsRead).toEqual({});
    expect(mergeProgress(desmarcada, leida).lessonsRead).toEqual({});
    const releida = withLessonRead(desmarcada, 'a', at(9));
    expect(Object.keys(mergeProgress(desmarcada, releida).lessonsRead)).toEqual(['a']);
  });

  it('la mejor nota es el máximo y el último intento es el más reciente', () => {
    const a = withQuizOutcome(
      emptyProgress(),
      { quizId: 'q', results: [correct('1'), correct('2')] },
      at(1),
    );
    const b = withQuizOutcome(
      emptyProgress(),
      { quizId: 'q', results: [correct('1'), wrong('2')] },
      at(9),
    );
    const merged = mergeProgress(a, b).quizScores.q;
    expect(merged.best).toBe(100);
    expect(merged.last).toBe(50);
    expect(merged.updatedAt).toBe(at(9).toISOString());
  });

  it('un lab superado no vuelve a «started»; el código es el más reciente', () => {
    const aprobado = withLabPassed(emptyProgress(), 'l', 'solucion', at(1));
    const trabajando = withLabCode(emptyProgress(), 'l', 'borrador nuevo', at(9));
    const merged = mergeProgress(aprobado, trabajando).labs.l;
    expect(merged.status).toBe('passed');
    expect(merged.code).toBe('borrador nuevo');
  });

  it('de cada tarjeta de repaso gana la respuesta más reciente', () => {
    const a = withReview(emptyProgress(), [wrong('q')], at(1));
    const b = withReview(withReview(a, [correct('q')], at(2)), [correct('q')], at(3));
    expect(mergeProgress(a, b).srs.q.box).toBe(3);
    expect(mergeProgress(b, a).srs.q.box).toBe(3);
  });

  it('los exámenes se unen sin duplicados', () => {
    const e = { date: at(1).toISOString(), score: 8, total: 10, byModule: {} };
    const a = withExam(emptyProgress(), e);
    const b = withExam(withExam(emptyProgress(), e), { ...e, date: at(2).toISOString() });
    expect(mergeProgress(a, b).exams).toHaveLength(2);
  });

  it('un reinicio posterior no se deshace con una copia antigua, pero lo nuevo sí se conserva', () => {
    const antigua = withLessonRead(
      withQuizOutcome(emptyProgress(), { quizId: 'q', results: [correct('1')] }, at(1)),
      'a',
      at(2),
    );
    const reiniciada = { ...emptyProgress(), resetAt: at(10).toISOString() };
    const despues = withLessonRead(reiniciada, 'b', at(20));
    const merged = mergeProgress(mergeProgress(antigua, despues), antigua);
    expect(Object.keys(merged.lessonsRead)).toEqual(['b']);
    expect(merged.quizScores).toEqual({});
    expect(merged.resetAt).toBe(at(10).toISOString());
  });

  it('las copias con datos de la v1 (sin marcas de tiempo) se descartan tras un reinicio', () => {
    const v1 = parseProgress(JSON.stringify({ lessonsRead: { a: '2026-09-01T00:00:00.000Z' } }));
    const reiniciada = { ...emptyProgress(), resetAt: at(1).toISOString() };
    expect(mergeProgress(v1, reiniciada).lessonsRead).toEqual({});
  });
});

describe('mergeProgress: propiedades (50 casos con semilla)', () => {
  const seeds = Array.from({ length: 50 }, (_, i) => i * 7919 + 13);

  it('es conmutativa', () => {
    for (const s of seeds) {
      const a = randomProgress(s, true);
      const b = randomProgress(s + 1, true);
      expect(mergeProgress(a, b)).toEqual(mergeProgress(b, a));
    }
  });

  it('es idempotente y fusionar de nuevo no cambia nada', () => {
    for (const s of seeds) {
      const a = randomProgress(s, true);
      const b = randomProgress(s + 1, true);
      const m = mergeProgress(a, b);
      expect(mergeProgress(m, m)).toEqual(m);
      expect(mergeProgress(m, a)).toEqual(m);
      expect(mergeProgress(m, b)).toEqual(m);
      expect(sameProgress(mergeProgress(a, a), a)).toBe(true);
    }
  });

  it('es asociativa (sin reinicios en medio)', () => {
    for (const s of seeds) {
      const a = randomProgress(s);
      const b = randomProgress(s + 1);
      const c = randomProgress(s + 2);
      expect(mergeProgress(mergeProgress(a, b), c)).toEqual(mergeProgress(a, mergeProgress(b, c)));
    }
  });

  it('nunca pierde una lección leída ni una nota máxima (sin reinicios ni desmarcados)', () => {
    for (const s of seeds) {
      const a = randomProgress(s);
      const b = randomProgress(s + 1);
      const m = mergeProgress(a, b);
      for (const side of [a, b]) {
        for (const [id, readAt] of Object.entries(side.lessonsRead)) {
          const dead = (m.unread[id] ?? '') >= readAt;
          if (!dead) expect(m.lessonsRead[id]).toBeDefined();
        }
        for (const [id, q] of Object.entries(side.quizScores)) {
          expect(m.quizScores[id].best).toBeGreaterThanOrEqual(q.best);
          expect(m.quizScores[id].attempts).toBeGreaterThanOrEqual(1);
        }
        for (const [id, lab] of Object.entries(side.labs)) {
          if (lab.status === 'passed') expect(m.labs[id].status).toBe('passed');
        }
        expect(m.exams.length).toBeGreaterThanOrEqual(side.exams.length);
      }
    }
  });
});

describe('restampAfter (importar una copia tras un reinicio)', () => {
  it('sin reinicio solo quita el resetAt de la copia', () => {
    const copia = { ...withLessonRead(emptyProgress(), 'a', at(1)), resetAt: at(0).toISOString() };
    const out = restampAfter(copia, undefined, at(50));
    expect(out.resetAt).toBeUndefined();
    expect(out.lessonsRead.a).toBe(at(1).toISOString());
  });

  it('tras un reinicio, lo anterior se re-sella y sobrevive a la fusión; lo posterior se respeta', () => {
    const copia = withQuizOutcome(
      withLessonRead(emptyProgress(), 'vieja', at(1)),
      { quizId: 'q', results: [correct('1')] },
      at(2),
    );
    const local = withLessonRead(
      { ...emptyProgress(), resetAt: at(10).toISOString() },
      'nueva',
      at(20),
    );
    const restaurada = mergeProgress(local, restampAfter(copia, local.resetAt, at(30)));
    expect(Object.keys(restaurada.lessonsRead).sort()).toEqual(['nueva', 'vieja']);
    expect(restaurada.quizScores.q.best).toBe(100);
    expect(restaurada.lessonsRead.nueva).toBe(at(20).toISOString());
    // Y una sincronización posterior con la nube (que conserva el reinicio) no la descarta.
    const nube = { ...emptyProgress(), resetAt: at(10).toISOString() };
    expect(Object.keys(mergeProgress(restaurada, nube).lessonsRead).sort()).toEqual([
      'nueva',
      'vieja',
    ]);
  });
});
