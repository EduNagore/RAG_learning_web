import { useEffect, useMemo, useRef, useState } from 'react';
import {
  PASS_THRESHOLD,
  buildExam,
  examBreakdown,
  isCorrect,
  passed,
  presentationOrder,
  questionSeed,
  scorePct,
  type QuestionBank,
  type RenderedQuestion,
  type Response,
} from '../../lib/quiz';
import { recordExam, recordReview } from '../../lib/progress';
import { url } from '../../lib/url';
import QuestionView from './QuestionView';
import { useQuestionBank } from './useQuestionBank';

const COUNTS = [20, 40, 60];
const SECONDS_PER_QUESTION = 90;
const newSeed = () => Math.floor(Math.random() * 2 ** 31);

const fmt = (s: number) =>
  `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;

export default function Exam() {
  const { bank, error } = useQuestionBank();
  if (error) return <p role="alert">No se pudieron cargar las preguntas: {error}</p>;
  if (!bank) return <p>Cargando preguntas…</p>;
  if (bank.questions.length === 0) return <p>Aún no hay preguntas para hacer un examen.</p>;
  return <ExamFlow bank={bank} />;
}

function ExamFlow({ bank }: { bank: QuestionBank }) {
  const moduleIds = useMemo(
    () => Object.keys(bank.modules).sort((a, b) => bank.modules[a].order - bank.modules[b].order),
    [bank],
  );
  const [selected, setSelected] = useState<string[]>(moduleIds);
  const [count, setCount] = useState(COUNTS[0]);
  const [timed, setTimed] = useState(false);
  const [exam, setExam] = useState<{
    questions: RenderedQuestion[];
    seed: number;
    deadline: number | null;
  } | null>(null);
  const [report, setReport] = useState<ReportData | null>(null);

  const available = bank.questions.filter((q) => selected.includes(q.moduleId)).length;
  const effectiveCount = Math.min(count, available);

  const start = () => {
    const seed = newSeed();
    const questions = buildExam(bank.questions, { moduleIds: selected, count, seed });
    setReport(null);
    setExam({
      questions,
      seed,
      deadline: timed ? Date.now() + questions.length * SECONDS_PER_QUESTION * 1000 : null,
    });
  };

  const finish = (responses: Record<string, Response>, orders: Record<string, number[]>) => {
    if (!exam) return;
    const items = exam.questions.map((q) => ({
      q,
      correct: isCorrect(q, responses[q.id] ?? (q.type === 'order' ? orders[q.id] : [])),
    }));
    const byModule = examBreakdown(
      items.map(({ q, correct }) => ({ moduleId: q.moduleId, correct })),
    );
    const score = items.filter((i) => i.correct).length;
    recordExam({ date: new Date().toISOString(), score, total: items.length, byModule });
    recordReview(items.map(({ q, correct }) => ({ id: q.id, correct })));
    setReport({ items, byModule, score, total: items.length });
    setExam(null);
  };

  if (exam) return <ExamRun exam={exam} onFinish={finish} />;
  if (report) return <ExamReport bank={bank} report={report} onNew={() => setReport(null)} />;

  const byPart = new Map<string, string[]>();
  for (const id of moduleIds)
    byPart.set(bank.modules[id].part, [...(byPart.get(bank.modules[id].part) ?? []), id]);

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        start();
      }}
      className="space-y-6"
    >
      <fieldset>
        <legend className="text-lg font-semibold">1. Módulos</legend>
        <p className="mb-2 text-sm text-slate-600 dark:text-slate-400">
          Solo aparecen los módulos que ya tienen preguntas.
        </p>
        <div className="space-y-2">
          {[...byPart.values()].flat().map((id) => (
            <label key={id} className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={selected.includes(id)}
                onChange={(e) =>
                  setSelected((s) => (e.target.checked ? [...s, id] : s.filter((x) => x !== id)))
                }
              />
              <span>{bank.modules[id].title}</span>
              <span className="text-xs text-slate-500">
                ({bank.questions.filter((q) => q.moduleId === id).length} preguntas)
              </span>
            </label>
          ))}
        </div>
      </fieldset>

      <fieldset>
        <legend className="text-lg font-semibold">2. Número de preguntas</legend>
        <div className="mt-2 flex flex-wrap gap-4">
          {COUNTS.map((n) => (
            <label key={n} className="flex items-center gap-2">
              <input type="radio" name="count" checked={count === n} onChange={() => setCount(n)} />
              {n}
            </label>
          ))}
        </div>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
          Con tu selección hay {available} preguntas disponibles
          {available < count && available > 0 ? `: el examen tendrá ${available}` : ''}.
        </p>
      </fieldset>

      <label className="flex items-center gap-2">
        <input type="checkbox" checked={timed} onChange={(e) => setTimed(e.target.checked)} />
        Con temporizador ({SECONDS_PER_QUESTION} s por pregunta
        {effectiveCount > 0 ? `, ${fmt(effectiveCount * SECONDS_PER_QUESTION)} en total` : ''})
      </label>

      <button
        type="submit"
        disabled={selected.length === 0 || available === 0}
        className="rounded-md bg-indigo-600 px-5 py-2.5 font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        Empezar examen
      </button>
    </form>
  );
}

interface ReportData {
  items: { q: RenderedQuestion; correct: boolean }[];
  byModule: Record<string, number>;
  score: number;
  total: number;
}

function ExamRun({
  exam,
  onFinish,
}: {
  exam: { questions: RenderedQuestion[]; seed: number; deadline: number | null };
  onFinish: (responses: Record<string, Response>, orders: Record<string, number[]>) => void;
}) {
  const { questions, seed, deadline } = exam;
  const [idx, setIdx] = useState(0);
  const [responses, setResponses] = useState<Record<string, Response>>({});
  const [confirming, setConfirming] = useState(false);
  const [left, setLeft] = useState(
    deadline ? Math.max(0, Math.round((deadline - Date.now()) / 1000)) : null,
  );
  const headingRef = useRef<HTMLHeadingElement>(null);
  const first = useRef(true);

  const orders = useMemo(
    () =>
      Object.fromEntries(
        questions.map((q) => [q.id, presentationOrder(q, questionSeed(seed, q.id))]),
      ),
    [questions, seed],
  );

  useEffect(() => {
    if (deadline === null) return;
    const t = setInterval(
      () => setLeft(Math.max(0, Math.round((deadline - Date.now()) / 1000))),
      1000,
    );
    return () => clearInterval(t);
  }, [deadline]);

  // Se acabó el tiempo: se corrige lo respondido hasta ahora.
  useEffect(() => {
    if (left === 0) onFinish(responses, orders);
  }, [left]);

  useEffect(() => {
    if (first.current) {
      first.current = false;
      return;
    }
    headingRef.current?.focus();
  }, [idx]);

  const q = questions[idx];
  const response = responses[q.id] ?? (q.type === 'order' ? orders[q.id] : []);
  const unanswered = questions.filter(
    (x) => x.type !== 'order' && !(responses[x.id]?.length > 0),
  ).length;

  return (
    <section aria-labelledby="exam-title">
      <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2">
        <h2
          id="exam-title"
          ref={headingRef}
          tabIndex={-1}
          className="text-xl font-semibold outline-none"
        >
          Pregunta {idx + 1} de {questions.length}
        </h2>
        {left !== null && (
          <p
            role="timer"
            aria-label="Tiempo restante"
            className={`font-mono text-lg ${left <= 60 ? 'text-red-600 dark:text-red-400' : ''}`}
          >
            {fmt(left)}
          </p>
        )}
      </div>

      <div className="mb-4 flex flex-wrap gap-1" aria-label="Navegación entre preguntas">
        {questions.map((x, i) => {
          const done = x.type === 'order' || (responses[x.id]?.length ?? 0) > 0;
          return (
            <button
              key={x.id}
              type="button"
              onClick={() => setIdx(i)}
              aria-label={`Ir a la pregunta ${i + 1}${done ? ' (respondida)' : ''}`}
              aria-current={i === idx ? 'step' : undefined}
              className={`size-7 rounded text-xs font-medium ${
                i === idx
                  ? 'bg-indigo-600 text-white'
                  : done
                    ? 'bg-indigo-100 text-indigo-900 dark:bg-indigo-950 dark:text-indigo-200'
                    : 'bg-slate-100 dark:bg-slate-800'
              }`}
            >
              {i + 1}
            </button>
          );
        })}
      </div>

      <QuestionView
        key={q.id}
        question={q}
        order={orders[q.id]}
        response={response}
        onChange={(r) => setResponses((s) => ({ ...s, [q.id]: r }))}
        checked={false}
      />

      <div className="mt-5 flex flex-wrap items-center justify-between gap-2">
        <div className="flex gap-2">
          <button
            type="button"
            disabled={idx === 0}
            onClick={() => setIdx(idx - 1)}
            className="rounded-md border border-slate-300 px-4 py-2 disabled:opacity-40 dark:border-slate-700"
          >
            Anterior
          </button>
          <button
            type="button"
            disabled={idx === questions.length - 1}
            onClick={() => setIdx(idx + 1)}
            className="rounded-md border border-slate-300 px-4 py-2 disabled:opacity-40 dark:border-slate-700"
          >
            Siguiente
          </button>
        </div>
        {!confirming ? (
          <button
            type="button"
            onClick={() => (unanswered > 0 ? setConfirming(true) : onFinish(responses, orders))}
            className="rounded-md bg-indigo-600 px-4 py-2 font-medium text-white hover:bg-indigo-700"
          >
            Terminar examen
          </button>
        ) : (
          <div
            role="alertdialog"
            aria-label="Confirmar fin del examen"
            className="flex flex-wrap items-center gap-2"
          >
            <span className="text-sm">
              Te quedan {unanswered} sin responder. ¿Terminar de todos modos?
            </span>
            <button
              type="button"
              onClick={() => onFinish(responses, orders)}
              className="rounded-md bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-700"
            >
              Sí, terminar
            </button>
            <button
              type="button"
              onClick={() => setConfirming(false)}
              className="rounded-md border border-slate-300 px-3 py-1.5 text-sm dark:border-slate-700"
            >
              Seguir
            </button>
          </div>
        )}
      </div>
    </section>
  );
}

function ExamReport({
  bank,
  report,
  onNew,
}: {
  bank: QuestionBank;
  report: ReportData;
  onNew: () => void;
}) {
  const pct = scorePct(report.items);
  const failed = report.items.filter((i) => !i.correct);
  const rows = Object.entries(report.byModule).sort(
    ([a], [b]) => (bank.modules[a]?.order ?? 0) - (bank.modules[b]?.order ?? 0),
  );
  return (
    <section aria-labelledby="report-title" className="space-y-6">
      <div>
        <h2 id="report-title" className="text-2xl font-bold">
          Resultado: {report.score} / {report.total} ({pct} %)
        </h2>
        <p className="mt-1" role="status">
          {passed(pct)
            ? `Aprobado (mínimo ${PASS_THRESHOLD} %).`
            : `Por debajo del ${PASS_THRESHOLD} %: repasa los módulos marcados.`}{' '}
          Las preguntas falladas se han añadido al repaso espaciado.
        </p>
      </div>

      <table className="w-full text-sm">
        <caption className="mb-2 text-left font-semibold">Resultado por módulo</caption>
        <thead>
          <tr className="border-b border-slate-300 text-left dark:border-slate-700">
            <th className="py-1 pr-4">Módulo</th>
            <th className="py-1 pr-4">Acierto</th>
            <th className="py-1">Qué hacer</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(([id, p]) => (
            <tr key={id} className="border-b border-slate-200 dark:border-slate-800">
              <td className="py-1.5 pr-4">{bank.modules[id]?.title ?? id}</td>
              <td className="py-1.5 pr-4 font-medium">{p} %</td>
              <td className="py-1.5">
                {passed(p) ? (
                  '✓ Bien'
                ) : (
                  <a
                    className="text-indigo-700 hover:underline dark:text-indigo-300"
                    href={url(`/teoria/#${id}`)}
                  >
                    Repasar el módulo →
                  </a>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {failed.length > 0 && (
        <div>
          <h3 className="mb-2 font-semibold">Preguntas falladas ({failed.length})</h3>
          <div className="space-y-2">
            {failed.map(({ q }) => (
              <details
                key={q.id}
                className="rounded-lg border border-slate-200 p-3 dark:border-slate-700"
              >
                <summary
                  className="cursor-pointer font-medium"
                  dangerouslySetInnerHTML={{ __html: q.promptHtml }}
                />
                <div
                  className="prose prose-sm prose-slate mt-2 max-w-none dark:prose-invert"
                  dangerouslySetInnerHTML={{ __html: q.explanationHtml }}
                />
                <a
                  className="text-sm font-medium text-indigo-700 hover:underline dark:text-indigo-300"
                  href={`${url(`/teoria/${q.lessonId}/`)}${q.ref ?? ''}`}
                >
                  Repasar en la lección →
                </a>
              </details>
            ))}
          </div>
        </div>
      )}

      <button
        type="button"
        onClick={onNew}
        className="rounded-md bg-indigo-600 px-4 py-2 font-medium text-white hover:bg-indigo-700"
      >
        Nuevo examen
      </button>
    </section>
  );
}
