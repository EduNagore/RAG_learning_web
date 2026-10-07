/**
 * Orquestación en el navegador: sesión de Supabase + motor de sincronización + estado reactivo.
 * `startSync()` es idempotente y se llama desde la cabecera en todas las páginas; sin las
 * variables de entorno o sin sesión no descarga supabase-js ni hace ninguna petición.
 */
import type { Session } from '@supabase/supabase-js';
import { $progress, mergeIntoProgress, loadProgress } from './progress';
import { AUTH_STORAGE_KEY, createSupabaseBackend, getClient, isSyncConfigured } from './supabase';
import { $sync, SyncEngine, setSyncStatus } from './sync';
import { url } from './url';

let started = false;
let engine: SyncEngine | null = null;
let unlisten: (() => void) | null = null;

function storedSession(): boolean {
  try {
    return localStorage.getItem(AUTH_STORAGE_KEY) !== null;
  } catch {
    return false;
  }
}

/** ¿Venimos de pulsar el enlace del correo? (los tokens llegan en el fragmento de la URL). */
const returningFromLink = (): boolean =>
  typeof location !== 'undefined' && /access_token=|error_code=|type=magiclink/.test(location.hash);

function stopEngine() {
  engine?.stop();
  engine = null;
  unlisten?.();
  unlisten = null;
}

function begin(session: Session) {
  stopEngine();
  setSyncStatus({ state: 'idle', email: session.user.email ?? null, error: null });
  void getClient().then((client) => {
    const backend = createSupabaseBackend(client, session.user.id);
    // Lo que llega de la nube también cambia el store: no debe programar otra subida.
    let applying = false;
    const e = new SyncEngine({
      backend,
      getLocal: () => loadProgress(),
      applyRemote: (remote) => {
        applying = true;
        try {
          mergeIntoProgress(remote);
        } finally {
          applying = false;
        }
      },
      onStatus: setSyncStatus,
    });
    engine = e;
    // Cada cambio local programa una subida con debounce.
    unlisten = $progress.listen(() => {
      if (!applying) e.notifyLocalChange();
    });
    void e.syncNow();
  });
}

export async function startSync(): Promise<void> {
  if (started) return;
  started = true;
  if (!isSyncConfigured()) {
    setSyncStatus({ state: 'disabled' });
    return;
  }
  setSyncStatus({ state: 'signed-out' });
  if (typeof window !== 'undefined') {
    window.addEventListener('online', () => void engine?.syncNow());
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') engine?.flush();
    });
  }
  if (!storedSession() && !returningFromLink()) return;
  await attachAuthListener();
}

let listening = false;

/** Escucha los cambios de sesión (una sola vez). Se llama al arrancar con sesión y al iniciarla. */
async function attachAuthListener(): Promise<void> {
  if (listening) return;
  listening = true;
  const client = await getClient();
  client.auth.onAuthStateChange((event, session) => {
    // Sin llamar a Supabase dentro del callback (puede bloquearse): se aplaza al siguiente turno.
    setTimeout(() => {
      if (event === 'SIGNED_OUT') {
        stopEngine();
        setSyncStatus({ state: 'signed-out', email: null, lastSyncedAt: null, error: null });
      } else if (session && (event === 'SIGNED_IN' || event === 'INITIAL_SESSION') && !engine) {
        begin(session);
      }
    }, 0);
  });
}

/** Envía el enlace (y código) de acceso al correo. Lanza con un mensaje legible si falla. */
export async function signInWithEmail(email: string): Promise<void> {
  const client = await getClient();
  await attachAuthListener();
  const { error } = await client.auth.signInWithOtp({
    email,
    options: { emailRedirectTo: new URL(url('/progreso/'), location.origin).toString() },
  });
  if (error) throw new Error(error.message);
}

/** Alternativa al enlace: el código de 6 dígitos del correo (los escáneres de correo pueden gastar el enlace). */
export async function verifyEmailCode(email: string, token: string): Promise<void> {
  const client = await getClient();
  await attachAuthListener();
  const { error } = await client.auth.verifyOtp({ email, token, type: 'email' });
  if (error) throw new Error(error.message);
}

export async function signOut(): Promise<void> {
  const client = await getClient();
  await client.auth.signOut();
  stopEngine(); // sin esperar al evento: así un cambio local posterior no intenta subirse
  setSyncStatus({ state: 'signed-out', email: null, lastSyncedAt: null, error: null });
}

/** Borra la copia de la nube y cierra la sesión (si no, la siguiente sincronización la volvería a crear). */
export async function deleteCloudDataAndSignOut(): Promise<void> {
  if (!engine) throw new Error('No hay sesión iniciada.');
  await engine.deleteRemote();
  await signOut();
}

export async function syncNow(): Promise<void> {
  await engine?.syncNow();
}

export const syncStatus = $sync;
