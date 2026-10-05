import { expect, test } from '@playwright/test';

test('la portada carga bajo el base de GitHub Pages y el favicon resuelve', async ({
  page,
  request,
}) => {
  await page.goto('./');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('RAG');

  const href = await page.locator('link[rel="icon"]').getAttribute('href');
  expect(href).toBe('/RAG_learning_web/favicon.svg');
  expect((await request.get(href!)).ok()).toBe(true);
});

test('la navegación principal enlaza bajo el base', async ({ page }) => {
  await page.goto('./');
  const hrefs = await page
    .getByRole('navigation', { name: 'Principal' })
    .getByRole('link')
    .evaluateAll((links) => links.map((a) => a.getAttribute('href')));
  expect(hrefs.length).toBeGreaterThan(0);
  for (const href of hrefs) expect(href).toMatch(/^\/RAG_learning_web\//);
});
