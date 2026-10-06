import { readdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { expect, test } from '@playwright/test';

const CASES = readdirSync(resolve(process.cwd(), 'src/content/cases')).filter((f) =>
  f.endsWith('.mdx'),
);

test('Entrevistas: filtros, idioma y flashcards', async ({ page }) => {
  await page.goto('entrevistas/');
  await expect(page.locator('astro-island[ssr]')).toHaveCount(0);
  const status = page.getByRole('status').first();
  await expect(status).toContainText(/\d+ de \d+ preguntas/);
  const total = Number((await status.textContent())!.match(/de (\d+) preguntas/)![1]);
  expect(total).toBeGreaterThanOrEqual(80);

  await page.getByLabel('Nivel').selectOption('senior');
  await expect(status).not.toContainText(`${total} de ${total}`);
  const seniors = await page.getByTestId('interview-item').count();
  expect(seniors).toBeGreaterThan(0);
  expect(seniors).toBeLessThan(total);

  // La respuesta se muestra al abrir la pregunta, y el idioma cambia el texto.
  const first = page.getByTestId('interview-item').first();
  const esQuestion = await first.locator('summary').textContent();
  await first.locator('summary').click();
  await expect(first.locator('p').nth(1)).toBeVisible();
  await page.getByLabel('Idioma').selectOption('en');
  await expect(status).toContainText(/\d+ of \d+ questions/);
  await expect(first.locator('summary')).not.toHaveText(esQuestion!);

  await page.getByLabel('Level').selectOption('all');
  await page.getByRole('button', { name: 'Flashcards' }).click();
  await expect(page.getByText(/Card 1 of/)).toBeVisible();
  await page.getByRole('button', { name: 'Show answer' }).click();
  await expect(page.getByRole('button', { name: 'Hide answer' })).toBeVisible();
  await page.getByRole('button', { name: 'Next' }).click();
  await expect(page.getByText(/Card 2 of/)).toBeVisible();
  await expect(page.getByRole('button', { name: 'Show answer' })).toBeVisible();
});

test('Entrevistas: cada caso de system design se abre con sus secciones', async ({ page }) => {
  await page.goto('entrevistas/');
  await expect(page.getByRole('link', { name: /Chatbot de soporte/ })).toBeVisible();
  for (const file of CASES) {
    await page.goto(`entrevistas/system-design/${file.replace(/\.mdx$/, '')}/`);
    for (const heading of [
      'Requisitos',
      'Arquitectura',
      'Riesgos',
      'Qué diría una persona senior',
    ]) {
      await expect(page.getByRole('heading', { name: heading, exact: true })).toBeVisible();
    }
  }
});

test('Glosario: la búsqueda ignora acentos y mezcla español e inglés', async ({ page }) => {
  await page.goto('glosario/');
  await expect(page.locator('astro-island[ssr]')).toHaveCount(0);
  const status = page.getByText(/\d+ de \d+ términos/);
  await expect(status).toBeVisible();
  const total = Number((await status.textContent())!.match(/de (\d+) términos/)![1]);
  expect(total).toBeGreaterThanOrEqual(50);

  await page.getByLabel(/Buscar un término/).fill('recuperacion contextual');
  await expect(page.getByTestId('glossary-term')).toHaveCount(1);
  await page.getByLabel(/Buscar un término/).fill('lethal trifecta');
  await expect(page.getByTestId('glossary-term').first()).toContainText('tríada letal');
  await page.getByLabel(/Buscar un término/).fill('zzzz');
  await expect(page.getByText('Ningún término coincide')).toBeVisible();
});

test('Fuentes: lista las fuentes de las lecciones agrupadas por parte', async ({ page }) => {
  await page.goto('fuentes/');
  await expect(page.getByRole('heading', { name: /Parte II/ })).toBeVisible();
  const links = page.locator('[data-testid="source-list"] > li > a');
  expect(await links.count()).toBeGreaterThan(100);
  await expect(page.getByRole('link', { name: 'Building effective agents' })).toHaveAttribute(
    'href',
    'https://www.anthropic.com/engineering/building-effective-agents',
  );
});

test('Proyectos: lista cinco guías y cada una se abre con sus secciones', async ({ page }) => {
  await page.goto('proyectos/');
  const cards = page.getByRole('main').getByRole('link', { name: /Código inicial|≈/ });
  expect(await cards.count()).toBeGreaterThanOrEqual(5);
  const ids = readdirSync(resolve(process.cwd(), 'src/content/projects')).map((f) =>
    f.replace(/\.mdx$/, ''),
  );
  for (const id of ids) {
    await page.goto(`proyectos/${id}/`);
    for (const heading of ['Objetivo', 'Arquitectura', 'Pasos', 'Criterios de evaluación']) {
      await expect(page.getByRole('heading', { name: heading, exact: true })).toBeVisible();
    }
    await expect(page.getByRole('link', { name: `projects/${id}` })).toHaveAttribute(
      'href',
      new RegExp(`projects/${id}$`),
    );
  }
});

test('Hojas de resumen: cada parte lista las ideas clave de sus lecciones', async ({ page }) => {
  await page.goto('hojas/');
  await expect(page.getByRole('link', { name: /Parte II · Agentes/ })).toBeVisible();
  await page.goto('hojas/agentes/');
  await expect(page.getByRole('heading', { name: /Hoja de resumen/ })).toBeVisible();
  expect(await page.getByTestId('sheet-points').count()).toBeGreaterThan(20);
  await expect(page.getByRole('button', { name: /Imprimir/ })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Glosario de esta parte' })).toBeVisible();
  // Sin marcas de Markdown sin resolver en las ideas clave.
  const text = await page.getByTestId('sheet-points').first().innerText();
  expect(text).not.toMatch(/\*\*|`/);
});
