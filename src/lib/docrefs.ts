/** Detección de referencias a documentos del corpus de ejemplo (`doc-001`...) dentro de un texto. */

const DOC_REF = /\bdoc-\d{3}\b/g;

export type Piece = { text: string; docId?: string };

/** ¿Contiene el texto alguna referencia con forma de `doc-NNN`? (comprobación barata previa). */
export const hasDocRef = (text: string): boolean => /\bdoc-\d{3}\b/.test(text);

/**
 * Parte un texto en trozos: las referencias a documentos que existen (`known`) llevan `docId`;
 * el resto, incluidas las inventadas a propósito en los ejemplos (`doc-099`), se dejan como texto.
 */
export function splitDocRefs(text: string, known: ReadonlySet<string>): Piece[] {
  const pieces: Piece[] = [];
  let last = 0;
  for (const m of text.matchAll(DOC_REF)) {
    if (!known.has(m[0])) continue;
    const start = m.index ?? 0;
    if (start > last) pieces.push({ text: text.slice(last, start) });
    pieces.push({ text: m[0], docId: m[0] });
    last = start + m[0].length;
  }
  if (last < text.length) pieces.push({ text: text.slice(last) });
  return pieces;
}
