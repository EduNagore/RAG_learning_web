import { useStore } from '@nanostores/react';
import { useEffect } from 'react';
import { startSync } from '../../lib/syncClient';
import { $sync, type SyncState } from '../../lib/sync';

const LABELS: Record<SyncState, { text: string; dot: string }> = {
  disabled: { text: '', dot: '' },
  'signed-out': { text: 'sin sesión', dot: 'bg-slate-400' },
  idle: { text: 'sincronizado', dot: 'bg-emerald-500' },
  pending: { text: 'pendiente', dot: 'bg-amber-500' },
  syncing: { text: 'sincronizando', dot: 'bg-sky-500' },
  offline: { text: 'sin conexión', dot: 'bg-amber-500' },
  error: { text: 'error', dot: 'bg-red-500' },
};

/** Indicador discreto de la cabecera. Arranca la sincronización en todas las páginas. */
export default function SyncBadge({ href }: { href: string }) {
  const status = useStore($sync);
  useEffect(() => {
    void startSync();
  }, []);

  const { text, dot } = LABELS[status.state];
  if (status.state === 'disabled') return null;
  const label = `Progreso en la nube: ${text}`;
  return (
    <a
      href={href}
      aria-label={label}
      title={label}
      data-testid="sync-badge"
      data-state={status.state}
      className="flex items-center gap-1.5 rounded-md px-2 py-1.5 text-xs text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
    >
      <span aria-hidden="true" className={`inline-block h-2 w-2 rounded-full ${dot}`} />
      <span className="hidden lg:inline">Nube: {text}</span>
    </a>
  );
}
