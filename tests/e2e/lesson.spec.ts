import { expect, test, type Page } from '@playwright/test';

/** Abre la primera lección del índice de teoría (no depende de un id concreto). */
async function openFirstLesson(page: Page) {
  await page.goto('teoria/');
  await page.locator('[data-module-progress] ol a').first().click();
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
}

test('el índice de teoría lista módulos y lleva a una lección', async ({ page }) => {
  await openFirstLesson(page);
  await expect(page).toHaveURL(/\/RAG_learning_web\/teoria\/.+\/.+\//);
  await expect(page.getByRole('navigation', { name: 'Migas de pan' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Fuentes' })).toBeVisible();
});

test('el tema oscuro se alterna y persiste tras recargar', async ({ page }) => {
  await page.goto('./');
  const html = page.locator('html');
  const before = await html.evaluate((el) => el.classList.contains('dark'));
  await page.getByRole('button', { name: /tema claro y oscuro/i }).click();
  expect(await html.evaluate((el) => el.classList.contains('dark'))).toBe(!before);
  await page.reload();
  expect(await html.evaluate((el) => el.classList.contains('dark'))).toBe(!before);
});

test('marcar una lección como leída persiste y se refleja en el índice', async ({ page }) => {
  await openFirstLesson(page);
  const toggle = page.getByRole('button', { name: /leída/i });
  await expect(toggle).toHaveAttribute('aria-pressed', 'false');
  await toggle.click();
  await expect(toggle).toHaveAttribute('aria-pressed', 'true');

  await page.reload();
  await expect(page.getByRole('button', { name: /leída/i })).toHaveAttribute(
    'aria-pressed',
    'true',
  );

  await page.goto('teoria/');
  await expect(page.locator('[data-lesson-id][data-read="true"]').first()).toBeVisible();
  await expect(page.locator('[data-module-progress] [data-count]').first()).toHaveText(/^[1-9]\//);
});

test('las fórmulas KaTeX y los diagramas Mermaid se renderizan', async ({ page }) => {
  await openFirstLesson(page);
  await expect(page.locator('.katex').first()).toBeVisible();
  const diagram = page.locator('.mermaid-diagram').first();
  await diagram.scrollIntoViewIfNeeded();
  await expect(diagram.locator('svg')).toBeVisible({ timeout: 15_000 });
});

test('la web carga sin errores de consola', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
  await openFirstLesson(page);
  // Mermaid se carga en diferido: hay que llevar el diagrama a la vista para que se dibuje.
  await page.locator('.mermaid-diagram').first().scrollIntoViewIfNeeded();
  await page.locator('.mermaid-diagram svg').first().waitFor({ timeout: 15_000 });
  expect(errors).toEqual([]);
});

test('en móvil la lección no desborda horizontalmente', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 800 });
  await openFirstLesson(page);
  await page.locator('.mermaid-diagram').first().scrollIntoViewIfNeeded();
  await page.locator('.mermaid-diagram svg').first().waitFor({ timeout: 15_000 });
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
  expect(overflow).toBeLessThanOrEqual(1);
});
