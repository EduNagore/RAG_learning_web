import { useMemo, useState } from 'react';

export interface InterviewQuestion {
  id: string;
  topic: string;
  topicTitle: string;
  level: 'junior' | 'mid' | 'senior';
  kind: 'conceptual' | 'design' | 'debug';
  es: { q: string; a: string };
  en: { q: string; a: string };
  lessons: { id: string; title: string; href: string }[];
}

interface Props {
  questions: InterviewQuestion[];
}

type Lang = 'es' | 'en';

const KINDS: Record<InterviewQuestion['kind'], Record<Lang, string>> = {
  conceptual: { es: 'Conceptual', en: 'Conceptual' },
  design: { es: 'Diseño', en: 'Design' },
  debug: { es: 'Depuración', en: 'Debugging' },
};

const T = {
  es: {
    topic: 'Tema',
    level: 'Nivel',
    kind: 'Tipo',
    all: 'Todos',
    list: 'Lista',
    flash: 'Flashcards',
    show: 'Mostrar respuesta',
    hide: 'Ocultar respuesta',
    next: 'Siguiente',
    shuffle: 'Mezclar',
    count: (n: number, total: number) => `${n} de ${total} preguntas`,
    card: (i: number, n: number) => `Tarjeta ${i} de ${n}`,
    none: 'Ninguna pregunta cumple los filtros.',
    lessons: 'Más información',
    language: 'Idioma',
  },
  en: {
    topic: 'Topic',
    level: 'Level',
    kind: 'Type',
    all: 'All',
    list: 'List',
    flash: 'Flashcards',
    show: 'Show answer',
    hide: 'Hide answer',
    next: 'Next',
    shuffle: 'Shuffle',
    count: (n: number, total: number) => `${n} of ${total} questions`,
    card: (i: number, n: number) => `Card ${i} of ${n}`,
    none: 'No question matches the filters.',
    lessons: 'Learn more',
    language: 'Language',
  },
} as const;

const select =
  'rounded-md border border-slate-300 px-2 py-1 text-sm dark:border-slate-700 dark:bg-slate-900';
const button =
  'rounded-md border border-slate-300 px-3 py-1 text-sm hover:bg-slate-100 disabled:opacity-40 dark:border-slate-700 dark:hover:bg-slate-800';

/** Barajado determinista (Fisher-Yates con un generador congruencial) para poder probarlo. */
export function shuffled<T>(items: readonly T[], seed: number): T[] {
  const out = [...items];
  let state = seed >>> 0 || 1;
  for (let i = out.length - 1; i > 0; i--) {
    state = (Math.imul(state, 1664525) + 1013904223) >>> 0;
    const j = state % (i + 1);
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

export default function InterviewBrowser({ questions }: Props) {
  const [lang, setLang] = useState<Lang>('es');
  const [topic, setTopic] = useState('all');
  const [level, setLevel] = useState('all');
  const [kind, setKind] = useState('all');
  const [mode, setMode] = useState<'list' | 'flash'>('list');
  const [seed, setSeed] = useState(0);
  const [index, setIndex] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const t = T[lang];

  const topics = useMemo(
    () => [...new Map(questions.map((q) => [q.topic, q.topicTitle])).entries()],
    [questions],
  );
  const filtered = useMemo(
    () =>
      questions.filter(
        (q) =>
          (topic === 'all' || q.topic === topic) &&
          (level === 'all' || q.level === level) &&
          (kind === 'all' || q.kind === kind),
      ),
    [questions, topic, level, kind],
  );
  const deck = useMemo(() => (seed ? shuffled(filtered, seed) : filtered), [filtered, seed]);
  const current = deck[Math.min(index, Math.max(0, deck.length - 1))];

  const resetCard = () => {
    setIndex(0);
    setRevealed(false);
  };

  const renderAnswer = (q: InterviewQuestion) => (
    <div className="mt-3 space-y-2 text-sm">
      {q[lang].a.split('\n\n').map((p, i) => (
        <p key={i} className="whitespace-pre-line">
          {p}
        </p>
      ))}
      {q.lessons.length > 0 && (
        <p className="text-slate-600 dark:text-slate-400">
          {t.lessons}:{' '}
          {q.lessons.map((l, i) => (
            <span key={l.id}>
              {i > 0 && ', '}
              <a
                href={l.href}
                className="text-indigo-700 underline underline-offset-2 dark:text-indigo-300"
              >
                {l.title}
              </a>
            </span>
          ))}
        </p>
      )}
    </div>
  );

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end gap-4">
        <label className="block text-sm">
          {t.language}
          <select
            value={lang}
            onChange={(e) => setLang(e.target.value as Lang)}
            className={`${select} ml-2`}
          >
            <option value="es">Español</option>
            <option value="en">English</option>
          </select>
        </label>
        <label className="block text-sm">
          {t.topic}
          <select
            value={topic}
            onChange={(e) => {
              setTopic(e.target.value);
              resetCard();
            }}
            className={`${select} ml-2`}
          >
            <option value="all">{t.all}</option>
            {topics.map(([id, title]) => (
              <option key={id} value={id}>
                {title}
              </option>
            ))}
          </select>
        </label>
        <label className="block text-sm">
          {t.level}
          <select
            value={level}
            onChange={(e) => {
              setLevel(e.target.value);
              resetCard();
            }}
            className={`${select} ml-2`}
          >
            <option value="all">{t.all}</option>
            <option value="junior">junior</option>
            <option value="mid">mid</option>
            <option value="senior">senior</option>
          </select>
        </label>
        <label className="block text-sm">
          {t.kind}
          <select
            value={kind}
            onChange={(e) => {
              setKind(e.target.value);
              resetCard();
            }}
            className={`${select} ml-2`}
          >
            <option value="all">{t.all}</option>
            {(Object.keys(KINDS) as InterviewQuestion['kind'][]).map((k) => (
              <option key={k} value={k}>
                {KINDS[k][lang]}
              </option>
            ))}
          </select>
        </label>
        <div className="flex gap-2" role="group" aria-label="Modo">
          <button
            type="button"
            className={button}
            aria-pressed={mode === 'list'}
            onClick={() => setMode('list')}
          >
            {t.list}
          </button>
          <button
            type="button"
            className={button}
            aria-pressed={mode === 'flash'}
            onClick={() => {
              setMode('flash');
              resetCard();
            }}
          >
            {t.flash}
          </button>
        </div>
      </div>

      <p role="status" className="text-sm font-medium">
        {t.count(filtered.length, questions.length)}
      </p>

      {filtered.length === 0 && <p className="text-sm text-slate-500">{t.none}</p>}

      {mode === 'list' && (
        <ul className="space-y-3">
          {filtered.map((q) => (
            <li
              key={q.id}
              className="rounded-lg border border-slate-200 p-4 dark:border-slate-800"
              data-testid="interview-item"
            >
              <details>
                <summary className="cursor-pointer font-medium">{q[lang].q}</summary>
                <p className="mt-2 text-xs text-slate-500">
                  {q.topicTitle} · {q.level} · {KINDS[q.kind][lang]}
                </p>
                {renderAnswer(q)}
              </details>
            </li>
          ))}
        </ul>
      )}

      {mode === 'flash' && current && (
        <div className="space-y-3 rounded-lg border border-slate-200 p-5 dark:border-slate-800">
          <p className="text-xs text-slate-500" role="status">
            {t.card(Math.min(index, deck.length - 1) + 1, deck.length)} · {current.topicTitle} ·{' '}
            {current.level}
          </p>
          <p className="text-lg font-medium">{current[lang].q}</p>
          {revealed && renderAnswer(current)}
          <div className="flex flex-wrap gap-2">
            <button type="button" className={button} onClick={() => setRevealed((r) => !r)}>
              {revealed ? t.hide : t.show}
            </button>
            <button
              type="button"
              className={button}
              onClick={() => {
                setIndex((i) => (i + 1) % deck.length);
                setRevealed(false);
              }}
            >
              {t.next}
            </button>
            <button
              type="button"
              className={button}
              onClick={() => {
                setSeed((s) => s + 7919);
                resetCard();
              }}
            >
              {t.shuffle}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
