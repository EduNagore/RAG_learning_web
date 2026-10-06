import { getCollection } from 'astro:content';
import type { InterviewQuestion } from '../components/interview/InterviewBrowser';
import { url } from './url';

/** Todas las preguntas de entrevista, ordenadas por tema y con las lecciones enlazadas resueltas. */
export async function getInterviewQuestions(): Promise<InterviewQuestion[]> {
  const [topics, lessons] = await Promise.all([
    getCollection('interview'),
    getCollection('lessons'),
  ]);
  const lessonById = new Map(lessons.map((l) => [l.id, l]));
  return topics
    .sort((a, b) => a.data.order - b.data.order)
    .flatMap((topic) =>
      topic.data.questions.map((q) => ({
        id: q.id,
        topic: topic.id,
        topicTitle: topic.data.title,
        level: q.level,
        kind: q.kind,
        es: q.es,
        en: q.en,
        lessons: q.lessons.flatMap((id) => {
          const lesson = lessonById.get(id);
          return lesson ? [{ id, title: lesson.data.title, href: url(`/teoria/${id}/`) }] : [];
        }),
      })),
    );
}

export async function getCases() {
  return (await getCollection('cases')).sort((a, b) => a.data.order - b.data.order);
}

export const caseHref = (id: string) => url(`/entrevistas/system-design/${id}/`);
