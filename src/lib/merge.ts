/**
 * Fusión de dos copias del progreso (otro dispositivo, copia de seguridad, nube).
 *
 * Es una función pura y **nunca pierde progreso**: cada campo se resuelve con un máximo sobre un
 * orden total (la marca de tiempo y, si empatan, otros campos), de modo que la fusión es
 * conmutativa, asociativa e idempotente (`merge(a, b) = merge(b, a)`, `merge(a, a) = a`).
 *
 * Única excepción documentada: tras un «reiniciar progreso» (`resetAt`) lo anterior se descarta
 * de cada copia antes de fusionar. Ahí se conservan la conmutatividad y la idempotencia, pero no
 * la asociatividad exacta de `best` en un test si el reinicio cae entre dos intentos.
 */
import type { ExamResult, LabState, Progress, QuizScore, SrsCard } from './progress';

/** Debe coincidir con `SCHEMA_VERSION` de progress.ts (hay un test). */
const VERSION = 2 as const;

const ts = (s: string | undefined): string => s ?? '';
const max = (a: string, b: string): string => (a >= b ? a : b);
const canon = (v: unknown): string => JSON.stringify(v, (_k, x) => sortKeys(x));
function sortKeys(x: unknown): unknown {
  if (typeof x !== 'object' || x === null || Array.isArray(x)) return x;
  return Object.fromEntries(Object.entries(x).sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0)));
}

/** Devuelve el mayor según una clave de varios campos (orden total, desempate por contenido). */
function maxBy<T>(a: T, b: T, key: (x: T) => (string | number)[]): T {
  const ka = key(a);
  const kb = key(b);
  for (let i = 0; i < ka.length; i++) {
    if (ka[i] > kb[i]) return a;
    if (ka[i] < kb[i]) return b;
  }
  return canon(a) >= canon(b) ? a : b;
}

function mergeRecords<T>(
  a: Record<string, T>,
  b: Record<string, T>,
  pick: (x: T, y: T) => T,
): Record<string, T> {
  const out: Record<string, T> = {};
  for (const id of new Set([...Object.keys(a), ...Object.keys(b)])) {
    out[id] = id in a && id in b ? pick(a[id], b[id]) : id in a ? a[id] : b[id];
  }
  return out;
}

const mergeQuiz = (x: QuizScore, y: QuizScore): QuizScore => {
  const latest = maxBy(x, y, (q) => [ts(q.updatedAt), q.attempts, q.last]);
  return {
    best: Math.max(x.best, y.best),
    last: latest.last,
    attempts: latest.attempts,
    ...(latest.updatedAt !== undefined ? { updatedAt: latest.updatedAt } : {}),
  };
};

const mergeLab = (x: LabState, y: LabState): LabState => {
  const latest = maxBy(x, y, (l) => [ts(l.updatedAt), l.code]);
  return {
    status: x.status === 'passed' || y.status === 'passed' ? 'passed' : 'started',
    code: latest.code,
    updatedAt: latest.updatedAt,
  };
};

const mergeCard = (x: SrsCard, y: SrsCard): SrsCard =>
  maxBy(x, y, (c) => [ts(c.reviewedAt), c.box, c.due]);

const examKey = (e: ExamResult) => `${e.date}|${e.score}|${e.total}`;

/** Descarta lo anterior (o igual) al último reinicio. Sin `resetAt` no toca nada. */
function afterReset(p: Progress, resetAt: string | undefined): Progress {
  if (!resetAt) return p;
  const keep = <T>(r: Record<string, T>, when: (v: T) => string | undefined) =>
    Object.fromEntries(Object.entries(r).filter(([, v]) => ts(when(v)) > resetAt));
  return {
    ...p,
    lessonsRead: keep(p.lessonsRead, (v) => v),
    unread: keep(p.unread, (v) => v),
    quizScores: keep(p.quizScores, (v) => v.updatedAt),
    labs: keep(p.labs, (v) => v.updatedAt),
    srs: keep(p.srs, (v) => v.reviewedAt),
    exams: p.exams.filter((e) => ts(e.date) > resetAt),
    resetAt,
  };
}

/**
 * Para restaurar una copia de seguridad DESPUÉS de un reinicio: lo que sea anterior (o igual) al
 * reinicio se «re-sella» con la hora actual, porque importar es una acción de ahora y, si no, la
 * siguiente sincronización lo descartaría. Quita el `resetAt` de la copia importada (una copia
 * nunca debe borrar el progreso local). El historial de exámenes muestra entonces la fecha de la
 * importación en lugar de la original.
 */
export function restampAfter(imported: Progress, resetAt: string | undefined, now: Date): Progress {
  const rest: Progress = { ...imported };
  delete rest.resetAt;
  if (!resetAt) return rest;
  const stamp = now.toISOString();
  const fresh = (t: string | undefined) => (ts(t) > resetAt ? (t as string) : stamp);
  return {
    ...rest,
    lessonsRead: Object.fromEntries(
      Object.entries(rest.lessonsRead).map(([k, v]) => [k, fresh(v)]),
    ),
    unread: {},
    quizScores: Object.fromEntries(
      Object.entries(rest.quizScores).map(([k, v]) => [k, { ...v, updatedAt: fresh(v.updatedAt) }]),
    ),
    labs: Object.fromEntries(
      Object.entries(rest.labs).map(([k, v]) => [k, { ...v, updatedAt: fresh(v.updatedAt) }]),
    ),
    srs: Object.fromEntries(
      Object.entries(rest.srs).map(([k, v]) => [k, { ...v, reviewedAt: fresh(v.reviewedAt) }]),
    ),
    exams: rest.exams.map((e) => ({ ...e, date: fresh(e.date) })),
  };
}

export function mergeProgress(a: Progress, b: Progress): Progress {
  const resetAt =
    a.resetAt === undefined && b.resetAt === undefined
      ? undefined
      : max(ts(a.resetAt), ts(b.resetAt));
  const x = afterReset(a, resetAt);
  const y = afterReset(b, resetAt);

  const reads = mergeRecords(x.lessonsRead, y.lessonsRead, max);
  const unread = mergeRecords(x.unread, y.unread, max);
  // «Leída» solo si la lectura es posterior al último desmarcado; el desmarcado se conserva.
  const lessonsRead = Object.fromEntries(
    Object.entries(reads).filter(([id, readAt]) => readAt > ts(unread[id])),
  );

  const exams = new Map<string, ExamResult>();
  for (const e of [...x.exams, ...y.exams]) exams.set(examKey(e), e);

  const merged: Progress = {
    version: VERSION,
    lessonsRead,
    unread,
    quizScores: mergeRecords(x.quizScores, y.quizScores, mergeQuiz),
    labs: mergeRecords(x.labs, y.labs, mergeLab),
    srs: mergeRecords(x.srs, y.srs, mergeCard),
    exams: [...exams.values()].sort((p, q) =>
      p.date !== q.date ? (p.date < q.date ? -1 : 1) : canon(p) < canon(q) ? -1 : 1,
    ),
  };
  if (resetAt !== undefined) merged.resetAt = resetAt;
  return merged;
}

/** Igualdad profunda del contenido (para saber si hace falta subir o guardar). */
export function sameProgress(a: Progress, b: Progress): boolean {
  return canon(mergeProgress(a, a)) === canon(mergeProgress(b, b));
}
