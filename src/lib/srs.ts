/** Repaso espaciado con el sistema Leitner de 5 cajas. */
import type { SrsCard } from './progress';

/** Días hasta el siguiente repaso según la caja (1-5). */
export const INTERVAL_DAYS = [1, 2, 4, 8, 16] as const;
export const MAX_BOX = INTERVAL_DAYS.length;

type Box = SrsCard['box'];
export type SrsState = Record<string, SrsCard>;

const DAY_MS = 24 * 60 * 60 * 1000;

export function addDays(from: Date, days: number): string {
  return new Date(from.getTime() + days * DAY_MS).toISOString();
}

/**
 * Aplica el resultado de una respuesta:
 * - Fallo: la tarjeta (nueva o existente) pasa a la caja 1 y vuelve en 1 día.
 * - Acierto en una tarjeta existente: sube una caja (máx. 5) y se espacia más.
 * - Acierto en una pregunta que no está en el sistema: no se crea tarjeta.
 */
export function applyResult(
  state: SrsState,
  questionId: string,
  correct: boolean,
  now: Date,
): SrsState {
  const card = state[questionId];
  const reviewedAt = now.toISOString();
  if (!correct) {
    return { ...state, [questionId]: { box: 1, due: addDays(now, INTERVAL_DAYS[0]), reviewedAt } };
  }
  if (!card) return state;
  const box = Math.min(card.box + 1, MAX_BOX) as Box;
  return { ...state, [questionId]: { box, due: addDays(now, INTERVAL_DAYS[box - 1]), reviewedAt } };
}

export function applyResults(
  state: SrsState,
  results: { id: string; correct: boolean }[],
  now: Date,
): SrsState {
  return results.reduce((s, r) => applyResult(s, r.id, r.correct, now), state);
}

export function isDue(card: SrsCard, now: Date): boolean {
  return new Date(card.due).getTime() <= now.getTime();
}

/** Ids de preguntas pendientes de repaso, las más atrasadas primero. */
export function dueQuestionIds(state: SrsState, now: Date): string[] {
  return Object.entries(state)
    .filter(([, card]) => isDue(card, now))
    .sort(([, a], [, b]) => new Date(a.due).getTime() - new Date(b.due).getTime())
    .map(([id]) => id);
}

/** Número de tarjetas por caja (índice 0 = caja 1). */
export function boxCounts(state: SrsState): number[] {
  const counts = new Array<number>(MAX_BOX).fill(0);
  for (const card of Object.values(state)) counts[card.box - 1]++;
  return counts;
}

/** Fecha del próximo repaso, o null si no hay tarjetas. */
export function nextDue(state: SrsState): string | null {
  const dues = Object.values(state)
    .map((c) => c.due)
    .sort();
  return dues[0] ?? null;
}
