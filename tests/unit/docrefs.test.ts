import { describe, expect, it } from 'vitest';
import { hasDocRef, splitDocRefs } from '../../src/lib/docrefs';

const known = new Set(['doc-001', 'doc-002']);

describe('splitDocRefs', () => {
  it('separa las referencias que existen y deja el resto del texto intacto', () => {
    const pieces = splitDocRefs('Ver [doc-001] y también doc-002, no doc-099.', known);
    expect(pieces.map((p) => p.text).join('')).toBe('Ver [doc-001] y también doc-002, no doc-099.');
    expect(pieces.filter((p) => p.docId).map((p) => p.docId)).toEqual(['doc-001', 'doc-002']);
  });

  it('ignora referencias a documentos que no existen (ejemplos inventados)', () => {
    expect(splitDocRefs('cita a doc-099', known)).toEqual([{ text: 'cita a doc-099' }]);
  });

  it('no confunde identificadores más largos o pegados a otras letras', () => {
    expect(splitDocRefs('doc-0011 y xdoc-001', known).some((p) => p.docId)).toBe(false);
  });

  it('un texto sin referencias o vacío queda igual', () => {
    expect(splitDocRefs('', known)).toEqual([]);
    expect(splitDocRefs('nada', known)).toEqual([{ text: 'nada' }]);
  });

  it('hasDocRef es una comprobación previa barata', () => {
    expect(hasDocRef('mira doc-007')).toBe(true);
    expect(hasDocRef('documento 7')).toBe(false);
  });
});
