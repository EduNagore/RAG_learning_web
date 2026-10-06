import { describe, expect, it } from 'vitest';
import { BASE_TOKENS, SCENARIOS, approxTokens, loopStats } from '../../src/lib/agentloop';

describe('approxTokens', () => {
  it('equivale a ceil(longitud / 4) y es 0 para texto vacío', () => {
    expect(approxTokens('')).toBe(0);
    expect(approxTokens('abcd')).toBe(1);
    expect(approxTokens('abcde')).toBe(2);
  });
});

describe('SCENARIOS', () => {
  it('tienen ids únicos y toda observación sigue a una acción', () => {
    expect(new Set(SCENARIOS.map((s) => s.id)).size).toBe(SCENARIOS.length);
    for (const scenario of SCENARIOS) {
      scenario.steps.forEach((step, i) => {
        if (step.kind === 'observation') expect(scenario.steps[i - 1].kind).toBe('action');
      });
    }
  });

  it('el escenario de éxito termina con respuesta final y el del bucle con una parada', () => {
    const last = (id: string) => {
      const steps = SCENARIOS.find((s) => s.id === id)!.steps;
      return steps[steps.length - 1].kind;
    };
    expect(last('exito')).toBe('final');
    expect(last('error')).toBe('final');
    expect(last('bucle')).toBe('stop');
  });

  it('el escenario del bucle repite exactamente la misma acción 3 veces', () => {
    const actions = SCENARIOS.find((s) => s.id === 'bucle')!.steps.filter(
      (s) => s.kind === 'action',
    );
    expect(actions).toHaveLength(3);
    expect(new Set(actions.map((a) => a.text)).size).toBe(1);
  });
});

describe('loopStats', () => {
  const scenario = SCENARIOS[0];

  it('al principio solo hay base y tarea, sin llamadas ni envíos', () => {
    const stats = loopStats(scenario, 0);
    expect(stats.contextTokens).toBe(BASE_TOKENS + approxTokens(scenario.task));
    expect(stats.sentTokens).toBe(0);
    expect(stats.modelCalls).toBe(0);
  });

  it('el contexto no decrece y los envíos acumulados solo suben en llamadas al modelo', () => {
    let previous = loopStats(scenario, 0);
    for (let i = 1; i <= scenario.steps.length; i++) {
      const stats = loopStats(scenario, i);
      expect(stats.contextTokens).toBeGreaterThanOrEqual(previous.contextTokens);
      const isCall = ['thought', 'final'].includes(scenario.steps[i - 1].kind);
      expect(stats.sentTokens > previous.sentTokens).toBe(isCall);
      previous = stats;
    }
  });

  it('cada llamada reenvía todo el historial, así que el envío crece más que el número de llamadas', () => {
    const total = loopStats(scenario, scenario.steps.length);
    const firstCall = loopStats(scenario, 1);
    expect(total.modelCalls).toBe(3);
    expect(total.sentTokens).toBeGreaterThan(total.modelCalls * firstCall.sentTokens);
  });

  it('un índice fuera de rango se acota', () => {
    expect(loopStats(scenario, -3)).toEqual(loopStats(scenario, 0));
    expect(loopStats(scenario, 999)).toEqual(loopStats(scenario, scenario.steps.length));
  });
});
