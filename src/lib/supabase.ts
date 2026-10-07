/**
 * Adaptador de Supabase: configuración, cliente (se carga bajo demanda) y `SyncBackend`.
 *
 * La clave pública (`PUBLIC_SUPABASE_ANON_KEY`) está pensada para el navegador: la seguridad la dan
 * las políticas RLS de `supabase/schema.sql` (cada persona solo accede a su fila). Sin las dos
 * variables, la sincronización queda desactivada y el sitio funciona como siempre.
 */
import type { SupabaseClient } from '@supabase/supabase-js';
import { parseProgress, type Progress } from './progress';
import { NetworkError, type PushResult, type RemoteSnapshot, type SyncBackend } from './sync';

export const SUPABASE_URL: string = import.meta.env.PUBLIC_SUPABASE_URL ?? '';
export const SUPABASE_ANON_KEY: string = import.meta.env.PUBLIC_SUPABASE_ANON_KEY ?? '';
export const isSyncConfigured = (): boolean => Boolean(SUPABASE_URL && SUPABASE_ANON_KEY);

/** Clave de localStorage donde supabase-js guarda la sesión (la usamos para no cargarlo sin sesión). */
export const AUTH_STORAGE_KEY = 'rma:supabase-auth';
const TABLE = 'progress';
const UNIQUE_VIOLATION = '23505';

let clientPromise: Promise<SupabaseClient> | null = null;

/** Importa supabase-js solo cuando hace falta (no pesa en las páginas sin sesión). */
export function getClient(): Promise<SupabaseClient> {
  clientPromise ??= import('@supabase/supabase-js').then(({ createClient }) =>
    createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true,
        flowType: 'implicit',
        storageKey: AUTH_STORAGE_KEY,
      },
    }),
  );
  return clientPromise;
}

interface PgError {
  code?: string;
  message: string;
}

/** Los fallos de red de fetch llegan como TypeError («Failed to fetch»): se tratan como sin conexión. */
function toError(error: PgError | Error): Error {
  if (
    error instanceof TypeError ||
    /failed to fetch|networkerror|load failed/i.test(error.message)
  ) {
    return new NetworkError(error.message);
  }
  return error instanceof Error ? error : new Error(error.message);
}

/** Backend de sincronización sobre la tabla `progress` (una fila por usuario). */
export function createSupabaseBackend(client: SupabaseClient, userId: string): SyncBackend {
  return {
    async fetch(): Promise<RemoteSnapshot> {
      try {
        const { data, error } = await client
          .from(TABLE)
          .select('data, revision')
          .eq('user_id', userId)
          .maybeSingle();
        if (error) throw toError(error);
        if (!data) return { data: null, version: null };
        return { data: parseProgress(JSON.stringify(data.data)), version: String(data.revision) };
      } catch (e) {
        throw toError(e as Error);
      }
    },

    async push(progress: Progress, baseVersion: string | null): Promise<PushResult> {
      try {
        if (baseVersion === null) {
          const { data, error } = await client
            .from(TABLE)
            .insert({ user_id: userId, data: progress, schema_version: progress.version })
            .select('revision')
            .single();
          if (error?.code === UNIQUE_VIOLATION) return { ok: false, conflict: true };
          if (error) throw toError(error);
          return { ok: true, version: String(data.revision) };
        }
        // Actualización condicionada a la revisión que vimos: si otro dispositivo se adelantó,
        // no actualiza ninguna fila y el motor vuelve a fusionar.
        const { data, error } = await client
          .from(TABLE)
          .update({ data: progress, schema_version: progress.version })
          .eq('user_id', userId)
          .eq('revision', Number(baseVersion))
          .select('revision');
        if (error) throw toError(error);
        if (!data || data.length === 0) return { ok: false, conflict: true };
        return { ok: true, version: String(data[0].revision) };
      } catch (e) {
        throw toError(e as Error);
      }
    },

    async deleteRemote(): Promise<void> {
      try {
        const { error } = await client.from(TABLE).delete().eq('user_id', userId);
        if (error) throw toError(error);
      } catch (e) {
        throw toError(e as Error);
      }
    },
  };
}
