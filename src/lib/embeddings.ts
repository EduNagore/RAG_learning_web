/**
 * Port a TypeScript de ragkit.text y ragkit.embeddings.HashingEmbedder.
 * Debe producir exactamente los mismos vectores que la versión de Python (hay un test que lo comprueba).
 */

const STOPWORDS_ES_RAW = `
a al algo ante antes aqui como con cual cuando de del desde donde el ella ellas ellos en entre era
es esa ese eso esta estan este esto fue ha han hasta hay la las le les lo los mas me mi mis mucho
muy ni no nos nosotros o otro para pero poco por porque que quien se sea ser si sin sobre su sus
tambien te tengo tiene todo tu tus un una uno unos y ya yo
`;

/** Quita los acentos pero conserva la ñ (la tilde combinada U+0303). */
export function stripAccents(text: string): string {
  const out: string[] = [];
  for (const ch of text.normalize('NFD')) {
    if (/\p{Mn}/u.test(ch) && ch !== '̃') continue;
    out.push(ch);
  }
  return out.join('').normalize('NFC');
}

export const normalize = (text: string) => stripAccents(text.toLowerCase());

const STOPWORDS_ES = new Set(normalize(STOPWORDS_ES_RAW).split(/\s+/).filter(Boolean));

export function tokenize(text: string, removeStopwords = true): string[] {
  const tokens = normalize(text).match(/[a-zñ0-9]+/g) ?? [];
  return removeStopwords ? tokens.filter((t) => !STOPWORDS_ES.has(t)) : tokens;
}

// CRC-32 (el mismo de zlib.crc32).
const CRC_TABLE = (() => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    table[n] = c >>> 0;
  }
  return table;
})();

export function crc32(text: string): number {
  let crc = 0xffffffff;
  for (const byte of new TextEncoder().encode(text)) crc = CRC_TABLE[(crc ^ byte) & 0xff] ^ (crc >>> 8);
  return (crc ^ 0xffffffff) >>> 0;
}

export class HashingEmbedder {
  constructor(
    readonly dim = 256,
    readonly useBigrams = true,
  ) {}

  embed(text: string): number[] {
    const tokens = tokenize(text);
    const features = [...tokens];
    if (this.useBigrams) for (let i = 0; i + 1 < tokens.length; i++) features.push(`${tokens[i]}_${tokens[i + 1]}`);

    const vec = new Array<number>(this.dim).fill(0);
    for (const feature of features) {
      const h = crc32(feature);
      vec[h % this.dim] += (h >>> 16) & 1 ? 1 : -1;
    }
    const norm = Math.hypot(...vec);
    return norm > 0 ? vec.map((v) => v / norm) : vec;
  }
}

export const dot = (a: number[], b: number[]) => a.reduce((s, v, i) => s + v * b[i], 0);

/** Coseno de dos vectores ya normalizados (o 0 si alguno es el vector cero). */
export function cosine(a: number[], b: number[]): number {
  const na = Math.hypot(...a);
  const nb = Math.hypot(...b);
  return na === 0 || nb === 0 ? 0 : dot(a, b) / (na * nb);
}
