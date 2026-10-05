import { describe, expect, it } from 'vitest';
import { parseRanking, rrfFuse } from '../../src/lib/rrf';

describe('rrfFuse', () => {
  it('suma 1/(k+posición) y ordena de mayor a menor', () => {
    const out = rrfFuse([['a', 'b', 'c'], ['c', 'a', 'd']], 60);
    expect(out.map((d) => d.id)).toEqual(['a', 'c', 'b', 'd']);
    expect(out[0].score).toBeCloseTo(1 / 61 + 1 / 62, 10);
    expect(out[1].score).toBeCloseTo(1 / 63 + 1 / 61, 10);
    expect(out[2].score).toBeCloseTo(1 / 62, 10);
  });

  it('la constante k cambia el ganador (k=0 frente a k=60)', () => {
    const rankings = [['A', 'B', 'D'], ['C', 'E', 'B']];
    expect(rrfFuse(rankings, 0)[0].id).toBe('A');
    expect(rrfFuse(rankings, 60)[0].id).toBe('B');
  });

  it('un id repetido en un ranking cuenta una vez, con su primera posición', () => {
    const out = rrfFuse([['a', 'a', 'b']], 60);
    expect(out[0].score).toBeCloseTo(1 / 61, 10);
    expect(out.find((d) => d.id === 'b')!.ranks).toEqual([3]);
  });

  it('los empates conservan el orden de primera aparición', () => {
    expect(rrfFuse([['x', 'y'], ['y', 'x']], 60).map((d) => d.id)).toEqual(['x', 'y']);
  });

  it('registra la posición y la contribución por ranking', () => {
    const d = rrfFuse([['a'], ['b', 'a']], 10).find((x) => x.id === 'a')!;
    expect(d.ranks).toEqual([1, 2]);
    expect(d.parts[1]).toBeCloseTo(1 / 12, 10);
  });

  it('sin rankings devuelve una lista vacía', () => {
    expect(rrfFuse([], 60)).toEqual([]);
    expect(rrfFuse([[], []], 60)).toEqual([]);
  });
});

describe('parseRanking', () => {
  it('admite comas y saltos de línea y descarta vacíos', () => {
    expect(parseRanking('a, b\n c ,, \n')).toEqual(['a', 'b', 'c']);
  });
});
