import { useState } from 'react';
import { BASE_TOKENS, SCENARIOS, loopStats, type StepKind } from '../../lib/agentloop';

const button =
  'rounded-md border border-slate-300 px-3 py-1 text-sm hover:bg-slate-100 disabled:opacity-40 dark:border-slate-700 dark:hover:bg-slate-800';

const LABELS: Record<StepKind, string> = {
  thought: 'Pensamiento',
  action: 'Acción',
  observation: 'Observación',
  final: 'Respuesta final',
  stop: 'Parada',
};

const STYLES: Record<StepKind, string> = {
  thought: 'border-sky-400 bg-sky-50 dark:bg-sky-950/40',
  action: 'border-violet-400 bg-violet-50 dark:bg-violet-950/40',
  observation: 'border-amber-400 bg-amber-50 dark:bg-amber-950/40',
  final: 'border-emerald-500 bg-emerald-50 dark:bg-emerald-950/40',
  stop: 'border-rose-500 bg-rose-50 dark:bg-rose-950/40',
};

export default function AgentLoopStepper() {
  const [scenarioId, setScenarioId] = useState(SCENARIOS[0].id);
  const [shown, setShown] = useState(0);
  const scenario = SCENARIOS.find((s) => s.id === scenarioId) ?? SCENARIOS[0];
  const total = scenario.steps.length;
  const stats = loopStats(scenario, shown);

  return (
    <div className="not-prose my-8 space-y-4 rounded-xl border border-slate-200 p-5 dark:border-slate-800">
      <h3 className="text-lg font-semibold">Bucle del agente paso a paso</h3>
      <p className="text-sm text-slate-600 dark:text-slate-400">
        Avanza un paso cada vez y observa cómo el modelo piensa, pide una herramienta y recibe el
        resultado. Fíjate en el contexto: cada llamada al modelo reenvía <strong>todo</strong> el
        historial, y por eso lo enviado crece más rápido que el número de pasos.
      </p>

      <label className="block text-sm">
        Escenario
        <select
          value={scenarioId}
          onChange={(e) => {
            setScenarioId(e.target.value);
            setShown(0);
          }}
          className="ml-2 rounded-md border border-slate-300 px-2 py-1 text-sm dark:border-slate-700 dark:bg-slate-900"
        >
          {SCENARIOS.map((s) => (
            <option key={s.id} value={s.id}>
              {s.title}
            </option>
          ))}
        </select>
      </label>

      <p className="text-sm">
        <strong>Tarea:</strong> {scenario.task}
      </p>

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          className={button}
          onClick={() => setShown((n) => Math.max(0, n - 1))}
          disabled={shown === 0}
        >
          Paso anterior
        </button>
        <button
          type="button"
          className={button}
          onClick={() => setShown((n) => Math.min(total, n + 1))}
          disabled={shown === total}
        >
          Siguiente paso
        </button>
        <button type="button" className={button} onClick={() => setShown(0)} disabled={shown === 0}>
          Reiniciar
        </button>
      </div>

      <p role="status" className="text-sm font-medium">
        Paso {shown} de {total} · llamadas al modelo: {stats.modelCalls} · contexto actual: ≈{' '}
        {stats.contextTokens} tokens · enviados en total: ≈ {stats.sentTokens} tokens
      </p>

      <ol className="space-y-2" aria-label="Pasos del agente">
        {scenario.steps.slice(0, shown).map((step, i) => (
          <li
            key={`${scenario.id}-${i}`}
            aria-current={i === shown - 1 ? 'step' : undefined}
            className={`rounded-md border-l-4 p-2 text-sm ${STYLES[step.kind]} ${
              i === shown - 1 ? 'ring-2 ring-slate-400 dark:ring-slate-500' : ''
            }`}
          >
            <span className="font-semibold">{LABELS[step.kind]}:</span>{' '}
            <span className={step.kind === 'action' ? 'font-mono' : ''}>{step.text}</span>
          </li>
        ))}
      </ol>
      {shown === 0 && (
        <p className="text-sm text-slate-500">Pulsa «Siguiente paso» para empezar.</p>
      )}
      <p className="text-xs text-slate-500">
        Los tokens se estiman como 1 por cada 4 caracteres y se suman ≈ {BASE_TOKENS} de prompt de
        sistema y herramientas; son valores ilustrativos de un escenario guionizado, no de un modelo
        real.
      </p>
    </div>
  );
}
