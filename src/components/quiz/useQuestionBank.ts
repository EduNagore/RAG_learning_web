import { useEffect, useState } from 'react';
import type { QuestionBank } from '../../lib/quiz';
import { url } from '../../lib/url';

let cache: Promise<QuestionBank> | null = null;

/** Descarga (una sola vez por página) el banco de preguntas publicado en build. */
export function loadQuestionBank(): Promise<QuestionBank> {
  cache ??= fetch(url('/data/questions.json')).then((r) => {
    if (!r.ok) throw new Error(`No se pudo cargar el banco de preguntas (${r.status})`);
    return r.json() as Promise<QuestionBank>;
  });
  cache.catch(() => (cache = null)); // permite reintentar tras un fallo de red
  return cache;
}

export function useQuestionBank() {
  const [bank, setBank] = useState<QuestionBank | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    let alive = true;
    loadQuestionBank()
      .then((b) => alive && setBank(b))
      .catch((e: Error) => alive && setError(e.message));
    return () => {
      alive = false;
    };
  }, []);
  return { bank, error };
}
