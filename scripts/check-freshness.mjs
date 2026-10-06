/**
 * Lista las lecciones cuya revisión está vencida: `lastReviewed` con más de 6 meses, o con más de
 * 3 meses si la lección es de volatilidad alta (frameworks, protocolos, cifras de proveedores).
 *
 * Uso: node scripts/check-freshness.mjs [--now=AAAA-MM-DD] [--out=freshness.md]
 * Siempre termina con código 0: el informe es un aviso, no un fallo de CI.
 */
import { readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join, relative, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parse as parseYaml } from 'yaml';

export const MAX_AGE_DAYS = 183; // ≈ 6 meses
export const MAX_AGE_DAYS_HIGH_VOLATILITY = 92; // ≈ 3 meses
const DAY = 86_400_000;

/** @param {{id: string, lastReviewed: string|Date, volatility: string}[]} lessons */
export function findStale(lessons, now) {
  return lessons
    .map((l) => {
      const reviewed = new Date(l.lastReviewed);
      const ageDays = Math.floor((now.getTime() - reviewed.getTime()) / DAY);
      const limit = l.volatility === 'high' ? MAX_AGE_DAYS_HIGH_VOLATILITY : MAX_AGE_DAYS;
      return { ...l, ageDays, limit };
    })
    .filter((l) => l.ageDays > l.limit)
    .sort((a, b) => b.ageDays - a.ageDays || a.id.localeCompare(b.id));
}

export function formatReport(stale, total, now) {
  const date = now.toISOString().slice(0, 10);
  if (stale.length === 0) {
    return `## Frescura del contenido (${date})\n\nLas ${total} lecciones están dentro de su plazo de revisión.\n`;
  }
  const rows = stale.map(
    (l) =>
      `| \`${l.id}\` | ${l.volatility} | ${String(l.lastReviewed).slice(0, 10)} | ${l.ageDays} días (límite ${l.limit}) |`,
  );
  return [
    `## Frescura del contenido (${date})`,
    '',
    `${stale.length} de ${total} lecciones necesitan revisión. Plazos: 6 meses en general y 3 meses si la volatilidad es alta.`,
    '',
    '| Lección | Volatilidad | Última revisión | Antigüedad |',
    '| ------- | ----------- | --------------- | ---------- |',
    ...rows,
    '',
    'Al revisar una lección: abre sus fuentes, comprueba las cifras y los bloques `<Snapshot>`, y actualiza `lastReviewed`.',
    '',
  ].join('\n');
}

function walk(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory() ? walk(join(dir, e.name)) : e.name.endsWith('.mdx') ? [join(dir, e.name)] : [],
  );
}

function loadLessons(root) {
  return walk(root).map((file) => {
    const text = readFileSync(file, 'utf8');
    const match = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
    const fm = parseYaml(match[1]);
    return {
      id: relative(root, file)
        .split(sep)
        .join('/')
        .replace(/\.mdx$/, ''),
      lastReviewed: fm.lastReviewed,
      volatility: fm.volatility,
    };
  });
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const arg = (name) => process.argv.find((a) => a.startsWith(`--${name}=`))?.split('=')[1];
  const now = arg('now') ? new Date(arg('now')) : new Date();
  const root = fileURLToPath(new URL('../src/content/lessons', import.meta.url));
  const lessons = loadLessons(root);
  const report = formatReport(findStale(lessons, now), lessons.length, now);
  console.log(report);
  if (arg('out')) writeFileSync(arg('out'), report, 'utf8');
}
