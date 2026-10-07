/** Servidor estático mínimo para los e2e de sincronización: sirve una carpeta bajo /RAG_learning_web/. */
import { createReadStream, existsSync, statSync } from 'node:fs';
import { createServer } from 'node:http';
import { extname, join, normalize } from 'node:path';

const [dir = 'dist-sync', port = '4322'] = process.argv.slice(2);
const BASE = '/RAG_learning_web/';
const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.wasm': 'application/wasm',
  '.xml': 'application/xml',
};

createServer((req, res) => {
  const pathname = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  if (!pathname.startsWith(BASE)) {
    res.writeHead(404).end('Not found');
    return;
  }
  let file = normalize(join(dir, pathname.slice(BASE.length)));
  if (!file.startsWith(normalize(dir))) {
    res.writeHead(403).end();
    return;
  }
  if (existsSync(file) && statSync(file).isDirectory()) file = join(file, 'index.html');
  if (!existsSync(file)) {
    res.writeHead(404).end('Not found');
    return;
  }
  res.writeHead(200, { 'content-type': TYPES[extname(file)] ?? 'application/octet-stream' });
  createReadStream(file).pipe(res);
}).listen(Number(port), () => console.log(`sirviendo ${dir} en http://localhost:${port}${BASE}`));
