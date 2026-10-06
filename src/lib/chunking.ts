/** Troceado de texto con la misma semántica que las soluciones de Python de los laboratorios. */

export function chunkFixed(text: string, size: number, overlap: number): string[] {
  if (size <= 0 || overlap < 0 || overlap >= size) {
    throw new RangeError('size debe ser positivo y overlap debe cumplir 0 <= overlap < size');
  }
  const words = text.split(/\s+/).filter(Boolean);
  const step = size - overlap;
  const chunks: string[] = [];
  for (let start = 0; start < words.length; start += step) {
    chunks.push(words.slice(start, start + size).join(' '));
    if (start + size >= words.length) break; // esta ventana ya llega al final
  }
  return chunks;
}

export function chunkRecursive(
  text: string,
  maxChars: number,
  separators: readonly string[] = ['\n\n', '\n', ' '],
): string[] {
  text = text.trim();
  if (!text) return [];
  if (text.length <= maxChars) return [text];

  for (let i = 0; i < separators.length; i++) {
    const sep = separators[i];
    if (!text.includes(sep)) continue;
    const remaining = separators.slice(i + 1);
    const pieces = text
      .split(sep)
      .map((p) => p.trim())
      .filter(Boolean);
    const chunks: string[] = [];
    let current = '';
    for (const piece of pieces) {
      if (piece.length > maxChars) {
        if (current) {
          chunks.push(current);
          current = '';
        }
        chunks.push(...chunkRecursive(piece, maxChars, remaining));
        continue;
      }
      const candidate = current ? current + sep + piece : piece;
      if (candidate.length <= maxChars) current = candidate;
      else {
        chunks.push(current);
        current = piece;
      }
    }
    if (current) chunks.push(current);
    return chunks;
  }

  const hard: string[] = [];
  for (let i = 0; i < text.length; i += maxChars) hard.push(text.slice(i, i + maxChars));
  return hard;
}

export interface SectionChunk {
  text: string;
  headers: string[];
  path: string;
}

/** Troceado por encabezados Markdown: un fragmento por sección con su ruta de títulos. */
export function chunkMarkdown(text: string, maxChars = 500): SectionChunk[] {
  const result: SectionChunk[] = [];
  let headers: string[] = [];
  let buffer: string[] = [];
  let inCode = false;

  const flush = () => {
    const body = buffer.join('\n').trim();
    buffer = [];
    if (!body) return;
    for (const piece of chunkRecursive(body, maxChars, ['\n\n', '\n', ' '])) {
      result.push({ text: piece, headers: [...headers], path: headers.join(' > ') });
    }
  };

  for (const line of text.split(/\r?\n/)) {
    if (line.trimStart().startsWith('```')) {
      inCode = !inCode;
      buffer.push(line);
      continue;
    }
    const match = inCode ? null : /^(#{1,6}) +(.+?)\s*$/.exec(line);
    if (match) {
      flush();
      headers = [...headers.slice(0, match[1].length - 1), match[2]];
    } else buffer.push(line);
  }
  flush();
  return result;
}
