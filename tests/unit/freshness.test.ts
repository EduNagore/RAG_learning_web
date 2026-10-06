import { describe, expect, it } from 'vitest';
import { findStale, formatReport } from '../../scripts/check-freshness.mjs';

const now = new Date('2026-10-06');

describe('findStale', () => {
  it('marca las lecciones con más de 6 meses y las de volatilidad alta con más de 3', () => {
    const stale = findStale(
      [
        { id: 'a', lastReviewed: '2026-09-01', volatility: 'high' }, // 35 días: bien
        { id: 'b', lastReviewed: '2026-06-01', volatility: 'high' }, // 127 días: vencida
        { id: 'c', lastReviewed: '2026-06-01', volatility: 'medium' }, // 127 días: bien
        { id: 'd', lastReviewed: '2026-02-01', volatility: 'low' }, // 247 días: vencida
      ],
      now,
    );
    expect(stale.map((l) => l.id)).toEqual(['d', 'b']);
    expect(stale[0].ageDays).toBe(247);
  });

  it('respeta el límite exacto (no marca el último día del plazo)', () => {
    const day = (n: number) => new Date(now.getTime() - n * 86_400_000).toISOString();
    expect(findStale([{ id: 'x', lastReviewed: day(92), volatility: 'high' }], now)).toHaveLength(
      0,
    );
    expect(findStale([{ id: 'x', lastReviewed: day(93), volatility: 'high' }], now)).toHaveLength(
      1,
    );
    expect(findStale([{ id: 'y', lastReviewed: day(183), volatility: 'low' }], now)).toHaveLength(
      0,
    );
    expect(findStale([{ id: 'y', lastReviewed: day(184), volatility: 'low' }], now)).toHaveLength(
      1,
    );
  });
});

describe('formatReport', () => {
  it('lista las lecciones vencidas en una tabla o indica que todo está al día', () => {
    const stale = findStale([{ id: 'm00/01', lastReviewed: '2026-01-01', volatility: 'low' }], now);
    const report = formatReport(stale, 10, now);
    expect(report).toContain('1 de 10 lecciones necesitan revisión');
    expect(report).toContain('`m00/01`');
    expect(formatReport([], 10, now)).toContain('Las 10 lecciones están dentro de su plazo');
  });
});
