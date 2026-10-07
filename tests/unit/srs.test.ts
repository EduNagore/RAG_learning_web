import { describe, expect, it } from 'vitest';
import { emptyProgress, withExam, withQuizOutcome, withReview } from '../../src/lib/progress';
import {
  INTERVAL_DAYS,
  addDays,
  applyResult,
  applyResults,
  boxCounts,
  dueQuestionIds,
  isDue,
  nextDue,
  type SrsState,
} from '../../src/lib/srs';

const T0 = new Date('2026-10-05T10:00:00.000Z');
const daysLater = (n: number) => new Date(T0.getTime() + n * 24 * 60 * 60 * 1000);

describe('Leitner', () => {
  it('los intervalos son 1, 2, 4, 8 y 16 días', () => {
    expect([...INTERVAL_DAYS]).toEqual([1, 2, 4, 8, 16]);
  });

  it('un fallo nuevo entra en la caja 1 y vuelve en 1 día', () => {
    const s = applyResult({}, 'q1', false, T0);
    expect(s.q1).toEqual({ box: 1, due: addDays(T0, 1), reviewedAt: T0.toISOString() });
  });

  it('un acierto en una pregunta que no está en el sistema no crea tarjeta', () => {
    expect(applyResult({}, 'q1', true, T0)).toEqual({});
  });

  it('cada acierto sube una caja y espacia más el repaso', () => {
    let s = applyResult({}, 'q', false, T0);
    const boxes: number[] = [];
    const dues: string[] = [];
    for (let i = 0; i < 4; i++) {
      s = applyResult(s, 'q', true, T0);
      boxes.push(s.q.box);
      dues.push(s.q.due);
    }
    expect(boxes).toEqual([2, 3, 4, 5]);
    expect(dues).toEqual([2, 4, 8, 16].map((d) => addDays(T0, d)));
  });

  it('la caja 5 es el tope y se mantiene a 16 días', () => {
    let s: SrsState = { q: { box: 5, due: T0.toISOString() } };
    s = applyResult(s, 'q', true, T0);
    expect(s.q).toEqual({ box: 5, due: addDays(T0, 16), reviewedAt: T0.toISOString() });
  });

  it('un fallo en cualquier caja vuelve a la 1', () => {
    const s = applyResult({ q: { box: 4, due: T0.toISOString() } }, 'q', false, T0);
    expect(s.q.box).toBe(1);
    expect(s.q.due).toBe(addDays(T0, 1));
  });

  it('no muta el estado original', () => {
    const original = { q: { box: 2 as const, due: T0.toISOString() } };
    applyResult(original, 'q', true, T0);
    expect(original.q.box).toBe(2);
  });

  it('applyResults encadena varios resultados', () => {
    const s = applyResults(
      {},
      [
        { id: 'a', correct: false },
        { id: 'b', correct: true },
        { id: 'c', correct: false },
      ],
      T0,
    );
    expect(Object.keys(s).sort()).toEqual(['a', 'c']);
  });
});

describe('pendientes', () => {
  const state = {
    tarde: { box: 1 as const, due: daysLater(-3).toISOString() },
    hoy: { box: 2 as const, due: T0.toISOString() },
    futuro: { box: 3 as const, due: daysLater(2).toISOString() },
  };

  it('isDue incluye el instante exacto del vencimiento', () => {
    expect(isDue(state.hoy, T0)).toBe(true);
    expect(isDue(state.futuro, T0)).toBe(false);
  });

  it('dueQuestionIds devuelve las vencidas, las más atrasadas primero', () => {
    expect(dueQuestionIds(state, T0)).toEqual(['tarde', 'hoy']);
    expect(dueQuestionIds(state, daysLater(3))).toEqual(['tarde', 'hoy', 'futuro']);
  });

  it('boxCounts cuenta por caja', () => {
    expect(boxCounts(state)).toEqual([1, 1, 1, 0, 0]);
    expect(boxCounts({})).toEqual([0, 0, 0, 0, 0]);
  });

  it('nextDue devuelve la fecha más próxima o null', () => {
    expect(nextDue(state)).toBe(daysLater(-3).toISOString());
    expect(nextDue({})).toBeNull();
  });
});

describe('integración con el progreso', () => {
  it('withQuizOutcome guarda mejor, último e intentos y manda los fallos al repaso', () => {
    let p = withQuizOutcome(
      emptyProgress(),
      {
        quizId: 'm0/01',
        results: [
          { id: 'q1', correct: true },
          { id: 'q2', correct: false },
        ],
      },
      T0,
    );
    expect(p.quizScores['m0/01']).toEqual({
      best: 50,
      last: 50,
      attempts: 1,
      updatedAt: T0.toISOString(),
    });
    expect(Object.keys(p.srs)).toEqual(['q2']);

    p = withQuizOutcome(
      p,
      {
        quizId: 'm0/01',
        results: [
          { id: 'q1', correct: true },
          { id: 'q2', correct: true },
        ],
      },
      daysLater(1),
    );
    expect(p.quizScores['m0/01']).toEqual({
      best: 100,
      last: 100,
      attempts: 2,
      updatedAt: daysLater(1).toISOString(),
    });
    expect(p.srs.q2.box).toBe(2); // acertó la fallada: sube de caja

    p = withQuizOutcome(
      p,
      {
        quizId: 'm0/01',
        results: [
          { id: 'q1', correct: false },
          { id: 'q2', correct: true },
        ],
      },
      daysLater(2),
    );
    expect(p.quizScores['m0/01']).toEqual({
      best: 100,
      last: 50,
      attempts: 3,
      updatedAt: daysLater(2).toISOString(),
    }); // el mejor no baja
  });

  it('withReview solo toca el repaso, no las notas', () => {
    const p = withReview(emptyProgress(), [{ id: 'q', correct: false }], T0);
    expect(p.quizScores).toEqual({});
    expect(p.srs.q.box).toBe(1);
  });

  it('withExam añade el examen al historial', () => {
    const exam = { date: T0.toISOString(), score: 15, total: 20, byModule: { A: 75 } };
    expect(withExam(emptyProgress(), exam).exams).toEqual([exam]);
  });
});
