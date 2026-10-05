import { useEffect, useMemo, useState } from 'react';
import { loadProgress } from '../../lib/progress';
import { INTERVAL_DAYS, boxCounts, dueQuestionIds, nextDue } from '../../lib/srs';
import Quiz from './Quiz';
import { useQuestionBank } from './useQuestionBank';

const SESSION_SIZE = 20;

const dateFmt = (iso: string) =>
  new Date(iso).toLocaleDateString('es-ES', {
    day: 'numeric',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit',
  });

export default function Review() {
  const { bank, error } = useQuestionBank();
  // Se lee una sola vez al montar: la sesión no debe cambiar mientras se responde.
  const [srs] = useState(() => loadProgress().srs);
  const [now] = useState(() => new Date());
  const [started, setStarted] = useState(false);

  const session = useMemo(() => {
    if (!bank) return [];
    const byId = new Map(bank.questions.map((q) => [q.id, q]));
    return dueQuestionIds(srs, now)
      .map((id) => byId.get(id))
      .filter((q) => q !== undefined)
      .slice(0, SESSION_SIZE);
  }, [bank, srs, now]);

  useEffect(() => setStarted(false), [bank]);

  if (error) return <p role="alert">No se pudieron cargar las preguntas: {error}</p>;
  if (!bank) return <p>Cargando preguntas…</p>;

  const counts = boxCounts(srs);
  const total = counts.reduce((a, b) => a + b, 0);
  const upcoming = nextDue(srs);

  return (
    <div className="space-y-6">
      <section aria-labelledby="cajas">
        <h2 id="cajas" className="text-lg font-semibold">
          Tus cajas Leitner
        </h2>
        <p className="mb-2 text-sm text-slate-600 dark:text-slate-400">
          Las preguntas que fallas entran en la caja 1 y vuelven al día siguiente. Cada acierto las
          sube una caja y las espacia más ({INTERVAL_DAYS.join(', ')} días). Un fallo las devuelve a
          la caja 1.
        </p>
        <ul className="grid grid-cols-5 gap-2 text-center">
          {counts.map((n, i) => (
            <li key={i} className="rounded-lg border border-slate-200 p-3 dark:border-slate-700">
              <p className="text-2xl font-bold">{n}</p>
              <p className="text-xs text-slate-500">
                Caja {i + 1} · {INTERVAL_DAYS[i]} d
              </p>
            </li>
          ))}
        </ul>
      </section>

      {session.length === 0 ? (
        <p role="status" className="rounded-lg border border-slate-200 p-4 dark:border-slate-700">
          {total === 0
            ? 'Todavía no tienes preguntas en repaso. Aparecerán aquí las que falles en los tests y exámenes.'
            : `No tienes nada pendiente ahora mismo. El próximo repaso es el ${dateFmt(upcoming!)}.`}
        </p>
      ) : !started ? (
        <div>
          <p className="mb-3" role="status">
            Tienes <strong>{session.length}</strong> pregunta{session.length === 1 ? '' : 's'}{' '}
            pendiente
            {session.length === 1 ? '' : 's'}
            {dueQuestionIds(srs, now).length > SESSION_SIZE ? ` (sesiones de ${SESSION_SIZE})` : ''}
            .
          </p>
          <button
            type="button"
            onClick={() => setStarted(true)}
            className="rounded-md bg-indigo-600 px-5 py-2.5 font-medium text-white hover:bg-indigo-700"
          >
            Empezar repaso
          </button>
        </div>
      ) : (
        <Quiz quizId="review" title="Repaso espaciado" questions={session} mode="review" />
      )}
    </div>
  );
}
