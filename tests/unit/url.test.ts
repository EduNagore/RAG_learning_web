import { afterEach, describe, expect, it, vi } from 'vitest';
import { url } from '../../src/lib/url';

describe('url()', () => {
  afterEach(() => vi.unstubAllEnvs());

  it('antepone el base de GitHub Pages', () => {
    vi.stubEnv('BASE_URL', '/RAG_learning_web');
    expect(url('/teoria/')).toBe('/RAG_learning_web/teoria/');
    expect(url('py/ragkit/text.py')).toBe('/RAG_learning_web/py/ragkit/text.py');
  });

  it('tolera un base con barra final', () => {
    vi.stubEnv('BASE_URL', '/RAG_learning_web/');
    expect(url('favicon.svg')).toBe('/RAG_learning_web/favicon.svg');
  });

  it('devuelve la raíz del sitio sin argumentos', () => {
    vi.stubEnv('BASE_URL', '/RAG_learning_web');
    expect(url()).toBe('/RAG_learning_web/');
    expect(url('/')).toBe('/RAG_learning_web/');
  });

  it('funciona con base raíz (desarrollo sin base)', () => {
    vi.stubEnv('BASE_URL', '/');
    expect(url('/practica/')).toBe('/practica/');
    expect(url()).toBe('/');
  });
});
