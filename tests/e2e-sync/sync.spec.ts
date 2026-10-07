import AxeBuilder from '@axe-core/playwright';
import { expect, test, type Browser, type Page } from '@playwright/test';
import { AUTH_KEY, FakeSupabase, PROGRESS_KEY, makeSession } from './fakeSupabase';

const iso = (n: number) => new Date(Date.UTC(2026, 9, 1, 0, 0, n)).toISOString();

interface Seed {
  lessonsRead?: Record<string, string>;
  quizScores?: Record<string, unknown>;
  resetAt?: string;
}

/** Un «dispositivo»: contexto de navegador propio, sesión iniciada y un progreso local de partida. */
async function device(browser: Browser, server: FakeSupabase, seed: Seed = {}, signedIn = true) {
  const context = await browser.newContext();
  await server.install(context);
  await context.addInitScript(
    ([progressKey, authKey, progress, session]) => {
      // Solo siembra la primera vez: así una recarga conserva lo que el propio sitio haya guardado.
      if (localStorage.getItem('seeded') === null) {
        localStorage.setItem('seeded', '1');
        localStorage.setItem(progressKey, progress);
        if (session) localStorage.setItem(authKey, session);
      }
    },
    [
      PROGRESS_KEY,
      AUTH_KEY,
      JSON.stringify({
        version: 2,
        unread: {},
        labs: {},
        srs: {},
        exams: [],
        lessonsRead: {},
        quizScores: {},
        ...seed,
      }),
      signedIn ? JSON.stringify(makeSession(server.user)) : '',
    ] as const,
  );
  const page = await context.newPage();
  return { context, page };
}

const local = (page: Page) =>
  page.evaluate((k) => JSON.parse(localStorage.getItem(k) ?? 'null'), PROGRESS_KEY);

const badge = (page: Page) => page.getByTestId('sync-badge');

async function waitIdle(page: Page) {
  await expect(badge(page)).toHaveAttribute('data-state', 'idle', { timeout: 15_000 });
}

test('dos dispositivos que progresan por separado acaban con el progreso fusionado', async ({
  browser,
}) => {
  const server = new FakeSupabase();
  const a = await device(browser, server, { lessonsRead: { 'm00/01': iso(1) } });
  await a.page.goto('progreso/');
  await waitIdle(a.page);
  expect(Object.keys((server.rows.get('user-1')!.data as Seed).lessonsRead!)).toEqual(['m00/01']);

  const b = await device(browser, server, {
    lessonsRead: { 'm00/02': iso(2) },
    quizScores: { 'm00/02': { best: 80, last: 80, attempts: 1, updatedAt: iso(3) } },
  });
  await b.page.goto('progreso/');
  await waitIdle(b.page);
  const mergedB = await local(b.page);
  expect(Object.keys(mergedB.lessonsRead).sort()).toEqual(['m00/01', 'm00/02']);
  expect(mergedB.quizScores['m00/02'].best).toBe(80);

  // El dispositivo A recibe lo de B con «Sincronizar ahora» y no pierde lo suyo.
  await a.page.getByRole('button', { name: 'Sincronizar ahora' }).click();
  await waitIdle(a.page);
  const mergedA = await local(a.page);
  expect(Object.keys(mergedA.lessonsRead).sort()).toEqual(['m00/01', 'm00/02']);
  expect(mergedA.quizScores['m00/02'].best).toBe(80);
  await a.context.close();
  await b.context.close();
});

test('sin conexión no se pierde nada y al volver la red se sube lo pendiente', async ({
  browser,
}) => {
  const server = new FakeSupabase();
  const a = await device(browser, server, { lessonsRead: { 'm00/01': iso(1) } });
  await a.page.goto('progreso/');
  await waitIdle(a.page);

  server.offline = true;
  // El usuario sigue estudiando: marca una lección (en la propia página de la lección).
  await a.page.goto('teoria/m00-fundamentos-llm/01-tokens-y-contexto/');
  await a.page
    .getByRole('button', { name: /Marcar como leída/ })
    .first()
    .click();
  await expect(badge(a.page)).toHaveAttribute('data-state', /pending|offline/, { timeout: 15_000 });
  await expect(badge(a.page)).toHaveAttribute('data-state', 'offline', { timeout: 15_000 });
  const during = await local(a.page);
  expect(Object.keys(during.lessonsRead).sort()).toEqual([
    'm00-fundamentos-llm/01-tokens-y-contexto',
    'm00/01',
  ]);
  expect(Object.keys((server.rows.get('user-1')!.data as Seed).lessonsRead!)).toEqual(['m00/01']);

  server.offline = false;
  await a.page.goto('progreso/');
  await a.page.getByRole('button', { name: 'Sincronizar ahora' }).click();
  await waitIdle(a.page);
  expect(Object.keys((server.rows.get('user-1')!.data as Seed).lessonsRead!).sort()).toEqual([
    'm00-fundamentos-llm/01-tokens-y-contexto',
    'm00/01',
  ]);
  await a.context.close();
});

test('iniciar sesión con el código del correo y recibir el progreso guardado', async ({
  browser,
}) => {
  const server = new FakeSupabase();
  server.rows.set('user-1', {
    data: {
      version: 2,
      lessonsRead: { 'm05/01': iso(5) },
      unread: {},
      quizScores: {},
      labs: {},
      srs: {},
      exams: [],
    },
    revision: 4,
  });
  const d = await device(browser, server, {}, false);
  await d.page.goto('progreso/');
  await expect(d.page.getByTestId('sync-status')).toHaveText('Sin sesión iniciada.');

  await d.page.getByLabel('Correo electrónico').fill('ana@example.com');
  await d.page.getByRole('button', { name: 'Enviarme el enlace' }).click();
  await expect(d.page.getByTestId('sync-sent')).toContainText('ana@example.com');
  expect(server.otpEmails).toEqual(['ana@example.com']);

  await d.page.getByLabel('Código').fill('000000');
  await d.page.getByRole('button', { name: 'Entrar con el código' }).click();
  await expect(d.page.getByRole('alert')).toContainText(/invalid|expired/i);

  await d.page.getByLabel('Código').fill('123456');
  await d.page.getByRole('button', { name: 'Entrar con el código' }).click();
  await expect(d.page.getByText('Sesión iniciada como')).toBeVisible();
  await waitIdle(d.page);
  expect(server.verifyBodies.at(-1)).toMatchObject({
    email: 'ana@example.com',
    token: '123456',
    type: 'email',
  });
  expect(Object.keys((await local(d.page)).lessonsRead)).toEqual(['m05/01']);
  await d.context.close();
});

test('reiniciar con la sesión iniciada llega a la nube y a los demás dispositivos', async ({
  browser,
}) => {
  const server = new FakeSupabase();
  const a = await device(browser, server, { lessonsRead: { 'm00/01': iso(1) } });
  await a.page.goto('progreso/');
  await waitIdle(a.page);
  const b = await device(browser, server);
  await b.page.goto('progreso/');
  await waitIdle(b.page);
  expect(Object.keys((await local(b.page)).lessonsRead)).toEqual(['m00/01']);

  await a.page.getByRole('button', { name: 'Reiniciar progreso' }).click();
  await expect(a.page.getByRole('alertdialog')).toContainText('también en la nube');
  await a.page.getByRole('button', { name: 'Sí, borrar' }).click();
  await expect(badge(a.page)).toHaveAttribute('data-state', 'pending');
  await a.page.getByRole('button', { name: 'Sincronizar ahora' }).click();
  await waitIdle(a.page);
  expect((server.rows.get('user-1')!.data as Seed).resetAt).toBeTruthy();

  await b.page.getByRole('button', { name: 'Sincronizar ahora' }).click();
  await waitIdle(b.page);
  expect((await local(b.page)).lessonsRead).toEqual({});
  await a.context.close();
  await b.context.close();
});

test('borrar mi copia en la nube elimina la fila, cierra la sesión y conserva lo local', async ({
  browser,
}) => {
  const server = new FakeSupabase();
  const d = await device(browser, server, { lessonsRead: { 'm00/01': iso(1) } });
  await d.page.goto('progreso/');
  await waitIdle(d.page);
  expect(server.rows.has('user-1')).toBe(true);

  await d.page.getByRole('button', { name: 'Borrar mi copia en la nube' }).click();
  await d.page.getByRole('button', { name: 'Sí, borrar mi copia en la nube' }).click();
  await expect(d.page.getByTestId('sync-status')).toHaveText('Sin sesión iniciada.');
  expect(server.rows.has('user-1')).toBe(false);
  expect(Object.keys((await local(d.page)).lessonsRead)).toEqual(['m00/01']);
  await d.context.close();
});

test('cerrar sesión puede borrar el progreso de este dispositivo (equipos compartidos)', async ({
  browser,
}) => {
  const server = new FakeSupabase();
  const d = await device(browser, server, { lessonsRead: { 'm00/01': iso(1) } });
  await d.page.goto('progreso/');
  await waitIdle(d.page);
  await d.page.getByRole('button', { name: 'Cerrar sesión' }).click();
  await d.page
    .getByRole('button', { name: 'Borrarlo de este dispositivo y cerrar sesión' })
    .click();
  await expect(d.page.getByTestId('sync-status')).toHaveText('Sin sesión iniciada.');
  expect((await local(d.page)).lessonsRead).toEqual({});
  // La copia de la nube sigue intacta: al volver a entrar se recupera.
  expect(Object.keys((server.rows.get('user-1')!.data as Seed).lessonsRead!)).toEqual(['m00/01']);
  await d.context.close();
});

test('sin sesión no se hace ninguna petición a Supabase', async ({ browser }) => {
  const server = new FakeSupabase();
  const d = await device(browser, server, { lessonsRead: { 'm00/01': iso(1) } }, false);
  const seen: string[] = [];
  d.context.on('request', (r) => {
    if (r.url().includes('127.0.0.1:54321')) seen.push(r.url());
  });
  await d.page.goto('teoria/');
  await d.page.goto('progreso/');
  await expect(d.page.getByTestId('sync-status')).toBeVisible();
  expect(seen).toEqual([]);
  expect(server.tableCalls).toEqual([]);
  await d.context.close();
});

test('el panel de sincronización y la cabecera son accesibles (axe) en ambos temas, con y sin sesión', async ({
  browser,
}) => {
  const server = new FakeSupabase();
  for (const signedIn of [false, true]) {
    for (const theme of ['light', 'dark']) {
      const d = await device(browser, server, { lessonsRead: { 'm00/01': iso(1) } }, signedIn);
      await d.context.addInitScript((t) => localStorage.setItem('rma:theme', t), theme);
      await d.page.goto('progreso/');
      await expect(d.page.getByTestId('sync-status')).toBeVisible();
      if (signedIn) await waitIdle(d.page);
      const results = await new AxeBuilder({ page: d.page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
        .analyze();
      expect(
        results.violations.map((v) => `${v.id}: ${v.nodes[0].target.join(' ')}`),
        `${signedIn ? 'con' : 'sin'} sesión, tema ${theme}`,
      ).toEqual([]);
      await d.context.close();
    }
  }
});

test('volver desde el enlace del correo inicia la sesión y descarga el progreso', async ({
  browser,
}) => {
  const server = new FakeSupabase();
  server.rows.set('user-1', {
    data: {
      version: 2,
      lessonsRead: { 'm07/01': iso(7) },
      unread: {},
      quizScores: {},
      labs: {},
      srs: {},
      exams: [],
    },
    revision: 2,
  });
  const d = await device(browser, server, {}, false);
  const s = makeSession(server.user);
  const hash = new URLSearchParams({
    access_token: s.access_token,
    refresh_token: s.refresh_token,
    expires_in: String(s.expires_in),
    expires_at: String(s.expires_at),
    token_type: 'bearer',
    type: 'magiclink',
  }).toString();
  await d.page.goto(`progreso/#${hash}`);
  await expect(d.page.getByText('Sesión iniciada como')).toBeVisible();
  await waitIdle(d.page);
  expect(Object.keys((await local(d.page)).lessonsRead)).toEqual(['m07/01']);
  await d.context.close();
});
