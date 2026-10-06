import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

export const PARTS = ['fundamentos', 'rag', 'agentes', 'profesional'] as const;

const modules = defineCollection({
  loader: glob({ pattern: '*.yaml', base: './src/content/modules' }),
  schema: z.object({
    part: z.enum(PARTS),
    order: z.number().int(),
    title: z.string(),
    description: z.string(),
    objectives: z.array(z.string()).min(1),
  }),
});

const source = z.object({
  title: z.string(),
  url: z.url(),
  type: z.enum(['paper', 'docs', 'blog', 'spec', 'book', 'video']),
  authors: z.string().optional(),
  year: z.number().int().min(1990).max(2100),
});

const lessons = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/lessons' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    module: z.string(),
    order: z.number().int(),
    level: z.enum(['básico', 'intermedio', 'avanzado']),
    estimatedMinutes: z.number().int().positive(),
    objectives: z.array(z.string()).min(3).max(5),
    prerequisites: z.array(z.string()).optional(),
    volatility: z.enum(['low', 'medium', 'high']),
    lastReviewed: z.coerce.date(),
    sources: z.array(source).min(2),
    relatedLabs: z.array(z.string()).optional(),
  }),
});

const question = z
  .object({
    id: z.string(),
    type: z.enum(['single', 'multiple', 'truefalse', 'order', 'code-output']),
    difficulty: z.number().int().min(1).max(3),
    prompt: z.string(),
    code: z.string().optional(),
    options: z.array(z.string()).optional(),
    // single/multiple/code-output: índices correctos. truefalse: [0] = verdadero, [1] = falso.
    // order: se omite; `options` ya está en el orden correcto.
    answer: z.array(z.number().int().min(0)).optional(),
    explanation: z.string(),
    ref: z.string().optional(),
  })
  .superRefine((q, ctx) => {
    const issue = (message: string) =>
      ctx.addIssue({ code: 'custom', message: `${q.id}: ${message}` });
    const n = q.options?.length ?? 0;
    if (q.type === 'truefalse') {
      if (q.answer?.length !== 1 || ![0, 1].includes(q.answer[0]))
        issue('truefalse requiere answer [0] o [1]');
      return;
    }
    if (n < 2) issue('requiere al menos 2 options');
    if (q.type === 'order') {
      if (q.answer) issue('order no lleva answer (options ya está en orden correcto)');
      return;
    }
    if (!q.answer?.length) return issue('falta answer');
    if (q.answer.some((i) => i >= n)) issue('answer fuera de rango de options');
    if (new Set(q.answer).size !== q.answer.length) issue('answer con índices repetidos');
    if (q.type !== 'multiple' && q.answer.length !== 1)
      issue(`${q.type} requiere una única respuesta`);
    if (q.type === 'code-output' && !q.code) issue('code-output requiere code');
  });

const quizzes = defineCollection({
  loader: glob({ pattern: '**/*.yaml', base: './src/content/quizzes' }),
  schema: z.object({
    lesson: z.string(),
    questions: z.array(question).min(1),
  }),
});

const labs = defineCollection({
  // Un laboratorio por carpeta: src/content/labs/<id>/index.mdx (+ starter.py, solution.py, test_lab.py).
  loader: glob({
    pattern: '*/index.mdx',
    base: './src/content/labs',
    generateId: ({ entry }) => entry.split('/')[0],
  }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    part: z.enum(['fundamentos', 'rag', 'agentes']),
    module: z.string(),
    difficulty: z.union([z.literal(1), z.literal(2), z.literal(3)]),
    estimatedMinutes: z.number().int().positive(),
    concepts: z.array(z.string()).min(1),
    /** Paquetes de Pyodide que hay que cargar además de numpy (p. ej. 'networkx'). */
    packages: z.array(z.string()).default([]),
    hints: z.array(z.string()).min(1),
    relatedLessons: z.array(z.string()).default([]),
  }),
});

const langPair = z.object({ q: z.string().min(10), a: z.string().min(40) });

const interview = defineCollection({
  // Un fichero por tema: src/content/interview/<tema>.yaml con preguntas en español y en inglés.
  loader: glob({ pattern: '*.yaml', base: './src/content/interview' }),
  schema: z.object({
    title: z.string(),
    order: z.number().int(),
    questions: z
      .array(
        z.object({
          id: z.string(),
          level: z.enum(['junior', 'mid', 'senior']),
          kind: z.enum(['conceptual', 'design', 'debug']),
          es: langPair,
          en: langPair,
          /** Lecciones donde se explica el tema (ids de la colección lessons). */
          lessons: z.array(z.string()).default([]),
        }),
      )
      .min(1),
  }),
});

const cases = defineCollection({
  // Casos de system design: src/content/cases/<id>.mdx, servidos en /entrevistas/system-design/<id>/.
  loader: glob({ pattern: '*.mdx', base: './src/content/cases' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    order: z.number().int(),
    level: z.enum(['mid', 'senior']),
    estimatedMinutes: z.number().int().positive(),
    lessons: z.array(z.string()).default([]),
    lastReviewed: z.coerce.date(),
  }),
});

const glossary = defineCollection({
  loader: glob({ pattern: '*.yaml', base: './src/content/glossary' }),
  schema: z.object({
    terms: z
      .array(
        z.object({
          id: z.string(),
          es: z.string(),
          en: z.string(),
          def: z.string().min(30),
          /** Lecciones donde se explica el término. */
          lessons: z.array(z.string()).default([]),
        }),
      )
      .min(1),
  }),
});

const projects = defineCollection({
  // Guía de cada proyecto final: src/content/projects/<id>.mdx; el código inicial vive en projects/<id>/.
  loader: glob({ pattern: '*.mdx', base: './src/content/projects' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    order: z.number().int(),
    level: z.enum(['intermedio', 'avanzado']),
    estimatedHours: z.number().positive(),
    stack: z.array(z.string()).min(1),
    lessons: z.array(z.string()).default([]),
    /** Fecha en que se comprobaron las versiones y las APIs contra la documentación vigente. */
    verified: z.coerce.date(),
  }),
});

export const collections = {
  modules,
  lessons,
  quizzes,
  labs,
  interview,
  cases,
  glossary,
  projects,
};
