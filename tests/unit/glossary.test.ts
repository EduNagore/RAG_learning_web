import { describe, expect, it } from 'vitest';
import { filterTerms, normalize, type GlossaryTerm } from '../../src/lib/glossary';

const terms: GlossaryTerm[] = [
  { id: 'a', es: 'recuperación contextual', en: 'contextual retrieval', def: 'x', lessons: [] },
  { id: 'b', es: 'tríada letal', en: 'lethal trifecta', def: 'y', lessons: [] },
];

describe('glosario', () => {
  it('normalize quita acentos y mayúsculas', () => {
    expect(normalize('Recuperación')).toBe('recuperacion');
  });
  it('filterTerms busca en español, inglés y definición sin distinguir acentos', () => {
    expect(filterTerms(terms, 'recuperacion').map((t) => t.id)).toEqual(['a']);
    expect(filterTerms(terms, 'TRIFECTA').map((t) => t.id)).toEqual(['b']);
    expect(filterTerms(terms, '  ').length).toBe(2);
    expect(filterTerms(terms, 'zzz')).toEqual([]);
  });
});
