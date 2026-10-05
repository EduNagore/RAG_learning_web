/** Lógica pura de tests: corrección, barajado con semilla y construcción de exámenes. */

export type QuestionType = 'single' | 'multiple' | 'truefalse' | 'order' | 'code-output';

/** Pregunta tal y como se define en el YAML (ver content.config.ts). */
export interface Question {
  id: string;
  type: QuestionType;
  difficulty: number;
  prompt: string;
  code?: string;
  options?: string[];
  answer?: number[];
  explanation: string;
  ref?: string;
}

/** Pregunta lista para mostrar: el Markdown se renderiza en build y se añade su origen. */
export interface RenderedQuestion extends Question {
  promptHtml: string;
  explanationHtml: string;
  optionsHtml?: string[];
  lessonId: string;
  moduleId: string;
}

/**
 * Respuesta del usuario, siempre en índices ORIGINALES de `options` (no los mostrados):
 * - single / code-output: [i]
 * - multiple: conjunto de índices marcados
 * - truefalse: [0] = verdadero, [1] = falso
 * - order: la secuencia que ha construido el usuario
 */
export type Response = number[];

export const PASS_THRESHOLD = 80;

export function passed(pct: number): boolean {
  return pct >= PASS_THRESHOLD;
}

export function isCorrect(q: Question, response: Response): boolean {
  switch (q.type) {
    case 'order': {
      const n = q.options?.length ?? 0;
      return response.length === n && response.every((v, i) => v === i);
    }
    case 'multiple': {
      const expected = new Set(q.answer ?? []);
      const given = new Set(response);
      return (
        given.size === response.length &&
        given.size === expected.size &&
        [...given].every((i) => expected.has(i))
      );
    }
    default: {
      const expected = q.answer ?? [];
      return response.length === 1 && expected.length === 1 && response[0] === expected[0];
    }
  }
}

/** Porcentaje entero (0-100) de aciertos. Con 0 preguntas devuelve 0. */
export function scorePct(results: { correct: boolean }[]): number {
  if (results.length === 0) return 0;
  return Math.round((results.filter((r) => r.correct).length / results.length) * 100);
}

// --- Aleatoriedad reproducible ------------------------------------------------

/** PRNG mulberry32: determinista a partir de una semilla entera. */
export function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Fisher-Yates. No muta el original. */
export function shuffled<T>(items: readonly T[], rng: () => number): T[] {
  const out = [...items];
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

/**
 * Orden en que se muestran las opciones (índices originales). Las preguntas
 * `truefalse` no se barajan. En `order` se garantiza que el orden inicial NO sea
 * ya la solución.
 */
export function presentationOrder(q: Question, seed: number): number[] {
  const n = q.options?.length ?? 0;
  const identity = Array.from({ length: n }, (_, i) => i);
  if (q.type === 'truefalse' || n < 2) return identity;
  const rng = mulberry32(seed);
  let order = shuffled(identity, rng);
  if (q.type === 'order') {
    for (let guard = 0; guard < 20 && order.every((v, i) => v === i); guard++)
      order = shuffled(identity, rng);
    if (order.every((v, i) => v === i)) order = [...identity.slice(1), identity[0]];
  }
  return order;
}

/** Semilla estable por pregunta y por intento, para que cada una se baraje distinto. */
export function questionSeed(attemptSeed: number, questionId: string): number {
  let h = attemptSeed >>> 0;
  for (let i = 0; i < questionId.length; i++)
    h = Math.imul(h ^ questionId.charCodeAt(i), 16777619) >>> 0;
  return h;
}

// --- Exámenes -----------------------------------------------------------------

export interface ExamOptions {
  moduleIds: string[];
  count: number;
  seed: number;
}

/**
 * Elige `count` preguntas de los módulos indicados repartidas de forma proporcional
 * al tamaño de cada banco (método del mayor resto) y las baraja. Determinista.
 */
export function buildExam<T extends { moduleId: string }>(
  bank: readonly T[],
  opts: ExamOptions,
): T[] {
  const rng = mulberry32(opts.seed);
  const pool = bank.filter((q) => opts.moduleIds.includes(q.moduleId));
  if (pool.length <= opts.count) return shuffled(pool, rng);

  const byModule = new Map<string, T[]>();
  for (const q of pool) byModule.set(q.moduleId, [...(byModule.get(q.moduleId) ?? []), q]);
  const groups = [...byModule.entries()].sort(([a], [b]) => a.localeCompare(b));

  const exact = groups.map(([, qs]) => (qs.length / pool.length) * opts.count);
  const alloc = exact.map((x) => Math.floor(x));
  let remaining = opts.count - alloc.reduce((s, x) => s + x, 0);
  const byRemainder = exact
    .map((x, i) => ({ i, rest: x - Math.floor(x) }))
    .sort((a, b) => b.rest - a.rest || a.i - b.i);
  for (const { i } of byRemainder) {
    if (remaining === 0) break;
    if (alloc[i] < groups[i][1].length) {
      alloc[i]++;
      remaining--;
    }
  }

  const picked = groups.flatMap(([, qs], i) => shuffled(qs, rng).slice(0, alloc[i]));
  return shuffled(picked, rng);
}

export interface ExamAnswer {
  moduleId: string;
  correct: boolean;
}

/** Porcentaje de acierto por módulo (0-100). */
export function examBreakdown(answers: ExamAnswer[]): Record<string, number> {
  const groups = new Map<string, ExamAnswer[]>();
  for (const a of answers) groups.set(a.moduleId, [...(groups.get(a.moduleId) ?? []), a]);
  return Object.fromEntries([...groups.entries()].map(([m, list]) => [m, scorePct(list)]));
}

// --- Banco de preguntas publicado como JSON estático ---------------------------

export interface QuestionBank {
  questions: RenderedQuestion[];
  lessons: Record<string, { title: string; moduleId: string }>;
  modules: Record<string, { title: string; part: string; order: number }>;
}
