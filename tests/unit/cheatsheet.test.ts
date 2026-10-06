import { describe, expect, it } from 'vitest';
import { extractTakeaways, plainInline } from '../../src/lib/cheatsheet';

describe('extractTakeaways', () => {
  it('devuelve los puntos de la lista del bloque', () => {
    const body = `texto\n\n<KeyTakeaways>\n\n- Primero con **negrita**.\n- Segundo.\n\n</KeyTakeaways>\n\nfin`;
    expect(extractTakeaways(body)).toEqual(['Primero con **negrita**.', 'Segundo.']);
  });

  it('devuelve una lista vacía si no hay bloque y soporta saltos de línea de Windows', () => {
    expect(extractTakeaways('sin bloque')).toEqual([]);
    expect(extractTakeaways('<KeyTakeaways>\r\n\r\n- Uno\r\n\r\n</KeyTakeaways>')).toEqual(['Uno']);
  });
});

describe('plainInline', () => {
  it('quita negritas, cursivas, código y fórmulas en línea', () => {
    expect(plainInline('**pass@k** mide `capacidad` y _crece_ con $k$')).toBe(
      'pass@k mide capacidad y crece con k',
    );
  });

  it('no rompe una multiplicación con asteriscos aislados', () => {
    expect(plainInline('2 * 3 y 4 * 5')).toBe('2 * 3 y 4 * 5');
  });
});
