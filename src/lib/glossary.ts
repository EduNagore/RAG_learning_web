export interface GlossaryTerm {
  id: string;
  es: string;
  en: string;
  def: string;
  lessons: { id: string; title: string; href: string }[];
}

/** Quita acentos y pasa a minúsculas para que «recuperacion» encuentre «recuperación». */
export function normalize(text: string): string {
  return text.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
}

export function filterTerms(terms: GlossaryTerm[], query: string): GlossaryTerm[] {
  const q = normalize(query.trim());
  if (!q) return terms;
  return terms.filter((t) => normalize(`${t.es} ${t.en} ${t.def}`).includes(q));
}
