import { describe, expect, it } from 'vitest';
import { chunkFixed, chunkMarkdown, chunkRecursive } from '../../src/lib/chunking';

describe('chunkFixed (misma semántica que el lab de Python)', () => {
  const diez = 'uno dos tres cuatro cinco seis siete ocho nueve diez';

  it('ventanas con solape', () => {
    expect(chunkFixed(diez, 4, 1)).toEqual([
      'uno dos tres cuatro',
      'cuatro cinco seis siete',
      'siete ocho nueve diez',
    ]);
  });

  it('no genera un fragmento redundante al final', () => {
    expect(chunkFixed('a b c d e f g', 4, 2)).toEqual(['a b c d', 'c d e f', 'e f g']);
    expect(chunkFixed(diez, 5, 0)).toHaveLength(2);
  });

  it('casos límite', () => {
    expect(chunkFixed('', 4, 1)).toEqual([]);
    expect(chunkFixed('hola mundo', 5, 1)).toEqual(['hola mundo']);
    expect(chunkFixed('uno   dos\n\ntres', 2, 0)).toEqual(['uno dos', 'tres']);
    expect(() => chunkFixed(diez, 4, 4)).toThrow(RangeError);
    expect(() => chunkFixed(diez, 0, 0)).toThrow(RangeError);
  });
});

describe('chunkRecursive', () => {
  it('fusiona párrafos completos mientras caben', () => {
    const texto = 'Primer párrafo corto.\n\nSegundo párrafo corto.\n\nTercero.';
    expect(chunkRecursive(texto, 50)).toEqual([
      'Primer párrafo corto.\n\nSegundo párrafo corto.',
      'Tercero.',
    ]);
  });

  it('corta a la fuerza una palabra más larga que el máximo', () => {
    expect(chunkRecursive('x'.repeat(25), 10)).toEqual([
      'x'.repeat(10),
      'x'.repeat(10),
      'x'.repeat(5),
    ]);
  });

  it('nunca supera el máximo y conserva las palabras', () => {
    const texto = 'Corto.\n\nuno dos tres cuatro cinco seis siete ocho nueve diez\n\nOtro corto.';
    const chunks = chunkRecursive(texto, 28);
    expect(chunks.every((c) => c.length <= 28)).toBe(true);
    expect(chunks.join(' ').split(/\s+/)).toEqual(texto.split(/\s+/));
  });
});

describe('chunkMarkdown', () => {
  it('rutas de encabezados y reinicio de niveles', () => {
    const doc = '# A\n\n## B\n\n### C\n\ntexto c\n\n## D\n\ntexto d\n\n# E\n\ntexto e';
    expect(chunkMarkdown(doc).map((c) => c.path)).toEqual(['A > B > C', 'A > D', 'E']);
  });

  it('las almohadillas de un bloque de código no son encabezados', () => {
    const chunks = chunkMarkdown('# Guía\n\n```python\n# comentario\n```\n\nFin.');
    expect(chunks).toHaveLength(1);
    expect(chunks[0].text).toContain('# comentario');
  });

  it('secciones vacías no generan fragmento', () => {
    expect(chunkMarkdown('# A\n\n## B\n\n## C\n\ntexto').map((c) => c.path)).toEqual(['A > C']);
  });
});
