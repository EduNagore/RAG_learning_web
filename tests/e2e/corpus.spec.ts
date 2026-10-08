import { readdirSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { expect, test } from '@playwright/test';

const corpus = JSON.parse(
  readFileSync(resolve(process.cwd(), 'public/data/nimbus/corpus.json'), 'utf8'),
) as { id: string; title: string; text: string }[];

const LESSON = 'teoria/m06-generacion-contexto/01-prompt-citas-y-grounding/';
const PROSE = 'article[data-pagefind-body] .prose';

test('el corpus de ejemplo se puede consultar: índice y una ficha por documento', async ({
  page,
}) => {
  await page.goto('corpus/');
  await expect(page.getByTestId('corpus-row')).toHaveCount(corpus.length);
  await expect(
    page.getByRole('heading', { name: 'Preguntas del conjunto de evaluación' }),
  ).toBeVisible();

  await page.getByRole('link', { name: 'doc-001', exact: true }).first().click();
  await expect(page).toHaveURL(/corpus\/doc-001\/$/);
  await expect(page.getByRole('heading', { level: 1 })).toHaveText(corpus[0].title);
  await expect(page.getByTestId('corpus-text')).toContainText(
    corpus[0].text.split(/\n{2,}/)[0].slice(0, 40),
  );
  await expect(page.getByText('Preguntas de evaluación que lo usan')).toBeVisible();
});

test('todas las fichas existen y muestran el texto íntegro del documento', async ({ page }) => {
  for (const doc of corpus) {
    await page.goto(`corpus/${doc.id}/`);
    const shown = (await page.getByTestId('corpus-text').innerText()).replace(/\s+/g, ' ');
    expect(shown, doc.id).toBe(doc.text.replace(/\s+/g, ' ').trim());
  }
});

test('en la teoría, las referencias a documentos se pueden leer sin cambiar el texto de la lección', async ({
  browser,
}) => {
  // Línea base: la misma lección sin JavaScript (sin el script de referencias).
  const plain = await browser.newContext({ javaScriptEnabled: false });
  const plainPage = await plain.newPage();
  await plainPage.goto(LESSON);
  const baseline = await plainPage.locator(PROSE).first().innerText();
  await plain.close();

  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto(LESSON);
  const refs = page.locator('button.doc-ref');
  await expect(refs.first()).toBeVisible();
  expect(await refs.count()).toBeGreaterThan(3);

  // El texto visible es exactamente el mismo.
  expect(await page.locator(PROSE).first().innerText()).toBe(baseline);

  // Las referencias inventadas a propósito (doc-099) no se convierten en botones.
  expect(baseline).toContain('doc-099');
  await expect(page.locator('button.doc-ref', { hasText: 'doc-099' })).toHaveCount(0);

  // Al pulsar una, se lee el documento; Escape cierra y el foco vuelve a la referencia.
  const first = refs.first();
  const id = (await first.getAttribute('data-doc'))!;
  const doc = corpus.find((d) => d.id === id)!;
  await first.click();
  const dialog = page.getByRole('dialog');
  await expect(dialog).toBeVisible();
  await expect(dialog.getByRole('heading', { name: doc.title })).toBeVisible();
  await expect(dialog).toContainText(doc.text.split(/\n{2,}/)[0].slice(0, 40));
  await expect(dialog.getByRole('link', { name: 'Ver la ficha completa' })).toHaveAttribute(
    'href',
    new RegExp(`corpus/${id}/$`),
  );
  await page.keyboard.press('Escape');
  await expect(dialog).toBeHidden();
  await expect(first).toBeFocused();
  await context.close();
});

test('el botón «Cerrar» y el teclado también funcionan', async ({ page }) => {
  await page.goto(LESSON);
  const ref = page.locator('button.doc-ref').first();
  await ref.focus();
  await page.keyboard.press('Enter');
  const dialog = page.getByRole('dialog');
  await expect(dialog).toBeVisible();
  await dialog.getByRole('button', { name: 'Cerrar' }).click();
  await expect(dialog).toBeHidden();
});

test('las lecciones sin referencias no descargan el corpus ni cambian', async ({ page }) => {
  const requests: string[] = [];
  page.on('request', (r) => {
    if (r.url().includes('nimbus/corpus.json')) requests.push(r.url());
  });
  await page.goto('teoria/m10-fundamentos-agentes/02-bucle-react-y-herramientas/');
  await page.waitForLoadState('networkidle');
  await expect(page.locator('button.doc-ref')).toHaveCount(0);
  expect(requests).toEqual([]);
});

test('en TODAS las lecciones con referencias, el texto visible es idéntico al de la página sin JavaScript', async ({
  browser,
}) => {
  test.setTimeout(120_000);
  const root = resolve(process.cwd(), 'src/content/lessons');
  const routes = readdirSync(root).flatMap((mod) =>
    readdirSync(resolve(root, mod))
      .filter(
        (f) =>
          f.endsWith('.mdx') && /\bdoc-\d{3}\b/.test(readFileSync(resolve(root, mod, f), 'utf8')),
      )
      .map((f) => `teoria/${mod}/${f.replace(/\.mdx$/, '')}/`),
  );
  expect(routes.length).toBeGreaterThan(5);

  const plain = await browser.newContext({ javaScriptEnabled: false });
  const enhanced = await browser.newContext();
  const a = await plain.newPage();
  const b = await enhanced.newPage();
  const different: string[] = [];
  for (const route of routes) {
    await a.goto(route);
    const baseline = await a.locator(PROSE).first().innerText();
    await b.goto(route);
    await b.waitForLoadState('networkidle');
    if ((await b.locator(PROSE).first().innerText()) !== baseline) different.push(route);
  }
  expect(different).toEqual([]);
  await plain.close();
  await enhanced.close();
});
