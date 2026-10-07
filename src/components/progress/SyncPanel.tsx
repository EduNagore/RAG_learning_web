import { useStore } from '@nanostores/react';
import { useEffect, useState, type FormEvent } from 'react';
import { emptyProgress, replaceProgress } from '../../lib/progress';
import {
  deleteCloudDataAndSignOut,
  signInWithEmail,
  signOut,
  startSync,
  syncNow,
  verifyEmailCode,
} from '../../lib/syncClient';
import { $sync, type SyncStatus } from '../../lib/sync';

const button =
  'rounded-md border border-slate-300 px-3 py-1 text-sm hover:bg-slate-100 disabled:opacity-40 dark:border-slate-700 dark:hover:bg-slate-800';
const field =
  'rounded-md border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-900';

export function statusText(s: SyncStatus, now = new Date()): string {
  switch (s.state) {
    case 'syncing':
      return 'Sincronizando…';
    case 'pending':
      return 'Hay cambios pendientes de subir.';
    case 'offline':
      return 'Sin conexión: tu progreso está a salvo en este dispositivo y se subirá al volver la red.';
    case 'error':
      return `No se pudo sincronizar: ${s.error ?? 'error desconocido'}. Se reintentará.`;
    case 'idle': {
      if (!s.lastSyncedAt) return 'Conectado.';
      const seconds = Math.max(
        0,
        Math.round((now.getTime() - new Date(s.lastSyncedAt).getTime()) / 1000),
      );
      if (seconds < 60) return 'Sincronizado hace unos segundos.';
      return `Sincronizado hace ${Math.round(seconds / 60)} min.`;
    }
    default:
      return '';
  }
}

type Confirm = null | 'signout' | 'delete';

export default function SyncPanel() {
  const status = useStore($sync);
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [sentTo, setSentTo] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<{ tone: 'ok' | 'bad'; text: string } | null>(null);
  const [confirm, setConfirm] = useState<Confirm>(null);

  useEffect(() => {
    void startSync();
  }, []);

  const run = async (fn: () => Promise<void>, ok?: string) => {
    setBusy(true);
    setMessage(null);
    try {
      await fn();
      if (ok) setMessage({ tone: 'ok', text: ok });
    } catch (e) {
      setMessage({ tone: 'bad', text: e instanceof Error ? e.message : 'Algo ha fallado.' });
    } finally {
      setBusy(false);
    }
  };

  const sendLink = (e: FormEvent) => {
    e.preventDefault();
    void run(async () => {
      await signInWithEmail(email.trim());
      setSentTo(email.trim());
    });
  };

  const checkCode = (e: FormEvent) => {
    e.preventDefault();
    if (!sentTo) return;
    void run(() => verifyEmailCode(sentTo, code.trim()), 'Sesión iniciada.');
  };

  const leave = (wipeLocal: boolean) =>
    run(
      async () => {
        await syncNow(); // lo último llega a la nube antes de salir
        await signOut();
        if (wipeLocal) replaceProgress(emptyProgress());
        setConfirm(null);
      },
      wipeLocal
        ? 'Sesión cerrada y progreso de este dispositivo borrado.'
        : 'Sesión cerrada. Tu progreso sigue en este dispositivo.',
    );

  const signedIn = status.email !== null && status.state !== 'signed-out';

  return (
    <section
      id="sincronizacion"
      aria-labelledby="sync-title"
      className="rounded-lg border border-slate-200 p-5 dark:border-slate-800"
    >
      <h2 id="sync-title" className="text-xl font-semibold">
        Guardar mi progreso en la nube
      </h2>
      <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
        Opcional. Inicia sesión con tu correo y recupera tu progreso en cualquier dispositivo. Sin
        sesión, todo sigue funcionando y se guarda solo en este navegador.
      </p>

      <p
        role="status"
        aria-live="polite"
        className="mt-3 text-sm font-medium"
        data-testid="sync-status"
      >
        {signedIn ? statusText(status) : 'Sin sesión iniciada.'}
      </p>

      {!signedIn && (
        <div className="mt-3 space-y-3">
          <form onSubmit={sendLink} className="flex flex-wrap items-end gap-2">
            <label className="block text-sm">
              Correo electrónico
              <input
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={`${field} mt-1 block w-72 max-w-full`}
              />
            </label>
            <button type="submit" className={button} disabled={busy || !email.trim()}>
              Enviarme el enlace
            </button>
          </form>
          {sentTo && (
            <div className="space-y-2 text-sm" data-testid="sync-sent">
              <p>
                Te hemos escrito a <strong>{sentTo}</strong>. Abre el enlace en este navegador
                (caduca a la hora; se puede pedir otro cada 60 segundos). Si el enlace no funciona
                porque tu correo lo ha abierto antes, usa el código de 6 dígitos del mismo mensaje:
              </p>
              <form onSubmit={checkCode} className="flex flex-wrap items-end gap-2">
                <label className="block">
                  Código
                  <input
                    inputMode="numeric"
                    autoComplete="one-time-code"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    className={`${field} mt-1 block w-40`}
                  />
                </label>
                <button type="submit" className={button} disabled={busy || code.trim().length < 6}>
                  Entrar con el código
                </button>
              </form>
            </div>
          )}
        </div>
      )}

      {signedIn && (
        <div className="mt-3 space-y-3">
          <p className="text-sm">
            Sesión iniciada como <strong>{status.email}</strong>.
          </p>
          <div className="flex flex-wrap gap-2">
            <button type="button" className={button} onClick={() => run(syncNow)} disabled={busy}>
              Sincronizar ahora
            </button>
            <button
              type="button"
              className={button}
              onClick={() => setConfirm('signout')}
              disabled={busy}
            >
              Cerrar sesión
            </button>
            <button
              type="button"
              className={button}
              onClick={() => setConfirm('delete')}
              disabled={busy}
            >
              Borrar mi copia en la nube
            </button>
          </div>

          {confirm === 'signout' && (
            <div
              role="group"
              aria-label="Cerrar sesión"
              className="rounded-md border border-slate-300 p-3 text-sm dark:border-slate-700"
            >
              <p>¿Qué hacemos con el progreso guardado en este dispositivo?</p>
              <div className="mt-2 flex flex-wrap gap-2">
                <button
                  type="button"
                  className={button}
                  onClick={() => leave(false)}
                  disabled={busy}
                >
                  Conservarlo y cerrar sesión
                </button>
                <button
                  type="button"
                  className={button}
                  onClick={() => leave(true)}
                  disabled={busy}
                >
                  Borrarlo de este dispositivo y cerrar sesión
                </button>
                <button type="button" className={button} onClick={() => setConfirm(null)}>
                  Cancelar
                </button>
              </div>
            </div>
          )}
          {confirm === 'delete' && (
            <div
              role="group"
              aria-label="Borrar la copia en la nube"
              className="rounded-md border border-red-300 p-3 text-sm dark:border-red-800"
            >
              <p>
                Se borrará tu progreso de la nube y se cerrará la sesión. El progreso de este
                dispositivo no se toca. ¿Seguro?
              </p>
              <div className="mt-2 flex flex-wrap gap-2">
                <button
                  type="button"
                  className={button}
                  disabled={busy}
                  onClick={() =>
                    run(async () => {
                      await deleteCloudDataAndSignOut();
                      setConfirm(null);
                    }, 'Copia de la nube borrada y sesión cerrada.')
                  }
                >
                  Sí, borrar mi copia en la nube
                </button>
                <button type="button" className={button} onClick={() => setConfirm(null)}>
                  Cancelar
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {message && (
        <p
          role={message.tone === 'bad' ? 'alert' : 'status'}
          className={`mt-3 text-sm ${message.tone === 'bad' ? 'text-red-700 dark:text-red-300' : 'text-emerald-700 dark:text-emerald-300'}`}
        >
          {message.text}
        </p>
      )}

      <details className="mt-4 text-sm">
        <summary className="cursor-pointer font-medium">Qué se guarda y cómo borrarlo</summary>
        <ul className="mt-2 list-disc space-y-1 pl-5 text-slate-600 dark:text-slate-400">
          <li>
            Tu correo (para identificarte) y tu progreso: lecciones leídas, notas de los tests,
            repaso espaciado, exámenes y el código que escribes en los laboratorios.
          </li>
          <li>No se guardan tus claves de API ni nada del playground con modelos reales.</li>
          <li>Solo tú puedes leer tu progreso (reglas de acceso por usuario en el servidor).</li>
          <li>
            «Borrar mi copia en la nube» elimina tu progreso del servidor y cierra la sesión. Tu
            correo permanece en el sistema de acceso; si quieres que también se elimine, pídelo a
            quien administra el sitio.
          </li>
          <li>
            Si reinicias tu progreso con la sesión iniciada, el reinicio también llega a la nube y a
            tus otros dispositivos.
          </li>
        </ul>
      </details>
    </section>
  );
}
