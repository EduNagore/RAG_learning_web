/**
 * Construye una URL interna respetando el `base` de Astro (GitHub Pages sirve
 * el sitio bajo /RAG_learning_web). Nunca escribas rutas absolutas a mano.
 *
 *   url('/teoria/')          -> /RAG_learning_web/teoria/
 *   url('py/ragkit/x.py')    -> /RAG_learning_web/py/ragkit/x.py
 */
export function url(path = ''): string {
  const base = import.meta.env.BASE_URL.replace(/\/+$/, '');
  const clean = path.replace(/^\/+/, '');
  return clean === '' ? `${base}/` : `${base}/${clean}`;
}
