import AxeBuilder from '@axe-core/playwright';
import { expect, test } from '@playwright/test';

// Páginas representativas de cada tipo; cada una se revisa con tema claro y oscuro.
const PAGES = [
  '',
  'teoria/',
  'teoria/m17-fiabilidad-seguridad/01-inyeccion-de-prompts-y-triada-letal/',
  'teoria/m12-multi-agente/02-topologias-y-estado-compartido/',
  'practica/',
  'practica/tests/',
  'practica/examen/',
  'practica/labs/',
  'practica/labs/agents-35-evaluacion-de-trayectorias/',
  'practica/playground/',
  'entrevistas/',
  'entrevistas/system-design/06-copiloto-interno-con-permisos/',
  'glosario/',
  'fuentes/',
  'hojas/agentes/',
  'proyectos/',
  'proyectos/04-servidor-mcp/',
  'progreso/',
];

test.setTimeout(240_000);

for (const theme of ['light', 'dark'] as const) {
  test(`axe: sin violaciones WCAG A/AA en el tema ${theme}`, async ({ page }) => {
    await page.addInitScript((value) => {
      try {
        localStorage.setItem('rma:theme', value);
      } catch {
        /* sin almacenamiento */
      }
    }, theme);
    const failures: string[] = [];
    for (const route of PAGES) {
      await page.goto(route);
      await page.waitForLoadState('networkidle');
      const isDark = await page.evaluate(() => document.documentElement.classList.contains('dark'));
      expect(isDark).toBe(theme === 'dark');
      const results = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
        .analyze();
      for (const v of results.violations) {
        failures.push(
          `${route || '/'} · ${v.id} (${v.impact}): ${v.nodes.length} nodo(s) · ${v.nodes[0].target.join(' ')}`,
        );
      }
    }
    expect(failures, failures.join('\n')).toEqual([]);
  });
}

test('prefers-reduced-motion: no hay animaciones ni transiciones largas', async ({ browser }) => {
  const context = await browser.newContext({ reducedMotion: 'reduce' });
  const page = await context.newPage();
  await page.goto('teoria/m10-fundamentos-agentes/02-bucle-react-y-herramientas/');
  const longest = await page.evaluate(() =>
    Math.max(
      0,
      ...[...document.querySelectorAll('*')].map((el) => {
        const s = getComputedStyle(el);
        const dur = (v: string) => Math.max(0, ...v.split(',').map((x) => parseFloat(x) || 0));
        return (
          Math.max(dur(s.animationDuration), dur(s.transitionDuration)) *
          (s.animationDuration.includes('ms') ? 0.001 : 1)
        );
      }),
    ),
  );
  expect(longest).toBeLessThanOrEqual(0.01);
  await context.close();
});
