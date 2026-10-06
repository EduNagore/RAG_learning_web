import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { expect, test } from '@playwright/test';

const corpus = JSON.parse(
  readFileSync(resolve(process.cwd(), 'public/data/nimbus/corpus.json'), 'utf8'),
) as { id: string; access: string }[];
const publicIds = new Set(corpus.filter((d) => d.access === 'public').map((d) => d.id));

test('Playground: usa la clave solo contra la API, filtra por permisos y permite borrarla', async ({
  page,
}) => {
  let seen: { key?: string; body?: string; url?: string } = {};
  await page.route('https://api.anthropic.com/v1/messages', async (route) => {
    const request = route.request();
    seen = {
      key: request.headers()['x-api-key'],
      body: request.postData() ?? '',
      url: request.url(),
    };
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      headers: { 'access-control-allow-origin': '*' },
      body: JSON.stringify({
        content: [
          { type: 'text', text: 'El plazo es de 14 días naturales [doc-001] y [doc-999].' },
        ],
        usage: { input_tokens: 321, output_tokens: 17 },
      }),
    });
  });

  await page.goto('practica/playground/');
  await expect(page.getByRole('note')).toContainText('límite de gasto');
  const ask = page.getByRole('button', { name: 'Preguntar' });
  await expect(ask).toBeDisabled();

  await page.getByLabel('Clave de API').fill('sk-ant-prueba-1234567890');
  await page.getByLabel('Recordar la clave en este navegador').check();
  await expect(ask).toBeEnabled();
  await ask.click();

  await expect(page.getByTestId('answer')).toContainText('14 días naturales');
  await expect(page.locator('p[role="status"]')).toContainText(
    'Tokens: 321 de entrada y 17 de salida',
  );
  await expect(page.locator('p[role="status"]')).toContainText('doc-999');
  expect(seen.key).toBe('sk-ant-prueba-1234567890');
  expect(seen.url).toBe('https://api.anthropic.com/v1/messages');
  expect(seen.body).not.toContain('sk-ant-prueba');
  // El perfil público nunca envía documentos internos ni restringidos al modelo.
  const prompt = JSON.parse(seen.body!).messages[0].content as string;
  expect(prompt).toContain('Pregunta: ¿Cuál es el plazo de devolución');
  const ids = [...prompt.matchAll(/<documento id="(doc-\d+)"/g)].map((m) => m[1]);
  expect(ids.length).toBe(3);
  for (const id of ids) expect(publicIds.has(id)).toBe(true);

  // La clave recordada vive en localStorage y se borra con el botón.
  expect(await page.evaluate(() => localStorage.getItem('playground:apiKey'))).toBe(
    'sk-ant-prueba-1234567890',
  );
  await page.getByRole('button', { name: 'Borrar la clave' }).click();
  expect(await page.evaluate(() => localStorage.getItem('playground:apiKey'))).toBeNull();
  await expect(page.getByLabel('Clave de API')).toHaveValue('');
});

test('Playground: muestra el error de la API sin romperse', async ({ page }) => {
  await page.route('https://api.anthropic.com/v1/messages', (route) =>
    route.fulfill({
      status: 401,
      contentType: 'application/json',
      headers: { 'access-control-allow-origin': '*' },
      body: JSON.stringify({
        type: 'error',
        error: { type: 'authentication_error', message: 'clave inválida' },
      }),
    }),
  );
  await page.goto('practica/playground/');
  await page.getByLabel('Clave de API').fill('sk-ant-mala-0000000000');
  await page.getByRole('button', { name: 'Preguntar' }).click();
  await expect(page.getByRole('alert')).toContainText('clave inválida');
});
