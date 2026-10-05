import { describe, expect, it } from 'vitest';
import {
  PASS_THRESHOLD,
  buildExam,
  examBreakdown,
  isCorrect,
  mulberry32,
  passed,
  presentationOrder,
  questionSeed,
  scorePct,
  shuffled,
  type Question,
} from '../../src/lib/quiz';

const base = { difficulty: 1, prompt: 'p', explanation: 'e' };
const single: Question = {
  ...base,
  id: 's',
  type: 'single',
  options: ['a', 'b', 'c'],
  answer: [1],
};
const multiple: Question = {
  ...base,
  id: 'm',
  type: 'multiple',
  options: ['a', 'b', 'c', 'd'],
  answer: [0, 2],
};
const tf: Question = { ...base, id: 't', type: 'truefalse', answer: [0] };
const order: Question = {
  ...base,
  id: 'o',
  type: 'order',
  options: ['uno', 'dos', 'tres', 'cuatro'],
};
const code: Question = {
  ...base,
  id: 'c',
  type: 'code-output',
  code: 'print(1)',
  options: ['1', '2'],
  answer: [0],
};

describe('isCorrect', () => {
  it('single y code-output exigen exactamente la opción correcta', () => {
    expect(isCorrect(single, [1])).toBe(true);
    expect(isCorrect(single, [0])).toBe(false);
    expect(isCorrect(single, [])).toBe(false);
    expect(isCorrect(single, [1, 2])).toBe(false);
    expect(isCorrect(code, [0])).toBe(true);
    expect(isCorrect(code, [1])).toBe(false);
  });

  it('multiple exige el conjunto exacto, sin importar el orden ni parciales', () => {
    expect(isCorrect(multiple, [2, 0])).toBe(true);
    expect(isCorrect(multiple, [0])).toBe(false); // incompleta
    expect(isCorrect(multiple, [0, 1, 2])).toBe(false); // de más
    expect(isCorrect(multiple, [0, 0, 2])).toBe(false); // repetidos no cuentan como acierto
    expect(isCorrect(multiple, [])).toBe(false);
  });

  it('truefalse: 0 = verdadero, 1 = falso', () => {
    expect(isCorrect(tf, [0])).toBe(true);
    expect(isCorrect(tf, [1])).toBe(false);
  });

  it('order solo acepta la secuencia completa en el orden de options', () => {
    expect(isCorrect(order, [0, 1, 2, 3])).toBe(true);
    expect(isCorrect(order, [1, 0, 2, 3])).toBe(false);
    expect(isCorrect(order, [0, 1, 2])).toBe(false);
    expect(isCorrect(order, [])).toBe(false);
  });
});

describe('puntuación', () => {
  it('redondea a entero y tolera listas vacías', () => {
    expect(scorePct([])).toBe(0);
    expect(scorePct([{ correct: true }, { correct: false }, { correct: true }])).toBe(67);
    expect(scorePct([{ correct: true }])).toBe(100);
  });

  it('aprueba a partir del 80 %', () => {
    expect(PASS_THRESHOLD).toBe(80);
    expect(passed(80)).toBe(true);
    expect(passed(79)).toBe(false);
  });
});

describe('aleatoriedad reproducible', () => {
  it('la misma semilla da la misma secuencia y semillas distintas, otra', () => {
    const a = mulberry32(42);
    const b = mulberry32(42);
    const seqA = Array.from({ length: 5 }, () => a());
    expect(seqA).toEqual(Array.from({ length: 5 }, () => b()));
    expect(seqA).not.toEqual(
      Array.from(
        { length: 5 },
        (
          (c) => () =>
            c()
        )(mulberry32(43)),
      ),
    );
    expect(seqA.every((x) => x >= 0 && x < 1)).toBe(true);
  });

  it('shuffled es una permutación y no muta la entrada', () => {
    const input = [1, 2, 3, 4, 5, 6, 7, 8];
    const out = shuffled(input, mulberry32(7));
    expect([...out].sort()).toEqual(input);
    expect(input).toEqual([1, 2, 3, 4, 5, 6, 7, 8]);
  });

  it('presentationOrder es una permutación de las opciones y es estable por semilla', () => {
    const o1 = presentationOrder(multiple, 123);
    expect([...o1].sort()).toEqual([0, 1, 2, 3]);
    expect(presentationOrder(multiple, 123)).toEqual(o1);
  });

  it('truefalse no se baraja', () => {
    expect(presentationOrder(tf, 5)).toEqual([]);
  });

  it('en order el orden inicial nunca es ya la solución', () => {
    for (let seed = 0; seed < 200; seed++) {
      const o = presentationOrder(order, seed);
      expect([...o].sort()).toEqual([0, 1, 2, 3]);
      expect(o.every((v, i) => v === i)).toBe(false);
    }
  });

  it('questionSeed varía por pregunta y por intento', () => {
    expect(questionSeed(1, 'a')).not.toBe(questionSeed(1, 'b'));
    expect(questionSeed(1, 'a')).not.toBe(questionSeed(2, 'a'));
    expect(questionSeed(1, 'a')).toBe(questionSeed(1, 'a'));
  });
});

describe('buildExam', () => {
  const bank = [
    ...Array.from({ length: 30 }, (_, i) => ({ id: `a${i}`, moduleId: 'A' })),
    ...Array.from({ length: 10 }, (_, i) => ({ id: `b${i}`, moduleId: 'B' })),
    ...Array.from({ length: 5 }, (_, i) => ({ id: `c${i}`, moduleId: 'C' })),
  ];

  it('devuelve exactamente `count` preguntas sin repetir', () => {
    const exam = buildExam(bank, { moduleIds: ['A', 'B', 'C'], count: 20, seed: 1 });
    expect(exam).toHaveLength(20);
    expect(new Set(exam.map((q) => q.id)).size).toBe(20);
  });

  it('reparte de forma proporcional al tamaño de cada módulo', () => {
    const exam = buildExam(bank, { moduleIds: ['A', 'B', 'C'], count: 18, seed: 1 });
    const counts = (m: string) => exam.filter((q) => q.moduleId === m).length;
    expect(counts('A')).toBe(12); // 30/45 * 18
    expect(counts('B')).toBe(4); // 10/45 * 18 = 4
    expect(counts('C')).toBe(2); // 5/45 * 18 = 2
  });

  it('solo usa los módulos pedidos', () => {
    const exam = buildExam(bank, { moduleIds: ['B'], count: 5, seed: 3 });
    expect(exam.every((q) => q.moduleId === 'B')).toBe(true);
    expect(exam).toHaveLength(5);
  });

  it('si hay menos preguntas que `count`, devuelve todas barajadas', () => {
    const exam = buildExam(bank, { moduleIds: ['C'], count: 40, seed: 9 });
    expect(exam).toHaveLength(5);
  });

  it('nunca asigna más preguntas a un módulo de las que tiene', () => {
    const small = [
      ...Array.from({ length: 2 }, (_, i) => ({ id: `x${i}`, moduleId: 'X' })),
      ...Array.from({ length: 50 }, (_, i) => ({ id: `y${i}`, moduleId: 'Y' })),
    ];
    const exam = buildExam(small, { moduleIds: ['X', 'Y'], count: 40, seed: 2 });
    expect(exam).toHaveLength(40);
    expect(exam.filter((q) => q.moduleId === 'X').length).toBeLessThanOrEqual(2);
  });

  it('es determinista por semilla', () => {
    const a = buildExam(bank, { moduleIds: ['A', 'B'], count: 10, seed: 77 }).map((q) => q.id);
    const b = buildExam(bank, { moduleIds: ['A', 'B'], count: 10, seed: 77 }).map((q) => q.id);
    const c = buildExam(bank, { moduleIds: ['A', 'B'], count: 10, seed: 78 }).map((q) => q.id);
    expect(a).toEqual(b);
    expect(a).not.toEqual(c);
  });

  it('sin módulos seleccionados devuelve vacío', () => {
    expect(buildExam(bank, { moduleIds: [], count: 10, seed: 1 })).toEqual([]);
  });
});

describe('examBreakdown', () => {
  it('calcula el porcentaje por módulo', () => {
    const r = examBreakdown([
      { moduleId: 'A', correct: true },
      { moduleId: 'A', correct: false },
      { moduleId: 'B', correct: true },
    ]);
    expect(r).toEqual({ A: 50, B: 100 });
  });
});
