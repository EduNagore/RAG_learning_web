/** Acceso a las preguntas en build: lee los YAML, renderiza el Markdown y añade el origen. */
import { getCollection } from 'astro:content';
import { Marked } from 'marked';
import type { QuestionBank, RenderedQuestion } from './quiz';
import { getModules, getOrderedLessons } from './content';

const escapeHtml = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

// El HTML crudo del Markdown se escapa: así `<documents>` en una pregunta se ve literal
// en lugar de interpretarse como una etiqueta.
const md = new Marked({ renderer: { html: ({ text }) => escapeHtml(text) } });
const inline = (s: string) => md.parseInline(s, { async: false });
const block = (s: string) => md.parse(s, { async: false });

/** Todas las preguntas, en orden de lectura (módulo, lección, orden del YAML). */
export async function getRenderedQuestions(): Promise<RenderedQuestion[]> {
  const [lessons, quizzes] = await Promise.all([getOrderedLessons(), getCollection('quizzes')]);
  const quizByLesson = new Map(quizzes.map((q) => [q.data.lesson, q.data]));

  return lessons.flatMap((lesson) =>
    (quizByLesson.get(lesson.id)?.questions ?? []).map((q): RenderedQuestion => ({
      ...q,
      promptHtml: block(q.prompt),
      explanationHtml: block(q.explanation),
      optionsHtml: q.options?.map(inline),
      lessonId: lesson.id,
      moduleId: lesson.data.module,
    })),
  );
}

export async function getQuestionsByLesson(lessonId: string): Promise<RenderedQuestion[]> {
  return (await getRenderedQuestions()).filter((q) => q.lessonId === lessonId);
}

/** Banco completo con los metadatos necesarios para informes y enlaces. */
export async function getQuestionBank(): Promise<QuestionBank> {
  const [questions, lessons, modules] = await Promise.all([
    getRenderedQuestions(),
    getOrderedLessons(),
    getModules(),
  ]);
  const withQuestions = new Set(questions.map((q) => q.moduleId));
  return {
    questions,
    lessons: Object.fromEntries(
      lessons.map((l) => [l.id, { title: l.data.title, moduleId: l.data.module }]),
    ),
    modules: Object.fromEntries(
      modules
        .filter((m) => withQuestions.has(m.id))
        .map((m) => [m.id, { title: m.data.title, part: m.data.part, order: m.data.order }]),
    ),
  };
}
