import { describe, expect, it } from 'vitest';
import { HashingEmbedder, cosine, crc32, tokenize } from '../../src/lib/embeddings';

// Valores de referencia generados con ragkit (Python) con dim=64.
const REFERENCE: [string, string[], Record<number, number>][] = [
  [
    '¿Cuántos días tengo para devolver un pedido?',
    ['cuantos', 'dias', 'devolver', 'pedido'],
    { 1: 0.333333, 7: -0.333333, 14: -0.333333, 22: 0.666667, 27: 0.333333, 63: 0.333333 },
  ],
  [
    'El reembolso tarda 7 días hábiles',
    ['reembolso', 'tarda', '7', 'dias', 'habiles'],
    {
      1: -0.301511,
      2: 0.301511,
      7: -0.603023,
      36: -0.301511,
      38: 0.301511,
      39: 0.301511,
      40: 0.301511,
      55: -0.301511,
    },
  ],
  ['ñandú año', ['ñandu', 'año'], { 1: -0.57735, 19: -0.57735, 37: -0.57735 }],
];

describe('port de ragkit a TypeScript', () => {
  it('crc32 coincide con zlib.crc32', () => {
    expect(crc32('hello')).toBe(0x3610a686);
    expect(crc32('')).toBe(0);
  });

  it.each(REFERENCE)('tokeniza igual que Python: %s', (text, tokens) => {
    expect(tokenize(text)).toEqual(tokens);
  });

  it.each(REFERENCE)('produce el mismo vector que Python: %s', (text, _tokens, nonzero) => {
    const vec = new HashingEmbedder(64).embed(text);
    const got = Object.fromEntries(
      vec.flatMap((v, i) => (v !== 0 ? [[i, Number(v.toFixed(6))]] : [])),
    );
    expect(got).toEqual(nonzero);
  });

  it('los vectores están normalizados y el coseno de un texto consigo mismo es 1', () => {
    const e = new HashingEmbedder(128);
    const v = e.embed('el reembolso tarda siete días');
    expect(Math.hypot(...v)).toBeCloseTo(1, 10);
    expect(cosine(v, v)).toBeCloseTo(1, 10);
  });

  it('un texto sin palabras útiles da el vector cero', () => {
    const v = new HashingEmbedder(32).embed('el de la');
    expect(v.every((x) => x === 0)).toBe(true);
    expect(cosine(v, v)).toBe(0);
  });
});
