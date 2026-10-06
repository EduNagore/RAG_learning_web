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

test('AgentLoopStepper: avanza paso a paso y el contexto crece', async ({ page }) => {
  await page.goto('teoria/m10-fundamentos-agentes/02-bucle-react-y-herramientas/');
  const widget = page.locator('h3', { hasText: 'Bucle del agente paso a paso' }).locator('..');
  await widget.scrollIntoViewIfNeeded();
  await expect(page.locator('astro-island[ssr]')).toHaveCount(0);
  const status = widget.getByRole('status');
  await expect(status).toContainText('Paso 0 de 7');

  await widget.getByRole('button', { name: 'Siguiente paso' }).click();
  await expect(status).toContainText('Paso 1 de 7');
  await expect(status).toContainText('llamadas al modelo: 1');
  await expect(widget.getByRole('list', { name: 'Pasos del agente' })).toContainText('Pensamiento');

  for (let i = 0; i < 6; i++) await widget.getByRole('button', { name: 'Siguiente paso' }).click();
  await expect(status).toContainText('Paso 7 de 7');
  await expect(status).toContainText('llamadas al modelo: 3');
  await expect(widget.getByText('Respuesta final:')).toBeVisible();
  await expect(widget.getByRole('button', { name: 'Siguiente paso' })).toBeDisabled();

  await widget.getByLabel('Escenario').selectOption('bucle');
  await expect(status).toContainText('Paso 0 de 9');
  for (let i = 0; i < 9; i++) await widget.getByRole('button', { name: 'Siguiente paso' }).click();
  await expect(widget.getByText(/Guarda de bucle: la misma llamada/)).toBeVisible();

  await widget.getByRole('button', { name: 'Reiniciar' }).click();
  await expect(status).toContainText('Paso 0 de 9');
});

test('TopologyExplorer: los canales cambian con la topología y el número de agentes', async ({
  page,
}) => {
  await page.goto('teoria/m12-multi-agente/02-topologias-y-estado-compartido/');
  const widget = page.locator('h3', { hasText: 'Explorador de topologías' }).locator('..');
  await widget.scrollIntoViewIfNeeded();
  await expect(page.locator('astro-island[ssr]')).toHaveCount(0);
  const status = widget.getByRole('status');

  await widget.getByLabel(/Agentes de trabajo/).fill('6');
  await widget.locator('select').selectOption('red');
  await expect(status).toContainText('15 canales de comunicación para 6 agentes');
  await widget.locator('select').selectOption('supervisor');
  await expect(status).toContainText('6 canales de comunicación para 6 agentes');
  await expect(status).toContainText('el supervisor');

  await widget.getByLabel(/Agentes de trabajo/).fill('9');
  await widget.locator('select').selectOption('red');
  await expect(status).toContainText('36 canales de comunicación para 9 agentes');
  await expect(widget.getByRole('img')).toHaveAttribute('aria-label', /36 canales/);
});
