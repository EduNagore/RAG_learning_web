import { indentLess, indentMore } from '@codemirror/commands';
import { python } from '@codemirror/lang-python';
import { Compartment, EditorState } from '@codemirror/state';
import { oneDark } from '@codemirror/theme-one-dark';
import { EditorView, keymap } from '@codemirror/view';
import { basicSetup } from 'codemirror';
import { useEffect, useRef, useState } from 'react';
import { loadProgress, markLabPassed, saveLabCode } from '../../lib/progress';
import { PyRunner, type CheckReport, type RunReport } from '../../lib/pyodide/client';

interface Props {
  labId: string;
  title: string;
  starter: string;
  solution: string;
  tests: string;
  hints: string[];
  packages: string[];
  /** Ruta base del sitio con barra final, de donde el worker descarga ragkit y los datos. */
  base: string;
}

const FAILS_BEFORE_SOLUTION = 3;
const isDark = () => document.documentElement.classList.contains('dark');

export default function CodeLab({ labId, starter, solution, tests, hints, packages, base }: Props) {
  const host = useRef<HTMLDivElement>(null);
  const view = useRef<EditorView | null>(null);
  const runner = useRef<PyRunner | null>(null);
  const [initialCode] = useState(() => loadProgress().labs[labId]?.code ?? starter);
  const [code, setCode] = useState(initialCode);
  const [busy, setBusy] = useState<'run' | 'check' | null>(null);
  const [status, setStatus] = useState('');
  const [output, setOutput] = useState<RunReport | null>(null);
  const [report, setReport] = useState<CheckReport | null>(null);
  const [failedChecks, setFailedChecks] = useState(0);
  const [passed, setPassed] = useState(() => loadProgress().labs[labId]?.status === 'passed');
  const [hintsShown, setHintsShown] = useState(0);
  const [showSolution, setShowSolution] = useState(false);
  const [confirm, setConfirm] = useState<'reset' | 'solution' | null>(null);

  // --- Editor -----------------------------------------------------------------
  useEffect(() => {
    if (!host.current) return;
    const theme = new Compartment();
    let escaped = false; // Esc + Tab saca el foco del editor en lugar de sangrar
    /** Tab sangra, salvo justo después de Esc: entonces se deja pasar para mover el foco. */
    const tab = (indent: (v: EditorView) => boolean) => (v: EditorView) => {
      if (!escaped) return indent(v);
      escaped = false;
      return false;
    };

    const editor = new EditorView({
      parent: host.current,
      state: EditorState.create({
        doc: initialCode,
        extensions: [
          keymap.of([
            {
              key: 'Escape',
              run: () => {
                escaped = true;
                return false;
              },
            },
            {
              key: 'Tab',
              run: tab(indentMore),
              shift: tab(indentLess),
            },
          ]),
          basicSetup,
          python(),
          theme.of(isDark() ? oneDark : []),
          EditorView.contentAttributes.of({ 'aria-label': 'Editor de código Python' }),
          EditorView.domEventHandlers({
            keydown: (event) => {
              if (event.key !== 'Escape' && event.key !== 'Tab') escaped = false;
              return false;
            },
            blur: () => {
              escaped = false;
              return false;
            },
          }),
          EditorView.theme({
            '&': { height: '24rem', fontSize: '0.875rem' },
            '.cm-scroller': { overflow: 'auto', fontFamily: 'var(--font-mono)' },
          }),
          EditorView.updateListener.of((update) => {
            if (update.docChanged) setCode(update.state.doc.toString());
          }),
        ],
      }),
    });
    view.current = editor;

    // El tema del editor sigue al tema de la web.
    const observer = new MutationObserver(() =>
      editor.dispatch({ effects: theme.reconfigure(isDark() ? oneDark : []) }),
    );
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });

    return () => {
      observer.disconnect();
      editor.destroy();
      view.current = null;
    };
  }, [initialCode]);

  // Autoguardado con retardo; no guarda hasta que el alumno cambie algo.
  useEffect(() => {
    if (code === initialCode) return;
    const t = setTimeout(() => saveLabCode(labId, code), 800);
    return () => clearTimeout(t);
  }, [code, initialCode, labId]);

  // El worker se libera al salir de la página.
  useEffect(() => () => runner.current?.dispose(), []);

  const getRunner = () => (runner.current ??= new PyRunner(base, packages));

  const setEditorCode = (next: string) =>
    view.current?.dispatch({
      changes: { from: 0, to: view.current.state.doc.length, insert: next },
    });

  // --- Acciones ---------------------------------------------------------------
  const run = async () => {
    setBusy('run');
    setReport(null);
    setOutput(null);
    try {
      setOutput(await getRunner().run(code, setStatus));
    } catch (e) {
      setOutput({ stdout: '', error: e instanceof Error ? e.message : String(e) });
    } finally {
      setBusy(null);
      setStatus('');
    }
  };

  const check = async () => {
    setBusy('check');
    setOutput(null);
    try {
      const result = await getRunner().check(code, tests, setStatus);
      setReport(result);
      const ok =
        result.load_error === null &&
        result.results.length > 0 &&
        result.results.every((r) => r.passed);
      if (ok) {
        markLabPassed(labId, code);
        setPassed(true);
      } else {
        setFailedChecks((n) => n + 1);
      }
    } catch (e) {
      // RunTimeoutError (bucle infinito) y los fallos de carga llegan aquí con un mensaje legible.
      setReport({ load_error: e instanceof Error ? e.message : String(e), results: [] });
    } finally {
      setBusy(null);
      setStatus('');
    }
  };

  const askSolution = () => {
    if (passed || failedChecks >= FAILS_BEFORE_SOLUTION) setShowSolution(true);
    else setConfirm('solution');
  };

  const results = report?.results ?? [];
  const passedCount = results.filter((r) => r.passed).length;
  // Los tests ocultos se muestran con un nombre genérico para no dar pistas del enunciado.
  let hiddenCount = 0;
  const titles = results.map((r) => (r.hidden ? `Caso adicional ${++hiddenCount}` : r.title));

  const btn =
    'rounded-md px-4 py-2 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-50';
  const primary = `${btn} bg-indigo-600 text-white hover:bg-indigo-700`;
  const secondary = `${btn} border border-slate-300 hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800`;

  return (
    <div className="space-y-4">
      {passed && (
        <p
          role="status"
          className="rounded-lg border border-emerald-500 bg-emerald-50 p-3 font-medium text-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-200"
        >
          ✓ Laboratorio superado. Tu código pasa todos los tests.
        </p>
      )}

      <div
        ref={host}
        className="overflow-hidden rounded-lg border border-slate-300 dark:border-slate-700"
      />
      <p className="text-xs text-slate-500 dark:text-slate-400">
        Tab sangra el código. Para salir del editor con el teclado, pulsa Esc y después Tab. Tu
        código se guarda automáticamente en este navegador.
      </p>

      <div className="flex flex-wrap gap-2">
        <button type="button" className={secondary} onClick={run} disabled={busy !== null}>
          {busy === 'run' ? 'Ejecutando…' : 'Ejecutar'}
        </button>
        <button type="button" className={primary} onClick={check} disabled={busy !== null}>
          {busy === 'check' ? 'Comprobando…' : 'Comprobar'}
        </button>
        <button
          type="button"
          className={secondary}
          onClick={() => setHintsShown((n) => Math.min(n + 1, hints.length))}
          disabled={hintsShown >= hints.length}
        >
          Pista ({hintsShown}/{hints.length})
        </button>
        <button type="button" className={secondary} onClick={() => setConfirm('reset')}>
          Reiniciar
        </button>
        <button type="button" className={secondary} onClick={askSolution}>
          Ver solución
        </button>
      </div>

      {confirm && (
        <div
          role="alertdialog"
          aria-label="Confirmación"
          className="flex flex-wrap items-center gap-3 rounded-lg border border-amber-400 bg-amber-50 p-3 text-sm dark:bg-amber-950/30"
        >
          <span>
            {confirm === 'reset'
              ? 'Se perderá tu código y volverás al punto de partida. ¿Seguro?'
              : `Todavía no has agotado tus intentos (${failedChecks}/${FAILS_BEFORE_SOLUTION}). Intentarlo antes es la mejor forma de aprender. ¿Ver la solución igualmente?`}
          </span>
          <button
            type="button"
            className={`${btn} bg-amber-600 text-white hover:bg-amber-700`}
            onClick={() => {
              if (confirm === 'reset') {
                setEditorCode(starter);
                setReport(null);
                setOutput(null);
              } else setShowSolution(true);
              setConfirm(null);
            }}
          >
            Sí
          </button>
          <button type="button" className={secondary} onClick={() => setConfirm(null)}>
            No
          </button>
        </div>
      )}

      <div aria-live="polite" className="min-h-6 text-sm text-slate-600 dark:text-slate-400">
        {status}
      </div>

      {hintsShown > 0 && (
        <section
          aria-label="Pistas"
          className="rounded-lg border border-sky-300 bg-sky-50 p-4 dark:border-sky-800 dark:bg-sky-950/30"
        >
          <h3 className="mb-2 font-semibold">Pistas</h3>
          <ol className="list-decimal space-y-2 pl-5 text-sm">
            {hints.slice(0, hintsShown).map((h, i) => (
              <li key={i}>{h}</li>
            ))}
          </ol>
        </section>
      )}

      {output && (
        <section aria-label="Salida del programa">
          <h3 className="mb-1 font-semibold">Salida</h3>
          <pre className="max-h-64 overflow-auto whitespace-pre-wrap rounded-lg bg-slate-900 p-3 text-sm text-slate-100">
            {output.stdout}
            {output.error && <span className="text-red-400">{output.error}</span>}
            {!output.stdout && !output.error && (
              <span className="text-slate-400">(sin salida)</span>
            )}
          </pre>
        </section>
      )}

      {report && (
        <section aria-label="Resultado de los tests" aria-live="polite">
          <h3 className="mb-2 font-semibold">
            {report.load_error
              ? 'Tu código no se pudo ejecutar'
              : `${passedCount} de ${results.length} tests superados`}
          </h3>
          {report.load_error && (
            <p className="rounded-lg border border-red-400 bg-red-50 p-3 text-sm dark:bg-red-950/30">
              {report.load_error}
            </p>
          )}
          <ul className="space-y-2">
            {results.map((r, i) => {
              const title = titles[i];
              return (
                <li
                  key={r.name}
                  className={`rounded-lg border p-3 text-sm ${
                    r.passed
                      ? 'border-emerald-400 bg-emerald-50 dark:bg-emerald-950/30'
                      : 'border-red-400 bg-red-50 dark:bg-red-950/30'
                  }`}
                >
                  <p className="font-medium">
                    <span aria-hidden="true">{r.passed ? '✓' : '✗'}</span>{' '}
                    <span className="sr-only">{r.passed ? 'Superado: ' : 'Fallado: '}</span>
                    {title}
                  </p>
                  {!r.passed && <p className="mt-1 whitespace-pre-wrap">{r.message}</p>}
                  {r.stdout && (
                    <pre className="mt-2 max-h-32 overflow-auto whitespace-pre-wrap rounded bg-slate-900 p-2 text-xs text-slate-100">
                      {r.stdout}
                    </pre>
                  )}
                </li>
              );
            })}
          </ul>
        </section>
      )}

      {showSolution && (
        <section
          aria-label="Solución de referencia"
          className="rounded-lg border border-slate-300 p-4 dark:border-slate-700"
        >
          <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
            <h3 className="font-semibold">Solución de referencia</h3>
            <span className="flex gap-2">
              <button
                type="button"
                className={secondary}
                onClick={() => {
                  setEditorCode(solution);
                  setShowSolution(false);
                }}
              >
                Cargar en el editor
              </button>
              <button type="button" className={secondary} onClick={() => setShowSolution(false)}>
                Ocultar
              </button>
            </span>
          </div>
          <pre className="max-h-96 overflow-auto rounded bg-slate-900 p-3 text-sm text-slate-100">
            <code>{solution}</code>
          </pre>
        </section>
      )}
    </div>
  );
}
