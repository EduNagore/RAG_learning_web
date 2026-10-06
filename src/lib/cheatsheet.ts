/** Extrae los puntos del bloque <KeyTakeaways> de una lección (MDX en bruto). */
export function extractTakeaways(body: string): string[] {
  const match = body.match(/<KeyTakeaways>([\s\S]*?)<\/KeyTakeaways>/);
  if (!match) return [];
  return match[1]
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => /^[-*]\s+/.test(line))
    .map((line) => line.replace(/^[-*]\s+/, ''));
}

/** Pasa el Markdown en línea a texto plano (negritas, cursivas y código) para la hoja imprimible. */
export function plainInline(markdown: string): string {
  return markdown
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/(?<![\w*])\*(?!\s)(.+?)\*(?!\w)/g, '$1')
    .replace(/_(.+?)_/g, '$1')
    .replace(/`(.+?)`/g, '$1')
    .replace(/\$(.+?)\$/g, '$1');
}
