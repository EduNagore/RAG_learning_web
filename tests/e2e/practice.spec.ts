import { readdirSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { expect, test, type Page } from '@playwright/test';
import { parse } from 'yaml';

interface Q {
  id: string;
  type: 'single' | 'multiple' | 'truefalse' | 'order' | 'code-output';
  options?: string[];
  answer?: number[];
}

const LESSON = 'm00-fundamentos-llm/01-tokens-y-contexto';
const STORAGE_KEY = 'rma:progress:v1';

/** Todos los ficheros bajo un directorio con la extensión dada. */
function walk(dir: string, ext: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory()
      ? walk(resolve(dir, e.name), ext)
      : e.name.endsWith(ext)
        ? [resolve(dir, e.name)]
        : [],
  );
}

/** Totales reales del contenido, para que los tests no dependan de cuántas lecciones haya. */
const TOTAL_LESSONS = walk(resolve(process.cwd(), 'src/content/lessons'), '.mdx').length;
const TOTAL_QUESTIONS = walk(resolve(process.cwd(), 'src/content/quizzes'), '.yaml').reduce(
  (n, f) => n + (parse(readFileSync(f, 'utf8')).questions as Q[]).length,
  0,
);

function loadQuiz(lesson: string): Q[] {
  const file = resolve(process.cwd(), 'src/content/quizzes', `${lesson}.yaml`);
  return parse(readFileSync(file, 'utf8')).questions as Q[];
}

/** Texto visible de una opción: el Markdown (código, negritas) ya viene renderizado. */
const plain = (s: string) => s.replace(/[`*]/g, '');
const escapeRe = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const optionRegex = (s: string) => new RegExp(`^\\s*${escapeRe(plain(s))}\\s*$`);

const readProgress = (page: Page) =>
  page.evaluate((k) => JSON.parse(localStorage.getItem(k) ?? 'null'), STORAGE_KEY);

/** Responde la pregunta visible usando la solución del YAML. `correct=false` falla a propósito. */
async function answer(page: Page, q: Q, correct: boolean) {
  const opts = q.options ?? [];
  const label = (text: string) =>
    page
      .locator('label')
      .filter({ hasText: optionRegex(text) })
      .first();

  if (q.type === 'truefalse') {
    const want = correct ? q.answer![0] : 1 - q.answer![0];
    await page
      .locator('label')
      .filter({ hasText: want === 0 ? /^\s*Verdadero\s*$/ : /^\s*Falso\s*$/ })
      .click();
  } else if (q.type === 'single' || q.type === 'code-output') {
    const idx = correct ? q.answer![0] : opts.findIndex((_, i) => i !== q.answer![0]);
    await label(opts[idx]).click();
  } else if (q.type === 'multiple') {
    const picks = correct ? q.answer! : [opts.findIndex((_, i) => !q.answer!.includes(i))];
    for (const i of picks) await label(opts[i]).click();
  } else if (correct) {
    // order: lleva cada elemento a su sitio con los botones Subir.
    for (let target = 0; target < opts.length; target++) {
      for (let guard = 0; guard < 10; guard++) {
        const texts = await page.locator('ol > li span.flex-1').allInnerTexts();
        const at = texts.findIndex((t) => t.trim() === plain(opts[target]));
        if (at <= target) break;
        await page.getByRole('button', { name: `Subir: ${opts[target]}`, exact: true }).click();
      }
    }
  } // order incorrecto: se deja el orden mezclado inicial, que nunca es la solución.
}

async function openLessonQuiz(page: Page) {
  await page.goto(`teoria/${LESSON}/`);
  const heading = page.getByRole('heading', { name: 'Comprueba lo aprendido' });
  await heading.scrollIntoViewIfNeeded();
  await expect(heading).toBeVisible();
}

test('mini-test de lección: respondiendo todo bien se aprueba y se guarda la nota', async ({
  page,
}) => {
  const questions = loadQuiz(LESSON);
  await openLessonQuiz(page);

  for (let i = 0; i < questions.length; i++) {
    await expect(page.getByText(`Pregunta ${i + 1} de ${questions.length}`)).toBeVisible();
    await answer(page, questions[i], true);
    await page.getByRole('button', { name: 'Comprobar' }).click();
    await expect(page.getByText('✓ Correcto')).toBeVisible();
    await page
      .getByRole('button', { name: i === questions.length - 1 ? 'Ver resultado' : 'Siguiente' })
      .click();
  }

  await expect(page.getByRole('heading', { name: 'Resultado: 100 %' })).toBeVisible();
  await expect(page.getByText('Aprobado')).toBeVisible();

  const progress = await readProgress(page);
  expect(progress.quizScores[LESSON]).toMatchObject({ best: 100, last: 100, attempts: 1 });
  expect(progress.quizScores[LESSON].updatedAt).toBeTruthy(); // la marca de tiempo permite fusionar
  expect(progress.srs).toEqual({}); // sin fallos no se crea ninguna tarjeta de repaso
});

test('un fallo muestra la explicación y manda la pregunta al repaso espaciado', async ({
  page,
}) => {
  const questions = loadQuiz(LESSON);
  await openLessonQuiz(page);

  // Falla la primera pregunta y acierta el resto.
  for (let i = 0; i < questions.length; i++) {
    await answer(page, questions[i], i !== 0);
    await page.getByRole('button', { name: 'Comprobar' }).click();
    if (i === 0) {
      await expect(page.getByText('✗ Incorrecto')).toBeVisible();
      await expect(page.getByRole('link', { name: 'Repasar en la lección →' })).toBeVisible();
    }
    await page
      .getByRole('button', { name: i === questions.length - 1 ? 'Ver resultado' : 'Siguiente' })
      .click();
  }

  const pct = Math.round(((questions.length - 1) / questions.length) * 100);
  await expect(page.getByRole('heading', { name: `Resultado: ${pct} %` })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'A repasar (1)' })).toBeVisible();

  const progress = await readProgress(page);
  expect(progress.quizScores[LESSON].last).toBe(pct);
  expect(Object.keys(progress.srs)).toEqual([questions[0].id]);
  expect(progress.srs[questions[0].id].box).toBe(1);
});

test('los enlaces "Repasar en la lección" apuntan a un ancla que existe', async ({ page }) => {
  await openLessonQuiz(page);
  const q = loadQuiz(LESSON)[0];
  await answer(page, q, false);
  await page.getByRole('button', { name: 'Comprobar' }).click();
  const href = await page
    .getByRole('link', { name: 'Repasar en la lección →' })
    .getAttribute('href');
  expect(href).toMatch(/^\/RAG_learning_web\/teoria\/m00-fundamentos-llm\/01-tokens-y-contexto\/#/);
  const anchor = decodeURIComponent(href!.split('#')[1]);
  await expect(page.locator(`[id="${anchor}"]`)).toHaveCount(1);
});

test('repaso espaciado: las tarjetas vencidas se repasan y suben de caja', async ({ page }) => {
  const [q1, q2, q3] = loadQuiz(LESSON);
  const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
  const seed = {
    version: 1,
    lessonsRead: {},
    quizScores: {},
    labs: {},
    exams: [],
    srs: {
      [q1.id]: { box: 1, due: yesterday },
      [q2.id]: { box: 3, due: yesterday },
      [q3.id]: { box: 2, due: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString() }, // aún no toca
    },
  };
  await page.addInitScript(
    ([k, v]) => {
      if (!localStorage.getItem(k)) localStorage.setItem(k, v);
    },
    [STORAGE_KEY, JSON.stringify(seed)] as const,
  );

  await page.goto('practica/repaso/');
  await expect(page.getByText('Tienes 2 preguntas pendientes')).toBeVisible();
  await page.getByRole('button', { name: 'Empezar repaso' }).click();

  const byId = new Map(loadQuiz(LESSON).map((q) => [q.id, q]));
  // Se repasan las 2 vencidas (las más atrasadas primero): acertamos la primera y fallamos la segunda.
  await answer(page, byId.get(q1.id)!, true);
  await page.getByRole('button', { name: 'Comprobar' }).click();
  await expect(page.getByText('✓ Correcto')).toBeVisible();
  // El resultado se guarda al instante, no al terminar la sesión.
  expect((await readProgress(page)).srs[q1.id].box).toBe(2);
  await page.getByRole('button', { name: 'Siguiente' }).click();

  await answer(page, byId.get(q2.id)!, false);
  await page.getByRole('button', { name: 'Comprobar' }).click();
  await expect(page.getByText('✗ Incorrecto')).toBeVisible();
  await page.getByRole('button', { name: 'Ver resultado' }).click();

  const after = await readProgress(page);
  expect(after.srs[q1.id].box).toBe(2); // acierto: sube
  expect(after.srs[q2.id].box).toBe(1); // fallo: vuelve a la caja 1
  expect(after.srs[q3.id].box).toBe(2); // no tocaba: intacta
  expect(after.quizScores).toEqual({}); // el repaso no altera las notas de los tests
});

test('repaso sin tarjetas explica cómo aparecen', async ({ page }) => {
  await page.goto('practica/repaso/');
  await expect(page.getByText('Todavía no tienes preguntas en repaso')).toBeVisible();
});

test('test de módulo: el test rápido muestra una muestra de 20 preguntas', async ({ page }) => {
  await page.goto('practica/tests/m00-fundamentos-llm/');
  await expect(page.getByText(/Este test tiene 65 preguntas/)).toBeVisible();
  await page.getByRole('button', { name: 'Test rápido (20 preguntas)' }).click();
  await expect(page.getByText('Pregunta 1 de 20')).toBeVisible();
});

test('examen: configurar, hacerlo, ver el informe por módulo y guardar el resultado', async ({
  page,
}) => {
  await page.goto('practica/examen/');
  await expect(
    page.getByText(`Con tu selección hay ${TOTAL_QUESTIONS} preguntas disponibles`),
  ).toBeVisible();
  await page.getByRole('button', { name: 'Empezar examen' }).click();
  await expect(page.getByRole('heading', { name: 'Pregunta 1 de 20' })).toBeVisible();

  // Terminar sin responder pide confirmación explícita.
  await page.getByRole('button', { name: 'Terminar examen' }).click();
  await expect(page.getByRole('alertdialog')).toContainText('sin responder');
  await page.getByRole('button', { name: 'Sí, terminar' }).click();

  await expect(page.getByRole('heading', { name: /Resultado: 0 \/ 20/ })).toBeVisible();
  await expect(page.getByRole('table', { name: 'Resultado por módulo' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Repasar el módulo →' }).first()).toBeVisible();

  const progress = await readProgress(page);
  expect(progress.exams).toHaveLength(1);
  expect(progress.exams[0]).toMatchObject({ score: 0, total: 20 });
  expect(Object.keys(progress.srs)).toHaveLength(20); // todas las falladas pasan al repaso
});

test('el examen respeta el número de preguntas y los módulos elegidos', async ({ page }) => {
  await page.goto('practica/examen/');
  await page.getByRole('radio', { name: '40' }).check();
  await expect(page.getByText(/el examen tendrá 40|preguntas disponibles/)).toBeVisible();
  await page.getByRole('button', { name: 'Empezar examen' }).click();
  await expect(page.getByRole('heading', { name: 'Pregunta 1 de 40' })).toBeVisible();
});

test('panel de progreso: exportar, reiniciar e importar devuelve el mismo estado', async ({
  page,
}) => {
  const questions = loadQuiz(LESSON);
  // Genera algo de progreso: marcar la lección como leída.
  await page.goto(`teoria/${LESSON}/`);
  await page.getByRole('button', { name: 'Marcar como leída' }).click();
  await expect(page.getByRole('button', { name: /Lección leída/ })).toBeVisible();

  await page.goto('progreso/');
  await expect(page.getByText(`1 / ${TOTAL_LESSONS}`)).toBeVisible();

  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.getByRole('button', { name: 'Exportar progreso' }).click(),
  ]);
  expect(download.suggestedFilename()).toMatch(/^rma-progreso-\d{4}-\d{2}-\d{2}\.json$/);
  const exported = readFileSync((await download.path())!, 'utf8');
  expect(JSON.parse(exported).lessonsRead[LESSON]).toBeTruthy();

  await page.getByRole('button', { name: 'Reiniciar progreso' }).click();
  await page.getByRole('button', { name: 'Sí, borrar' }).click();
  await expect(page.getByText(`0 / ${TOTAL_LESSONS}`)).toBeVisible();

  await page.getByLabel('Importar progreso').setInputFiles({
    name: 'backup.json',
    mimeType: 'application/json',
    buffer: Buffer.from(exported),
  });
  await expect(page.getByText('Progreso importado')).toBeVisible();
  await expect(page.getByText(`1 / ${TOTAL_LESSONS}`)).toBeVisible();
  expect((await readProgress(page)).lessonsRead[LESSON]).toBeTruthy();
  expect(questions.length).toBeGreaterThan(0);
});

test('importar un archivo que no es un progreso muestra un error y no borra nada', async ({
  page,
}) => {
  await page.goto(`teoria/${LESSON}/`);
  await page.getByRole('button', { name: 'Marcar como leída' }).click();
  await expect(page.getByRole('button', { name: /Lección leída/ })).toBeVisible();

  await page.goto('progreso/');
  await page.getByLabel('Importar progreso').setInputFiles({
    name: 'roto.json',
    mimeType: 'application/json',
    buffer: Buffer.from('esto no es json'),
  });
  await expect(page.getByText('El archivo no es un JSON válido.')).toBeVisible();
  expect((await readProgress(page)).lessonsRead[LESSON]).toBeTruthy();
});
