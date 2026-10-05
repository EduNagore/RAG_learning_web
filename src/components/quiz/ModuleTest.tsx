import { useState } from 'react';
import { buildExam, type RenderedQuestion } from '../../lib/quiz';
import Quiz from './Quiz';

const QUICK = 20;

interface Props {
  moduleId: string;
  title: string;
  questions: RenderedQuestion[];
}

export default function ModuleTest({ moduleId, title, questions }: Props) {
  const [session, setSession] = useState<RenderedQuestion[] | null>(null);
  const [run, setRun] = useState(0);

  const start = (full: boolean) => {
    if (full || questions.length <= QUICK) {
      setSession(questions);
    } else {
      // Muestra repartida entre las lecciones del módulo (buildExam agrupa por `moduleId`).
      const byId = new Map(questions.map((q) => [q.id, q]));
      const lessonIds = [...new Set(questions.map((q) => q.lessonId))];
      const picked = buildExam(
        questions.map((q) => ({ id: q.id, moduleId: q.lessonId })),
        { moduleIds: lessonIds, count: QUICK, seed: Math.floor(Math.random() * 2 ** 31) },
      );
      setSession(picked.map((p) => byId.get(p.id)!));
    }
    setRun((r) => r + 1);
  };

  if (questions.length === 0) {
    return <p>Este módulo todavía no tiene preguntas.</p>;
  }

  if (!session) {
    return (
      <div className="space-y-3">
        <p>
          Este test tiene <strong>{questions.length}</strong> preguntas de todas las lecciones del
          módulo. Apruebas con un 80 % o más.
        </p>
        <div className="flex flex-wrap gap-3">
          {questions.length > QUICK && (
            <button
              type="button"
              onClick={() => start(false)}
              className="rounded-md bg-indigo-600 px-5 py-2.5 font-medium text-white hover:bg-indigo-700"
            >
              Test rápido ({QUICK} preguntas)
            </button>
          )}
          <button
            type="button"
            onClick={() => start(true)}
            className="rounded-md border border-slate-300 px-5 py-2.5 font-medium hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800"
          >
            Test completo ({questions.length})
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <Quiz key={run} quizId={`module:${moduleId}`} title={`Test: ${title}`} questions={session} />
      <button
        type="button"
        onClick={() => setSession(null)}
        className="mt-4 text-sm text-indigo-700 hover:underline dark:text-indigo-300"
      >
        ← Elegir otro tipo de test
      </button>
    </div>
  );
}
