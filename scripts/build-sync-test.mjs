/** Construye el sitio con la sincronización activada y una URL de Supabase FALSA (solo para los e2e). */
import { spawnSync } from 'node:child_process';

const result = spawnSync('pnpm', ['exec', 'astro', 'build', '--outDir', 'dist-sync'], {
  stdio: 'inherit',
  shell: true,
  env: {
    ...process.env,
    PUBLIC_SUPABASE_URL: 'http://127.0.0.1:54321',
    PUBLIC_SUPABASE_ANON_KEY: 'clave-publica-de-prueba',
  },
});
process.exit(result.status ?? 1);
