import { useId } from 'react';
import { isCorrect, type RenderedQuestion, type Response } from '../../lib/quiz';
import { url } from '../../lib/url';

interface Props {
  question: RenderedQuestion;
  /** Orden en que se muestran las opciones (índices originales). */
  order: number[];
  response: Response;
  onChange: (r: Response) => void;
  /** Si es true se muestra la corrección y se bloquea la edición. */
  checked: boolean;
}

const DIFFICULTY = ['Fácil', 'Media', 'Difícil'];

/** Enlace a la sección de la lección donde se explica la pregunta. */
export function refHref(q: RenderedQuestion): string {
  return `${url(`/teoria/${q.lessonId}/`)}${q.ref ?? ''}`;
}

export default function QuestionView({ question: q, order, response, onChange, checked }: Props) {
  const uid = useId();
  const promptId = `${uid}-prompt`;
  const correct = checked && isCorrect(q, response);
  const answer = new Set(q.answer ?? []);

  const optionLabel = (i: number) => q.options?.[i] ?? '';
  const mark = (orig: number) => {
    if (!checked) return null;
    const isAnswer = answer.has(orig);
    const chosen = response.includes(orig);
    if (isAnswer) return <Badge tone="ok">✓ Correcta</Badge>;
    if (chosen) return <Badge tone="bad">✗ Tu respuesta</Badge>;
    return null;
  };

  const optionClass = (orig: number) =>
    checked && answer.has(orig)
      ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-950/40'
      : checked && response.includes(orig)
        ? 'border-red-500 bg-red-50 dark:bg-red-950/40'
        : 'border-slate-200 hover:border-indigo-400 dark:border-slate-700';

  const toggleMultiple = (orig: number) =>
    onChange(response.includes(orig) ? response.filter((v) => v !== orig) : [...response, orig]);

  const move = (pos: number, delta: -1 | 1) => {
    const target = pos + delta;
    if (target < 0 || target >= response.length) return;
    const next = [...response];
    [next[pos], next[target]] = [next[target], next[pos]];
    onChange(next);
  };

  return (
    <fieldset aria-labelledby={promptId} className="min-w-0 border-0 p-0">
      <p className="mb-2 text-xs text-slate-500 dark:text-slate-400">
        Dificultad: {DIFFICULTY[q.difficulty - 1] ?? q.difficulty}
        {q.type === 'multiple' && ' · Hay más de una respuesta correcta: marca todas'}
        {q.type === 'order' && ' · Ordena los elementos con los botones Subir y Bajar'}
      </p>
      <div
        id={promptId}
        className="prose prose-slate max-w-none font-medium dark:prose-invert"
        dangerouslySetInnerHTML={{ __html: q.promptHtml }}
      />
      {q.code && (
        <pre className="my-3 overflow-x-auto rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm dark:border-slate-700 dark:bg-slate-900">
          <code>{q.code}</code>
        </pre>
      )}

      <div className="mt-3 space-y-2">
        {q.type === 'truefalse' &&
          ['Verdadero', 'Falso'].map((label, i) => (
            <label
              key={label}
              className={`flex cursor-pointer items-center gap-3 rounded-lg border p-3 ${optionClass(i)}`}
            >
              <input
                type="radio"
                name={uid}
                checked={response[0] === i}
                disabled={checked}
                onChange={() => onChange([i])}
              />
              <span className="flex-1">{label}</span>
              {mark(i)}
            </label>
          ))}

        {(q.type === 'single' || q.type === 'code-output') &&
          order.map((orig) => (
            <label
              key={orig}
              className={`flex cursor-pointer items-start gap-3 rounded-lg border p-3 ${optionClass(orig)}`}
            >
              <input
                type="radio"
                name={uid}
                className="mt-1"
                checked={response[0] === orig}
                disabled={checked}
                onChange={() => onChange([orig])}
              />
              <span
                className="flex-1"
                dangerouslySetInnerHTML={{ __html: q.optionsHtml?.[orig] ?? optionLabel(orig) }}
              />
              {mark(orig)}
            </label>
          ))}

        {q.type === 'multiple' &&
          order.map((orig) => (
            <label
              key={orig}
              className={`flex cursor-pointer items-start gap-3 rounded-lg border p-3 ${optionClass(orig)}`}
            >
              <input
                type="checkbox"
                className="mt-1"
                checked={response.includes(orig)}
                disabled={checked}
                onChange={() => toggleMultiple(orig)}
              />
              <span
                className="flex-1"
                dangerouslySetInnerHTML={{ __html: q.optionsHtml?.[orig] ?? optionLabel(orig) }}
              />
              {mark(orig)}
            </label>
          ))}

        {q.type === 'order' && (
          <ol className="space-y-2">
            {response.map((orig, pos) => (
              <li
                key={orig}
                className="flex items-center gap-3 rounded-lg border border-slate-200 p-3 dark:border-slate-700"
              >
                <span className="w-6 text-center font-semibold text-slate-500">{pos + 1}</span>
                <span
                  className="flex-1"
                  dangerouslySetInnerHTML={{ __html: q.optionsHtml?.[orig] ?? optionLabel(orig) }}
                />
                {!checked && (
                  <span className="flex gap-1">
                    <button
                      type="button"
                      onClick={() => move(pos, -1)}
                      disabled={pos === 0}
                      aria-label={`Subir: ${optionLabel(orig)}`}
                      className="rounded border border-slate-300 px-2 py-1 text-sm disabled:opacity-40 dark:border-slate-600"
                    >
                      Subir
                    </button>
                    <button
                      type="button"
                      onClick={() => move(pos, 1)}
                      disabled={pos === response.length - 1}
                      aria-label={`Bajar: ${optionLabel(orig)}`}
                      className="rounded border border-slate-300 px-2 py-1 text-sm disabled:opacity-40 dark:border-slate-600"
                    >
                      Bajar
                    </button>
                  </span>
                )}
              </li>
            ))}
          </ol>
        )}
      </div>

      <div aria-live="polite" className="mt-4">
        {checked && (
          <div
            className={`rounded-lg border-l-4 p-4 ${
              correct
                ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-950/40'
                : 'border-red-500 bg-red-50 dark:bg-red-950/40'
            }`}
          >
            <p className="font-semibold">{correct ? '✓ Correcto' : '✗ Incorrecto'}</p>
            {q.type === 'order' && !correct && (
              <div className="mt-2 text-sm">
                <p className="font-medium">Orden correcto:</p>
                <ol className="list-decimal pl-5">
                  {(q.options ?? []).map((opt, i) => (
                    <li key={i}>{opt}</li>
                  ))}
                </ol>
              </div>
            )}
            <div
              className="prose prose-sm prose-slate mt-2 max-w-none dark:prose-invert"
              dangerouslySetInnerHTML={{ __html: q.explanationHtml }}
            />
            <p className="mt-2 text-sm">
              <a
                className="font-medium text-indigo-700 hover:underline dark:text-indigo-300"
                href={refHref(q)}
              >
                Repasar en la lección →
              </a>
            </p>
          </div>
        )}
      </div>
    </fieldset>
  );
}

function Badge({ tone, children }: { tone: 'ok' | 'bad'; children: string }) {
  return (
    <span
      className={`shrink-0 rounded px-2 py-0.5 text-xs font-semibold ${
        tone === 'ok'
          ? 'bg-emerald-200 text-emerald-900 dark:bg-emerald-900 dark:text-emerald-100'
          : 'bg-red-200 text-red-900 dark:bg-red-900 dark:text-red-100'
      }`}
    >
      {children}
    </span>
  );
}
