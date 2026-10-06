export interface FusedDoc {
  id: string;
  score: number;
  /** Posición (desde 1) en cada ranking, o null si no aparece. */
  ranks: (number | null)[];
  /** Contribución 1 / (k + posición) de cada ranking. */
  parts: number[];
}

/** Reciprocal Rank Fusion (Cormack, Clarke y Büttcher, 2009). Empate: primera aparición. */
export function rrfFuse(rankings: string[][], k: number): FusedDoc[] {
  const docs = new Map<string, FusedDoc>();
  for (const [r, ranking] of rankings.entries()) {
    const seen = new Set<string>();
    for (const [i, id] of ranking.entries()) {
      let doc = docs.get(id);
      if (!doc) {
        doc = {
          id,
          score: 0,
          ranks: rankings.map(() => null),
          parts: rankings.map(() => 0),
        };
        docs.set(id, doc);
      }
      if (seen.has(id)) continue;
      seen.add(id);
      const part = 1 / (k + i + 1);
      doc.ranks[r] = i + 1;
      doc.parts[r] = part;
      doc.score += part;
    }
  }
  const order = [...docs.keys()];
  return [...docs.values()].sort(
    (a, b) => b.score - a.score || order.indexOf(a.id) - order.indexOf(b.id),
  );
}

/** Convierte "a, b, c" o un id por línea en una lista limpia. */
export function parseRanking(text: string): string[] {
  return text
    .split(/[\n,]/)
    .map((s) => s.trim())
    .filter(Boolean);
}
