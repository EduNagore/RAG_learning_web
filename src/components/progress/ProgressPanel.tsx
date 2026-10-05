import { useStore } from '@nanostores/react';
import { useEffect, useRef, useState } from 'react';
import {
  $progress,
  exportProgress,
  hydrateProgress,
  importProgress,
  moduleCompletion,
  replaceProgress,
  resetProgress,
} from '../../lib/progress';
import { boxCounts, dueQuestionIds } from '../../lib/srs';
import { url } from '../../lib/url';

interface Props {
  modules: { id: string; title: string; lessonIds: string[] }[];
  lessonTitles: Record<string, string>;
}

const dateFmt = (iso: string) =>
  new Date(iso).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' });

export default function ProgressPanel({ modules, lessonTitles }: Props) {
  const progress = useStore($progress);
  const [message, setMessage] = useState<{ tone: 'ok' | 'bad'; text: string } | null>(null);
  const [confirmReset, setConfirmReset] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => hydrateProgress(), []);

  const allLessons = modules.flatMap((m) => m.lessonIds);
  const read = moduleCompletion(progress, allLessons);
  const quizzes = Object.entries(progress.quizScores);
  const counts = boxCounts(progress.srs);
  const due = dueQuestionIds(progress.srs, new Date()).length;
  const labsPassed = Object.values(progress.labs).filter((l) => l.status === 'passed').length;

  const download = () => {
    const blob = new Blob([exportProgress(progress)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `rma-progreso-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
    setMessage({ tone: 'ok', text: 'Copia de seguridad descargada.' });
  };

  const onImport = async (file: File | undefined) => {
    if (!file) return;
    try {
      replaceProgress(importProgress(await file.text()));
      setMessage({ tone: 'ok', text: 'Progreso importado: ha sustituido al anterior.' });
    } catch (e) {
      setMessage({
        tone: 'bad',
        text: e instanceof Error ? e.message : 'No se pudo importar el archivo.',
      });
    } finally {
      if (fileRef.current) fileRef.current.value = '';
    }
  };

  return (
    <div className="space-y-8">
      <p className="rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm dark:border-amber-800 dark:bg-amber-950/30">
        Tu progreso se guarda <strong>solo en este navegador</strong> (no hay cuentas ni servidor).
        Descarga una copia de seguridad si cambias de equipo o borras los datos del sitio.
      </p>

      <section aria-labelledby="resumen" className="grid gap-4 sm:grid-cols-3">
        <h2 id="resumen" className="sr-only">
          Resumen
        </h2>
        <Stat label="Lecciones leídas" value={`${read.done} / ${read.total}`} />
        <Stat label="Tests realizados" value={String(quizzes.length)} />
        <Stat label="Repasos pendientes" value={String(due)} />
        <Stat label="Exámenes" value={String(progress.exams.length)} />
        <Stat label="Laboratorios superados" value={String(labsPassed)} />
        <Stat label="Preguntas en repaso" value={String(counts.reduce((a, b) => a + b, 0))} />
      </section>

      <section aria-labelledby="modulos">
        <h2 id="modulos" className="text-lg font-semibold">
          Avance por módulo
        </h2>
        <ul className="mt-2 space-y-2">
          {modules
            .filter((m) => m.lessonIds.length > 0)
            .map((m) => {
              const c = moduleCompletion(progress, m.lessonIds);
              return (
                <li key={m.id}>
                  <div className="flex justify-between text-sm">
                    <a className="hover:underline" href={url(`/teoria/#${m.id}`)}>
                      {m.title}
                    </a>
                    <span>
                      {c.done}/{c.total}
                    </span>
                  </div>
                  <div className="mt-1 h-1.5 overflow-hidden rounded bg-slate-200 dark:bg-slate-800">
                    <div
                      className="h-full bg-emerald-500"
                      style={{ width: `${(c.done / c.total) * 100}%` }}
                    />
                  </div>
                </li>
              );
            })}
        </ul>
      </section>

      {quizzes.length > 0 && (
        <section aria-labelledby="notas">
          <h2 id="notas" className="text-lg font-semibold">
            Notas de los tests
          </h2>
          <table className="mt-2 w-full text-sm">
            <thead>
              <tr className="border-b border-slate-300 text-left dark:border-slate-700">
                <th className="py-1 pr-4">Test</th>
                <th className="py-1 pr-4">Mejor</th>
                <th className="py-1 pr-4">Último</th>
                <th className="py-1">Intentos</th>
              </tr>
            </thead>
            <tbody>
              {quizzes.map(([id, s]) => (
                <tr key={id} className="border-b border-slate-200 dark:border-slate-800">
                  <td className="py-1.5 pr-4">{lessonTitles[id] ?? id}</td>
                  <td className="py-1.5 pr-4 font-medium">{s.best} %</td>
                  <td className="py-1.5 pr-4">{s.last} %</td>
                  <td className="py-1.5">{s.attempts}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {progress.exams.length > 0 && (
        <section aria-labelledby="examenes">
          <h2 id="examenes" className="text-lg font-semibold">
            Historial de exámenes
          </h2>
          <ul className="mt-2 space-y-1 text-sm">
            {[...progress.exams].reverse().map((e, i) => (
              <li key={i}>
                {dateFmt(e.date)} · {e.score}/{e.total} ({Math.round((e.score / e.total) * 100)} %)
              </li>
            ))}
          </ul>
        </section>
      )}

      <section aria-labelledby="copia" className="space-y-3">
        <h2 id="copia" className="text-lg font-semibold">
          Copia de seguridad
        </h2>
        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={download}
            className="rounded-md bg-indigo-600 px-4 py-2 font-medium text-white hover:bg-indigo-700"
          >
            Exportar progreso
          </button>
          <label className="cursor-pointer rounded-md border border-slate-300 px-4 py-2 font-medium hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800">
            Importar progreso
            <input
              ref={fileRef}
              type="file"
              accept="application/json,.json"
              className="sr-only"
              onChange={(e) => onImport(e.target.files?.[0])}
            />
          </label>
          {!confirmReset ? (
            <button
              type="button"
              onClick={() => setConfirmReset(true)}
              className="rounded-md border border-red-300 px-4 py-2 font-medium text-red-700 hover:bg-red-50 dark:border-red-800 dark:text-red-300 dark:hover:bg-red-950/40"
            >
              Reiniciar progreso
            </button>
          ) : (
            <span
              role="alertdialog"
              aria-label="Confirmar reinicio"
              className="flex items-center gap-2"
            >
              <span className="text-sm">Se borrará todo el progreso. ¿Seguro?</span>
              <button
                type="button"
                onClick={() => {
                  resetProgress();
                  setConfirmReset(false);
                  setMessage({ tone: 'ok', text: 'Progreso reiniciado.' });
                }}
                className="rounded-md bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-700"
              >
                Sí, borrar
              </button>
              <button
                type="button"
                onClick={() => setConfirmReset(false)}
                className="rounded-md border border-slate-300 px-3 py-1.5 text-sm dark:border-slate-700"
              >
                Cancelar
              </button>
            </span>
          )}
        </div>
        <p
          role="status"
          className={
            message?.tone === 'bad'
              ? 'text-red-700 dark:text-red-300'
              : 'text-emerald-700 dark:text-emerald-300'
          }
        >
          {message?.text}
        </p>
      </section>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-slate-200 p-4 dark:border-slate-800">
      <p className="text-2xl font-bold">{value}</p>
      <p className="text-sm text-slate-600 dark:text-slate-400">{label}</p>
    </div>
  );
}
