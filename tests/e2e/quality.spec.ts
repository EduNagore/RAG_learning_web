import { expect, test } from '@playwright/test';

test('Pyodide solo se descarga en los laboratorios', async ({ page }) => {
  const pyodideRequests: string[] = [];
  page.on('request', (r) => {
    if (/cdn\.jsdelivr\.net\/pyodide|pyodide[^/]*\.(m?js|wasm)(\?|$)/i.test(r.url())) {
      pyodideRequests.push(r.url());
    }
  });
  for (const route of [
    '',
    'teoria/m10-fundamentos-agentes/02-bucle-react-y-herramientas/',
    'practica/labs/',
    'practica/playground/',
    'entrevistas/',
  ]) {
    await page.goto(route);
    await page.waitForLoadState('networkidle');
  }
  expect(pyodideRequests).toEqual([]);
});

test('SEO: cada tipo de página tiene título, descripción, canónica y Open Graph', async ({
  page,
}) => {
  for (const route of [
    '',
    'teoria/m18-system-design/03-que-distingue-un-diseno-senior/',
    'entrevistas/system-design/01-soporte-sobre-documentacion-interna/',
    'proyectos/01-rag-produccion/',
    'glosario/',
  ]) {
    await page.goto(route);
    await expect(page).toHaveTitle(/\S+/);
    for (const selector of [
      'meta[name="description"]',
      'link[rel="canonical"]',
      'meta[property="og:title"]',
      'meta[property="og:description"]',
    ]) {
      await expect(page.locator(selector)).toHaveCount(1);
    }
    const description = await page.locator('meta[name="description"]').getAttribute('content');
    expect(description!.length).toBeGreaterThan(30);
  }
});

test('El sitemap incluye las secciones de F6', async ({ request, baseURL }) => {
  const index = await request.get(`${baseURL}sitemap-index.xml`);
  expect(index.ok()).toBe(true);
  const sitemapUrl = (await index.text()).match(/<loc>([^<]+)<\/loc>/)![1];
  // El índice apunta al sitio publicado; se lee el mismo fichero del servidor local.
  const sitemap = await request.get(`${baseURL}${sitemapUrl.split('/').pop()}`);
  const xml = await sitemap.text();
  for (const path of [
    '/entrevistas/',
    '/glosario/',
    '/fuentes/',
    '/hojas/agentes/',
    '/proyectos/',
  ]) {
    expect(xml).toContain(path);
  }
});
