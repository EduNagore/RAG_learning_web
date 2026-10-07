import { defineConfig } from '@playwright/test';

// E2E de la sincronización: se ejecutan contra un build aparte (dist-sync) hecho con una URL de
// Supabase falsa; el backend se simula en los tests con `page.route`. Ningún test llama a Supabase.
//   pnpm test:e2e:sync
const PORT = 4322;

export default defineConfig({
  testDir: 'tests/e2e-sync',
  workers: 1,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? 'github' : 'list',
  expect: { timeout: 8_000 },
  use: { baseURL: `http://localhost:${PORT}/RAG_learning_web/`, trace: 'on-first-retry' },
  webServer: {
    command: `node scripts/serve-static.mjs dist-sync ${PORT}`,
    url: `http://localhost:${PORT}/RAG_learning_web/`,
    reuseExistingServer: !process.env.CI,
  },
});
