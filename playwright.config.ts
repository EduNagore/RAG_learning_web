import { defineConfig } from '@playwright/test';

const PORT = 4321;

export default defineConfig({
  testDir: 'tests/e2e',
  // Un solo worker: con varios Chromium arrancando a la vez en Windows aparecen parones de ~10 s
  // por test (sin causa raíz identificada). La suite es pequeña y en serie tarda segundos.
  workers: 1,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? 'github' : 'list',
  use: {
    baseURL: `http://localhost:${PORT}/RAG_learning_web/`,
    trace: 'on-first-retry',
  },
  webServer: {
    command: `pnpm preview --port ${PORT}`,
    url: `http://localhost:${PORT}/RAG_learning_web/`,
    reuseExistingServer: !process.env.CI,
  },
});
