import { expect, test } from '@playwright/test';

test('la portada carga bajo el base de GitHub Pages y el favicon resuelve', async ({
  page,
  request,
}) => {
  await page.goto('./');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('RAG');

  const logo = page.getByRole('img', { name: 'Logo' });
  const src = await logo.getAttribute('src');
  expect(src).toBe('/RAG_learning_web/favicon.svg');

  const res = await request.get(src!);
  expect(res.ok()).toBe(true);
});
