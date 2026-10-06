import { readdirSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { expect, test, type Page } from '@playwright/test';
import { parse } from 'yaml';

// Pyodide se descarga de jsDelivr la primera vez: estos tests necesitan red y son lentos.
test.setTimeout(180_000);
const LOAD = { timeout: 120_000 };
const LAB = 'practica/labs/rag-01-coseno-topk/';
const STORAGE_KEY = 'rma:progress:v1';

/** Metadatos reales de los labs, para que el test no dependa de cuántos haya. */
const LABS = readdirSync(resolve(process.cwd(), 'src/content/labs')).map((id) => {
  const text = readFileSync(resolve(process.cwd(), 'src/content/labs', id, 'index.mdx'), 'utf8');
  return parse(text.split('---')[1]) as { part: string; difficulty: number };
});
const count = (f: (l: (typeof LABS)[number]) => boolean) => LABS.filter(f).length;

const readProgress = (page: Page) =>
  page.evaluate((k) => JSON.parse(localStorage.getItem(k) ?? 'null'), STORAGE_KEY);

/** Sustituye todo el contenido del editor (insertText evita el autosangrado y el cierre de paréntesis). */
async function setCode(page: Page, code: string) {
  await page.locator('.cm-content').click();
  await page.keyboard.press('Control+A');
  await page.keyboard.insertText(code);
}

test('el listado muestra los laboratorios y los filtros funcionan', async ({ page }) => {
  await page.goto('practica/labs/');
  const visible = page.locator('#lab-list > li:not([hidden])');
  await expect(page.locator('#lab-list > li')).toHaveCount(LABS.length);

  await page.getByLabel('Parte').selectOption('agentes');
  await expect(visible).toHaveCount(count((l) => l.part === 'agentes'));
  await expect(page.getByRole('link', { name: /bucle de un agente/i })).toBeVisible();

  await page.getByLabel('Parte').selectOption('');
  await page.getByLabel('Dificultad').selectOption('1');
  await expect(visible).toHaveCount(count((l) => l.difficulty === 1));

  // Una combinación sin ningún laboratorio muestra el aviso.
  await page.getByLabel('Parte').selectOption('agentes');
  await page.getByLabel('Dificultad').selectOption('1');
  await expect(visible).toHaveCount(count((l) => l.part === 'agentes' && l.difficulty === 1));
  await expect(page.getByText('Ningún laboratorio coincide con los filtros.')).toBeVisible();
});

test('una lección enlaza a sus laboratorios relacionados', async ({ page }) => {
  await page.goto('teoria/m00-fundamentos-llm/06-embeddings-intuicion/');
  await expect(page.getByRole('heading', { name: 'Practica en código' })).toBeVisible();
  await expect(page.getByRole('link', { name: /Similitud coseno y búsqueda top-k/ })).toBeVisible();
  await expect(page.getByRole('link', { name: 'BM25 desde cero' })).toBeVisible();
});

test('resolver un laboratorio: el starter falla, la solución pasa y el progreso se guarda', async ({
  page,
}) => {
  await page.goto(LAB);
  await expect(page.locator('.cm-content')).toBeVisible();

  // El starter carga pero no pasa ningún test.
  await page.getByRole('button', { name: 'Comprobar' }).click();
  await expect(
    page.getByText(/Descargando el intérprete|Cargando paquetes|Preparando ragkit/),
  ).toBeVisible();
  const summary = page.getByRole('heading', { name: /tests superados/ });
  await expect(summary).toHaveText(/^0 de \d+ tests superados$/, LOAD);
  await expect(
    page.getByText(/NotImplementedError: Completa cosine_similarity/).first(),
  ).toBeVisible();

  // Los tests ocultos aparecen con nombre genérico.
  await expect(page.getByText('Caso adicional 1')).toBeVisible();

  // Con menos de 3 intentos fallidos pide confirmación antes de enseñar la solución.
  await page.getByRole('button', { name: 'Ver solución' }).click();
  await expect(page.getByRole('alertdialog')).toContainText('Todavía no has agotado tus intentos');
  await page.getByRole('button', { name: 'Sí', exact: true }).click();
  await expect(page.getByRole('region', { name: 'Solución de referencia' })).toBeVisible();
  await page.getByRole('button', { name: 'Cargar en el editor' }).click();

  // Con la solución cargada, todos los tests pasan.
  await page.getByRole('button', { name: 'Comprobar' }).click();
  await expect(summary).toHaveText(/^(\d+) de \1 tests superados$/, LOAD);
  await expect(page.getByText('✓ Laboratorio superado')).toBeVisible();

  const progress = await readProgress(page);
  expect(progress.labs['rag-01-coseno-topk'].status).toBe('passed');
  expect(progress.labs['rag-01-coseno-topk'].code).toContain('def cosine_top_k');

  // Al recargar se conserva el código y el estado.
  await page.reload();
  await expect(page.getByText('✓ Laboratorio superado')).toBeVisible();
  await expect(page.locator('.cm-content')).toContainText('def cosine_top_k');
});

test('Ejecutar muestra la salida del programa y los errores indican la línea', async ({ page }) => {
  await page.goto(LAB);
  await setCode(page, 'print("hola " + str(2 + 3))');
  await page.getByRole('button', { name: 'Ejecutar' }).click();
  await expect(page.getByRole('region', { name: 'Salida del programa' })).toContainText(
    'hola 5',
    LOAD,
  );

  await setCode(page, 'x = 1\ny = x / 0');
  await page.getByRole('button', { name: 'Ejecutar' }).click();
  await expect(page.getByRole('region', { name: 'Salida del programa' })).toContainText(
    'ZeroDivisionError: division by zero (línea 2 de tu código)',
  );

  await setCode(page, 'def roto(:\n    pass');
  await page.getByRole('button', { name: 'Ejecutar' }).click();
  await expect(page.getByRole('region', { name: 'Salida del programa' })).toContainText(
    'Error de sintaxis',
  );
});

test('el bloque __main__ del starter solo se ejecuta con Ejecutar, no con Comprobar', async ({
  page,
}) => {
  await page.goto(LAB);
  await page.getByRole('button', { name: 'Ejecutar' }).click();
  await expect(page.getByRole('region', { name: 'Salida del programa' })).toContainText(
    'Aún por completar',
    LOAD,
  );
});

test('un bucle infinito se detiene a los 10 s y la página sigue funcionando', async ({ page }) => {
  await page.goto(LAB);
  // Calienta Pyodide para que el tiempo medido sea solo el del bucle.
  await setCode(page, 'print("listo")');
  await page.getByRole('button', { name: 'Ejecutar' }).click();
  await expect(page.getByRole('region', { name: 'Salida del programa' })).toContainText(
    'listo',
    LOAD,
  );

  await setCode(page, 'while True: pass');
  await page.getByRole('button', { name: 'Ejecutar' }).click();
  await expect(page.getByRole('region', { name: 'Salida del programa' })).toContainText(
    'tardó más de 10 s',
    { timeout: 40_000 },
  );
  await expect(page.getByRole('button', { name: 'Ejecutar' })).toBeEnabled();

  // Se recupera: el worker se recrea y vuelve a funcionar.
  await setCode(page, 'print(1 + 1)');
  await page.getByRole('button', { name: 'Ejecutar' }).click();
  await expect(page.getByRole('region', { name: 'Salida del programa' })).toContainText('2', LOAD);
});

test('las pistas se revelan de una en una y Reiniciar restaura el starter', async ({ page }) => {
  await page.goto(LAB);
  const hint = page.getByRole('button', { name: /^Pista \(/ });
  await expect(hint).toHaveText('Pista (0/4)');
  await hint.click();
  await expect(hint).toHaveText('Pista (1/4)');
  await expect(page.getByRole('region', { name: 'Pistas' }).getByRole('listitem')).toHaveCount(1);

  await setCode(page, '# mi código');
  await page.getByRole('button', { name: 'Reiniciar' }).click();
  await page.getByRole('button', { name: 'Sí', exact: true }).click();
  await expect(page.locator('.cm-content')).toContainText('def cosine_similarity');
});

test('Tab sangra y Esc seguido de Tab saca el foco del editor', async ({ page }) => {
  await page.goto(LAB);
  await setCode(page, 'x');
  await page.locator('.cm-content').press('Tab');
  // La línea ha quedado sangrada (toHaveText normaliza espacios, así que se lee el texto crudo).
  const firstLine = await page
    .locator('.cm-line')
    .first()
    .evaluate((el) => el.textContent);
  expect(firstLine).toMatch(/^\s+x$/);
  // El foco sigue en el editor tras Tab (sangrar)...
  expect(await page.evaluate(() => !!document.activeElement?.closest('.cm-editor'))).toBe(true);
  // ...y Esc + Tab lo deja salir.
  await page.keyboard.press('Escape');
  await page.keyboard.press('Tab');
  expect(await page.evaluate(() => !!document.activeElement?.closest('.cm-editor'))).toBe(false);
});
