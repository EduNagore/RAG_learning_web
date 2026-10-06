import { readdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { expect, test } from '@playwright/test';

// Cada diagrama Mermaid de cada lección y de cada caso de system design debe renderizarse (si la sintaxis falla, queda el código fuente).
const LESSONS_DIR = resolve(process.cwd(), 'src/content/lessons');
const routes = readdirSync(LESSONS_DIR).flatMap((mod) =>
  readdirSync(resolve(LESSONS_DIR, mod))
    .filter((f) => f.endsWith('.mdx'))
    .map((f) => `teoria/${mod}/${f.replace(/\.mdx$/, '')}/`),
);

const CASES_DIR = resolve(process.cwd(), 'src/content/cases');
routes.push(
  ...readdirSync(CASES_DIR)
    .filter((f) => f.endsWith('.mdx'))
    .map((f) => `entrevistas/system-design/${f.replace(/\.mdx$/, '')}/`),
);

test.setTimeout(180_000);

test('todos los diagramas Mermaid de las lecciones se renderizan', async ({ page }) => {
  const broken: string[] = [];
  for (const route of routes) {
    await page.goto(route);
    const diagrams = page.locator('.mermaid-diagram');
    const n = await diagrams.count();
    for (let i = 0; i < n; i++) {
      const diagram = diagrams.nth(i);
      await diagram.scrollIntoViewIfNeeded();
      try {
        await expect(diagram.locator('svg').first()).toBeVisible({ timeout: 10_000 });
      } catch {
        broken.push(`${route} (diagrama ${i + 1})`);
      }
    }
  }
  expect(broken, `Diagramas sin renderizar:\n${broken.join('\n')}`).toEqual([]);
});
