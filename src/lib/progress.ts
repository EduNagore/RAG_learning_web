import { atom } from 'nanostores';

/** Clave de localStorage; el sufijo es la versión del esquema. */
export const STORAGE_KEY = 'rma:progress:v1';
export const SCHEMA_VERSION = 1;

export interface QuizScore {
  best: number;
  last: number;
  attempts: number;
}

export interface LabState {
  status: 'started' | 'passed';
  code: string;
  updatedAt: string;
}

export interface SrsCard {
  box: 1 | 2 | 3 | 4 | 5;
  due: string;
}

export interface ExamResult {
  date: string;
  score: number;
  total: number;
  byModule: Record<string, number>;
}

export interface Progress {
  version: typeof SCHEMA_VERSION;
  lessonsRead: Record<string, string>;
  quizScores: Record<string, QuizScore>;
  labs: Record<string, LabState>;
  srs: Record<string, SrsCard>;
  exams: ExamResult[];
}

export function emptyProgress(): Progress {
  return { version: SCHEMA_VERSION, lessonsRead: {}, quizScores: {}, labs: {}, srs: {}, exams: [] };
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
  return {
    version: SCHEMA_VERSION,
    lessonsRead: pick<string>('lessonsRead'),
    quizScores: pick<QuizScore>('quizScores'),
    labs: pick<LabState>('labs'),
    srs: pick<SrsCard>('srs'),
    exams: Array.isArray(data.exams) ? (data.exams as ExamResult[]) : [],
  };
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
  return { ...p, lessonsRead: { ...p.lessonsRead, [lessonId]: now.toISOString() } };
}

export function withLessonUnread(p: Progress, lessonId: string): Progress {
  const lessonsRead = { ...p.lessonsRead };
  delete lessonsRead[lessonId];
  return { ...p, lessonsRead };
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

export function updateProgress(fn: (p: Progress) => Progress): void {
  const next = fn($progress.get());
  $progress.set(next);
  saveProgress(next);
}

export const markLessonRead = (id: string) => updateProgress((p) => withLessonRead(p, id));
export const markLessonUnread = (id: string) => updateProgress((p) => withLessonUnread(p, id));
export const resetProgress = () => updateProgress(() => emptyProgress());
