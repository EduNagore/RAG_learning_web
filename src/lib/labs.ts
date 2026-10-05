/** Acceso en build a los laboratorios: metadatos (colección) y archivos Python hermanos. */
import { getCollection, type CollectionEntry } from 'astro:content';

export type Lab = CollectionEntry<'labs'>;

export const PART_NAMES = { fundamentos: 'Fundamentos', rag: 'RAG', agentes: 'Agentes' } as const;
export const DIFFICULTY_NAMES = { 1: 'Básico', 2: 'Intermedio', 3: 'Avanzado' } as const;

// Los .py se importan como texto en build (no se publican como rutas: van dentro de la página).
const sources = import.meta.glob<string>('/src/content/labs/*/*.py', {
  query: '?raw',
  import: 'default',
  eager: true,
});

export interface LabFiles {
  starter: string;
  solution: string;
  tests: string;
}

export function getLabFiles(id: string): LabFiles {
  const read = (name: string) => {
    const content = sources[`/src/content/labs/${id}/${name}`];
    if (content === undefined) throw new Error(`Falta ${name} en el laboratorio ${id}`);
    return content;
  };
  return { starter: read('starter.py'), solution: read('solution.py'), tests: read('test_lab.py') };
}

/** Laboratorios ordenados por dificultad y después por id (que lleva el número del plan). */
export async function getLabs(): Promise<Lab[]> {
  return (await getCollection('labs')).sort(
    (a, b) => a.data.difficulty - b.data.difficulty || a.id.localeCompare(b.id),
  );
}
