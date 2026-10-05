import type { APIRoute } from 'astro';
import { getQuestionBank } from '../../lib/quiz-data';

// Se genera en build como /data/questions.json y lo cargan las páginas de examen y repaso.
export const GET: APIRoute = async () =>
  new Response(JSON.stringify(await getQuestionBank()), {
    headers: { 'Content-Type': 'application/json' },
  });
