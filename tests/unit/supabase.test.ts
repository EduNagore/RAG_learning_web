import type { SupabaseClient } from '@supabase/supabase-js';
import { describe, expect, it } from 'vitest';
import { createSupabaseBackend } from '../../src/lib/supabase';
import { emptyProgress, withLessonRead } from '../../src/lib/progress';
import { NetworkError } from '../../src/lib/sync';

interface Call {
  op: string;
  args: unknown[];
}

/** Cliente falso: registra la cadena de llamadas y devuelve el resultado configurado. */
function fakeClient(result: unknown) {
  const calls: Call[] = [];
  const chain = (): unknown =>
    new Proxy(() => {}, {
      get(_t, prop) {
        if (prop === 'then') return (resolve: (v: unknown) => void) => resolve(result);
        return (...args: unknown[]) => {
          calls.push({ op: String(prop), args });
          return chain();
        };
      },
    });
  return { client: { from: () => chain() } as unknown as SupabaseClient, calls };
}

const ops = (calls: Call[]) => calls.map((c) => c.op);

describe('createSupabaseBackend', () => {
  it('fetch sin fila devuelve datos nulos y versión nula', async () => {
    const { client, calls } = fakeClient({ data: null, error: null });
    const snapshot = await createSupabaseBackend(client, 'u1').fetch();
    expect(snapshot).toEqual({ data: null, version: null });
    expect(calls.find((c) => c.op === 'eq')!.args).toEqual(['user_id', 'u1']);
  });

  it('fetch con fila interpreta el progreso (también el de la v1) y devuelve la revisión', async () => {
    const stored = { version: 1, lessonsRead: { a: '2026-10-01T00:00:00.000Z' } };
    const { client } = fakeClient({ data: { data: stored, revision: 7 }, error: null });
    const snapshot = await createSupabaseBackend(client, 'u1').fetch();
    expect(snapshot.version).toBe('7');
    expect(Object.keys(snapshot.data!.lessonsRead)).toEqual(['a']);
    expect(snapshot.data!.version).toBe(2);
  });

  it('la primera subida inserta con el usuario y un choque de clave única es un conflicto', async () => {
    const ok = fakeClient({ data: { revision: 1 }, error: null });
    const p = withLessonRead(emptyProgress(), 'a', new Date());
    await expect(createSupabaseBackend(ok.client, 'u1').push(p, null)).resolves.toEqual({
      ok: true,
      version: '1',
    });
    expect(ops(ok.calls)).toEqual(['insert', 'select', 'single']);
    expect(ok.calls[0].args[0]).toMatchObject({ user_id: 'u1', schema_version: 2 });

    const dup = fakeClient({ data: null, error: { code: '23505', message: 'duplicate key' } });
    await expect(createSupabaseBackend(dup.client, 'u1').push(p, null)).resolves.toEqual({
      ok: false,
      conflict: true,
    });
  });

  it('actualizar condiciona por usuario y revisión; sin filas actualizadas es un conflicto', async () => {
    const p = emptyProgress();
    const ok = fakeClient({ data: [{ revision: 5 }], error: null });
    await expect(createSupabaseBackend(ok.client, 'u1').push(p, '4')).resolves.toEqual({
      ok: true,
      version: '5',
    });
    const eqs = ok.calls.filter((c) => c.op === 'eq').map((c) => c.args);
    expect(eqs).toEqual([
      ['user_id', 'u1'],
      ['revision', 4],
    ]);

    const stale = fakeClient({ data: [], error: null });
    await expect(createSupabaseBackend(stale.client, 'u1').push(p, '4')).resolves.toEqual({
      ok: false,
      conflict: true,
    });
  });

  it('los errores de red se convierten en NetworkError y los demás conservan su mensaje', async () => {
    const net = fakeClient({ data: null, error: { message: 'TypeError: Failed to fetch' } });
    await expect(createSupabaseBackend(net.client, 'u1').fetch()).rejects.toBeInstanceOf(
      NetworkError,
    );
    const denied = fakeClient({
      data: null,
      error: { code: '42501', message: 'permission denied' },
    });
    await expect(createSupabaseBackend(denied.client, 'u1').fetch()).rejects.toThrow(
      'permission denied',
    );
  });

  it('deleteRemote borra solo la fila del usuario', async () => {
    const { client, calls } = fakeClient({ error: null });
    await createSupabaseBackend(client, 'u1').deleteRemote();
    expect(ops(calls)).toEqual(['delete', 'eq']);
    expect(calls[1].args).toEqual(['user_id', 'u1']);
  });
});
