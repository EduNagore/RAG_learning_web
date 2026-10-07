import { atom } from 'nanostores';
import { applyResults } from './srs';
import { mergeProgress, restampAfter } from './merge';

/**
 * Clave de localStorage. Se mantiene estable entre versiones del esquema para no dejar datos
 * huérfanos; la versión del esquema va dentro del JSON (`version`).
 */
export const STORAGE_KEY = 'rma:progress:v1';
/** v2 añade marcas de tiempo por entrada (para fusionar copias de varios dispositivos). */
export const SCHEMA_VERSION = 2;

export interface QuizScore {
  best: number;
  last: number;
  attempts: number;
  /** Momento del último intento (ISO). Ausente en datos de la v1. */
  updatedAt?: string;
}

export interface LabState {
  status: 'started' | 'passed';
  code: string;
  updatedAt: string;
}

export interface SrsCard {
  box: 1 | 2 | 3 | 4 | 5;
  due: string;
  /** Momento de la última respuesta (ISO). Ausente en datos de la v1. */
  reviewedAt?: string;
}

export interface ExamResult {
  date: string;
  score: number;
  total: number;
  byModule: Record<string, number>;
}

export interface Progress {
  version: typeof SCHEMA_VERSION;
  /** Lección → momento en que se marcó como leída (ISO). */
  lessonsRead: Record<string, string>;
  /** Lección → momento en que se desmarcó. Permite que «no leída» gane a una copia antigua. */
  unread: Record<string, string>;
  quizScores: Record<string, QuizScore>;
  labs: Record<string, LabState>;
  srs: Record<string, SrsCard>;
  exams: ExamResult[];
  /** Momento del último «reiniciar progreso»: lo anterior no debe resucitar al fusionar. */
  resetAt?: string;
}

export function emptyProgress(): Progress {
  return {
    version: SCHEMA_VERSION,
    lessonsRead: {},
    unread: {},
    quizScores: {},
    labs: {},
    srs: {},
    exams: [],
  };
}

const isRecord = (v: unknown): v is Record<string, unknown> =>
  typeof v === 'object' && v !== null && !Array.isArray(v);

/**
 * Interpreta un JSON guardado. Es tolerante: ante datos corruptos o de otra versión
 * devuelve lo que se pueda aprovechar sin lanzar nunca, para no romper la web.
 */
export function parseProgress(raw: string | null | undefined): Progress {
  const base = emptyProgress();
  if (!raw) return base;
  let data: unknown;
  try {
    data = JSON.parse(raw);
  } catch {
    return base;
  }
  if (!isRecord(data)) return base;
  const pick = <T>(key: string): Record<string, T> =>
    isRecord(data[key]) ? (data[key] as Record<string, T>) : {};
  // Acepta la v1 (sin `unread` ni marcas de tiempo) y la v2: la migración es rellenar lo que falta.
  const progress: Progress = {
    version: SCHEMA_VERSION,
    lessonsRead: pick<string>('lessonsRead'),
    unread: pick<string>('unread'),
    quizScores: pick<QuizScore>('quizScores'),
    labs: pick<LabState>('labs'),
    srs: pick<SrsCard>('srs'),
    exams: Array.isArray(data.exams) ? (data.exams as ExamResult[]) : [],
  };
  if (typeof data.resetAt === 'string') progress.resetAt = data.resetAt;
  return progress;
}

/** Acceso defensivo a localStorage (puede lanzar o no existir: modo privado, SSR, tests). */
function getStorage(): Storage | null {
  try {
    return typeof localStorage === 'undefined' ? null : localStorage;
  } catch {
    return null;
  }
}

export function loadProgress(storage: Storage | null = getStorage()): Progress {
  try {
    return parseProgress(storage?.getItem(STORAGE_KEY));
  } catch {
    return emptyProgress();
  }
}

export function saveProgress(p: Progress, storage: Storage | null = getStorage()): void {
  try {
    storage?.setItem(STORAGE_KEY, JSON.stringify(p));
  } catch {
    // Cuota llena o almacenamiento bloqueado: la web sigue funcionando sin persistencia.
  }
}

// --- Transformaciones puras -------------------------------------------------

export function withLessonRead(p: Progress, lessonId: string, now = new Date()): Progress {
  const unread = { ...p.unread };
  delete unread[lessonId];
  return { ...p, lessonsRead: { ...p.lessonsRead, [lessonId]: now.toISOString() }, unread };
}

export function withLessonUnread(p: Progress, lessonId: string, now = new Date()): Progress {
  const lessonsRead = { ...p.lessonsRead };
  delete lessonsRead[lessonId];
  return { ...p, lessonsRead, unread: { ...p.unread, [lessonId]: now.toISOString() } };
}

export interface QuizOutcome {
  /** Id del quiz: el id de la lección, o "module:<id>" para el test de un módulo. */
  quizId: string;
  results: { id: string; correct: boolean }[];
}

/**
 * Registra un intento: actualiza mejor/último/intentos (porcentaje 0-100) y manda
 * las preguntas fallidas al repaso espaciado (o hace avanzar las ya existentes).
 */
export function withQuizOutcome(p: Progress, outcome: QuizOutcome, now = new Date()): Progress {
  const total = outcome.results.length;
  const pct =
    total === 0 ? 0 : Math.round((outcome.results.filter((r) => r.correct).length / total) * 100);
  const prev = p.quizScores[outcome.quizId];
  return {
    ...p,
    quizScores: {
      ...p.quizScores,
      [outcome.quizId]: {
        best: Math.max(prev?.best ?? 0, pct),
        last: pct,
        attempts: (prev?.attempts ?? 0) + 1,
        updatedAt: now.toISOString(),
      },
    },
    srs: applyResults(p.srs, outcome.results, now),
  };
}

/** Resultado de un repaso espaciado: solo toca el sistema Leitner, no las notas de los quizzes. */
export function withReview(
  p: Progress,
  results: { id: string; correct: boolean }[],
  now = new Date(),
): Progress {
  return { ...p, srs: applyResults(p.srs, results, now) };
}

/** Guarda el código del alumno. Un laboratorio ya superado no vuelve a "started". */
export function withLabCode(p: Progress, labId: string, code: string, now = new Date()): Progress {
  const status = p.labs[labId]?.status ?? 'started';
  return { ...p, labs: { ...p.labs, [labId]: { status, code, updatedAt: now.toISOString() } } };
}

export function withLabPassed(
  p: Progress,
  labId: string,
  code: string,
  now = new Date(),
): Progress {
  return {
    ...p,
    labs: { ...p.labs, [labId]: { status: 'passed', code, updatedAt: now.toISOString() } },
  };
}

export function withExam(p: Progress, exam: ExamResult): Progress {
  return { ...p, exams: [...p.exams, exam] };
}

export function moduleCompletion(
  p: Progress,
  lessonIds: string[],
): { done: number; total: number } {
  return { done: lessonIds.filter((id) => id in p.lessonsRead).length, total: lessonIds.length };
}

/** Exporta el progreso como JSON legible para copia de seguridad. */
export function exportProgress(p: Progress): string {
  return JSON.stringify(p, null, 2);
}

/** Importa una copia de seguridad. Lanza si el texto no es un JSON de progreso válido. */
export function importProgress(json: string): Progress {
  let data: unknown;
  try {
    data = JSON.parse(json);
  } catch {
    throw new Error('El archivo no es un JSON válido.');
  }
  if (!isRecord(data) || !('lessonsRead' in data || 'quizScores' in data || 'labs' in data)) {
    throw new Error('El archivo no parece una copia de seguridad de progreso.');
  }
  return parseProgress(json);
}

// --- Store reactivo (solo cliente) ------------------------------------------

export const $progress = atom<Progress>(emptyProgress());

/** Carga desde localStorage al store. Llamar una vez al montar en el cliente. */
export function hydrateProgress(): void {
  $progress.set(loadProgress());
}

/**
 * Aplica un cambio partiendo SIEMPRE de lo guardado en localStorage (la fuente de verdad):
 * así una isla que aún no se ha hidratado, o una segunda pestaña, no pisa el progreso
 * existente con un estado vacío. Sin almacenamiento disponible se usa el store en memoria.
 */
export function updateProgress(fn: (p: Progress) => Progress): void {
  const storage = getStorage();
  const next = fn(storage ? loadProgress(storage) : $progress.get());
  $progress.set(next);
  saveProgress(next, storage);
}

export const recordQuizOutcome = (outcome: QuizOutcome) =>
  updateProgress((p) => withQuizOutcome(p, outcome));
export const recordReview = (results: { id: string; correct: boolean }[]) =>
  updateProgress((p) => withReview(p, results));
export const saveLabCode = (labId: string, code: string) =>
  updateProgress((p) => withLabCode(p, labId, code));
export const markLabPassed = (labId: string, code: string) =>
  updateProgress((p) => withLabPassed(p, labId, code));
export const recordExam = (exam: ExamResult) => updateProgress((p) => withExam(p, exam));
export const markLessonRead = (id: string) => updateProgress((p) => withLessonRead(p, id));
export const markLessonUnread = (id: string) => updateProgress((p) => withLessonUnread(p, id));
/**
 * Reinicia el progreso. Con `propagate` (por defecto) deja una marca `resetAt` para que el
 * reinicio llegue a la nube y a otros dispositivos al sincronizar; sin ella, solo se vacía lo local.
 */
export const resetProgress = (propagate = true) =>
  updateProgress(() =>
    propagate ? { ...emptyProgress(), resetAt: new Date().toISOString() } : emptyProgress(),
  );

/** Sustituye todo el progreso. La importación de copias usa `mergeIntoProgress` (no pierde nada). */
export const replaceProgress = (p: Progress) => updateProgress(() => p);

/**
 * Importa una copia de seguridad: se fusiona con lo local (no se pierde nada) y, si hubo un
 * reinicio, lo importado se re-sella para que no lo descarte la siguiente sincronización.
 */
export const importIntoProgress = (imported: Progress) =>
  updateProgress((p) => mergeProgress(p, restampAfter(imported, p.resetAt, new Date())));

/** Fusiona un progreso externo (otro dispositivo, la nube) con el local. */
export const mergeIntoProgress = (other: Progress) =>
  updateProgress((p) => mergeProgress(p, other));
