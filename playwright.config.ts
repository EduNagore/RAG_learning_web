import { defineConfig } from '@playwright/test';

const PORT = 4321;
// E2E_BASE_URL permite pasar los tests contra un sitio ya desplegado (humo en producción):
//   $env:E2E_BASE_URL='https://edunagore.github.io/RAG_learning_web/'; pnpm test:e2e
// Debe terminar en barra. En ese caso no se levanta el servidor local.
const external = process.env.E2E_BASE_URL;
const local = `http://localhost:${PORT}/RAG_learning_web/`;

export default defineConfig({
  testDir: 'tests/e2e',
  // Un solo worker: con varios Chromium arrancando a la vez en Windows aparecen parones de ~10 s
  // por test (sin causa raíz identificada). La suite es pequeña y en serie tarda segundos.
  workers: 1,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? 'github' : 'list',
  // Contra un sitio remoto la hidratación de las islas tarda más que en local.
  expect: { timeout: external ? 15_000 : 5_000 },
  use: {
    baseURL: external ?? local,
    trace: 'on-first-retry',
  },
  webServer: external
    ? undefined
    : {
        command: `pnpm preview --port ${PORT}`,
        url: local,
        reuseExistingServer: !process.env.CI,
      },
});
