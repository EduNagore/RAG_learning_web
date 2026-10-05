import { useEffect, useMemo, useRef, useState } from 'react';
import {
  PASS_THRESHOLD,
  isCorrect,
  passed,
  presentationOrder,
  questionSeed,
  scorePct,
  type RenderedQuestion,
  type Response,
} from '../../lib/quiz';
import { recordQuizOutcome, recordReview } from '../../lib/progress';
import QuestionView, { refHref } from './QuestionView';

export interface QuizResultItem {
  id: string;
  correct: boolean;
}

interface Props {
  /** Id con el que se guarda la nota: id de lección o "module:<id>". */
  quizId: string;
  title: string;
  questions: RenderedQuestion[];
  /**
   * `test` guarda la nota al terminar. `review` es el repaso espaciado: registra cada
   * respuesta al instante en las cajas de Leitner y no toca las notas de los tests.
   */
  mode?: 'test' | 'review';
  /** Se llama una vez al terminar con el resultado de cada pregunta. */
  onFinish?: (results: QuizResultItem[]) => void;
}

const newSeed = () => Math.floor(Math.random() * 2 ** 31);

export default function Quiz({ quizId, title, questions, mode = 'test', onFinish }: Props) {
  const [seed, setSeed] = useState(newSeed);
  const [idx, setIdx] = useState(0);
  const [responses, setResponses] = useState<Record<string, Response>>({});
  const [checked, setChecked] = useState<Record<string, boolean>>({});
  const [finished, setFinished] = useState(false);
  const headingRef = useRef<HTMLHeadingElement>(null);
  const firstRender = useRef(true);

  const orders = useMemo(
    () =>
      Object.fromEntries(
        questions.map((q) => [q.id, presentationOrder(q, questionSeed(seed, q.id))]),
      ),
    [questions, seed],
  );

  // Al cambiar de pregunta o de pantalla, el foco vuelve al encabezado (teclado y lectores).
  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false;
      return;
    }
    headingRef.current?.focus();
  }, [idx, finished]);

  if (questions.length === 0) {
    return (
      <p className="text-slate-600 dark:text-slate-400">Aún no hay preguntas para este test.</p>
    );
  }

  const q = questions[idx];
  const order = orders[q.id];
  const response = responses[q.id] ?? (q.type === 'order' ? order : []);
  const isChecked = !!checked[q.id];
  const canCheck = q.type === 'order' || response.length > 0;
  const isLast = idx === questions.length - 1;

  const results = (): QuizResultItem[] =>
    questions.map((x) => ({
      id: x.id,
      correct: isCorrect(x, responses[x.id] ?? (x.type === 'order' ? orders[x.id] : [])),
    }));

  const check = () => {
    setChecked((c) => ({ ...c, [q.id]: true }));
    if (mode === 'review') recordReview([{ id: q.id, correct: isCorrect(q, response) }]);
  };

  const next = () => {
    if (!isLast) return setIdx(idx + 1);
    const final = results();
    if (mode === 'test') recordQuizOutcome({ quizId, results: final });
    onFinish?.(final);
    setFinished(true);
  };

  const restart = () => {
    setSeed(newSeed());
    setIdx(0);
    setResponses({});
    setChecked({});
    setFinished(false);
  };

  if (finished) {
    const final = results();
    const pct = scorePct(final);
    const failed = questions.filter((_q, i) => !final[i].correct);
    const ok = passed(pct);
    return (
      <section
        aria-labelledby={`${quizId}-result`}
        className="rounded-xl border border-slate-200 p-5 dark:border-slate-800"
      >
        <h2
          id={`${quizId}-result`}
          ref={headingRef}
          tabIndex={-1}
          className="text-xl font-semibold outline-none"
        >
          Resultado: {pct} %
        </h2>
        <p className="mt-1" role="status">
          {final.filter((r) => r.correct).length} de {final.length} correctas.{' '}
          {mode === 'review'
            ? 'Las que has fallado vuelven mañana a la caja 1.'
            : ok
              ? `Aprobado (mínimo ${PASS_THRESHOLD} %).`
              : `Todavía no llegas al ${PASS_THRESHOLD} %: repasa las preguntas falladas y vuelve a intentarlo.`}
        </p>

        {failed.length > 0 && (
          <div className="mt-4 space-y-4">
            <h3 className="font-semibold">A repasar ({failed.length})</h3>
            {failed.map((x) => (
              <div
                key={x.id}
                className="rounded-lg border border-slate-200 p-3 dark:border-slate-700"
              >
                <div
                  className="prose prose-sm prose-slate max-w-none font-medium dark:prose-invert"
                  dangerouslySetInnerHTML={{ __html: x.promptHtml }}
                />
                <div
                  className="prose prose-sm prose-slate mt-2 max-w-none dark:prose-invert"
                  dangerouslySetInnerHTML={{ __html: x.explanationHtml }}
                />
                <a
                  className="mt-1 inline-block text-sm font-medium text-indigo-700 hover:underline dark:text-indigo-300"
                  href={refHref(x)}
                >
                  Repasar en la lección →
                </a>
              </div>
            ))}
          </div>
        )}

        <button
          type="button"
          onClick={restart}
          className="mt-5 rounded-md bg-indigo-600 px-4 py-2 font-medium text-white hover:bg-indigo-700"
        >
          Repetir el test
        </button>
      </section>
    );
  }

  return (
    <section
      aria-labelledby={`${quizId}-title`}
      className="rounded-xl border border-slate-200 p-5 dark:border-slate-800"
    >
      <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2">
        <h2
          id={`${quizId}-title`}
          ref={headingRef}
          tabIndex={-1}
          className="text-xl font-semibold outline-none"
        >
          {title}
        </h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Pregunta {idx + 1} de {questions.length}
        </p>
      </div>
      <div
        className="mb-4 h-1.5 overflow-hidden rounded bg-slate-200 dark:bg-slate-800"
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={questions.length}
        aria-valuenow={idx + 1}
        aria-label="Progreso del test"
      >
        <div
          className="h-full bg-indigo-500"
          style={{ width: `${((idx + 1) / questions.length) * 100}%` }}
        />
      </div>

      <QuestionView
        key={q.id + seed}
        question={q}
        order={order}
        response={response}
        onChange={(r) => setResponses((s) => ({ ...s, [q.id]: r }))}
        checked={isChecked}
      />

      <div className="mt-4 flex justify-end gap-2">
        {!isChecked ? (
          <button
            type="button"
            onClick={check}
            disabled={!canCheck}
            className="rounded-md bg-indigo-600 px-4 py-2 font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Comprobar
          </button>
        ) : (
          <button
            type="button"
            onClick={next}
            className="rounded-md bg-indigo-600 px-4 py-2 font-medium text-white hover:bg-indigo-700"
          >
            {isLast ? 'Ver resultado' : 'Siguiente'}
          </button>
        )}
      </div>
    </section>
  );
}
