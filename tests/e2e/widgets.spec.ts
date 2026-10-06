import { expect, test } from '@playwright/test';

test('ChunkingVisualizer: reacciona a la estrategia y a los controles', async ({ page }) => {
  await page.goto('teoria/m02-ingesta-chunking/02-estrategias-de-chunking/');
  const widget = page.locator('h3', { hasText: 'Visualizador de chunking' }).locator('..');
  await widget.scrollIntoViewIfNeeded();
  const status = widget.getByRole('status');
  await expect(status).toContainText(/\d+ fragmentos/);

  // La isla se renderiza en servidor y se hidrata al hacerse visible: se reintenta hasta que responda.
  await expect(async () => {
    await widget.getByLabel('Estrategia').selectOption('fixed');
    await expect(widget.getByText(/Tamaño: \d+ palabras/)).toBeVisible({ timeout: 500 });
  }).toPass();
  const before = await status.textContent();

  await widget.getByLabel(/Tamaño:/).fill('10');
  await expect(status).not.toHaveText(before!);
  await expect(widget.getByText(/Lo resaltado en amarillo es el solape/)).toBeVisible();

  await widget.getByLabel('Estrategia').selectOption('markdown');
  await expect(widget.getByText(/ruta: Devoluciones > Plazos/)).toBeVisible();
});

test('RRFCalculator: la constante k cambia el documento ganador', async ({ page }) => {
  await page.goto('teoria/m05-recuperacion-avanzada/01-busqueda-hibrida-y-rrf/');
  const widget = page.locator('h3', { hasText: 'Calculadora de RRF' }).locator('..');
  await widget.scrollIntoViewIfNeeded();
  // Las islas con client:visible pierden el atributo `ssr` cuando se hidratan.
  await expect(page.locator('astro-island[ssr]')).toHaveCount(0);
  const status = widget.getByRole('status');

  await widget.getByLabel('Búsqueda léxica (BM25)').fill('A, B, D');
  await widget.getByLabel('Búsqueda densa').fill('C, E, B, F');
  await widget.getByLabel(/Constante k/).fill('0');
  await expect(status).toContainText('Primero: A');
  await expect(status).toContainText('6 documentos');

  await widget.getByLabel(/Constante k/).fill('60');
  await expect(status).toContainText('Primero: B');
  await expect(widget.getByRole('table', { name: 'Resultado de la fusión RRF' })).toBeVisible();
});
