import { getCollection, type CollectionEntry } from 'astro:content';
import { url } from './url';

export type Lesson = CollectionEntry<'lessons'>;
export type Module = CollectionEntry<'modules'>;

export const PART_LABELS: Record<Module['data']['part'], string> = {
  fundamentos: 'Parte 0 · Fundamentos',
  rag: 'Parte I · RAG',
  agentes: 'Parte II · Agentes y multi-agentes',
  profesional: 'Parte III · Preparación profesional',
};

export async function getModules(): Promise<Module[]> {
  return (await getCollection('modules')).sort((a, b) => a.data.order - b.data.order);
}

/** Lecciones agrupadas por id de módulo, ordenadas por `order`. */
export async function getLessonsByModule(): Promise<Map<string, Lesson[]>> {
  const map = new Map<string, Lesson[]>();
  for (const lesson of await getCollection('lessons')) {
    const list = map.get(lesson.data.module) ?? [];
    list.push(lesson);
    map.set(lesson.data.module, list);
  }
  for (const list of map.values()) list.sort((a, b) => a.data.order - b.data.order);
  return map;
}

/** Todas las lecciones en orden de lectura (módulo, luego lección). */
export async function getOrderedLessons(): Promise<Lesson[]> {
  const [modules, byModule] = await Promise.all([getModules(), getLessonsByModule()]);
  return modules.flatMap((m) => byModule.get(m.id) ?? []);
}

export const lessonHref = (lesson: Lesson) => url(`/teoria/${lesson.id}/`);

/** Agrupa módulos por parte manteniendo el orden. */
export function groupByPart(modules: Module[]): [Module['data']['part'], Module[]][] {
  const parts = new Map<Module['data']['part'], Module[]>();
  for (const m of modules) parts.set(m.data.part, [...(parts.get(m.data.part) ?? []), m]);
  return [...parts.entries()];
}
