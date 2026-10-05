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
