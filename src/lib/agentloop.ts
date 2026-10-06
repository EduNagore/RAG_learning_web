/** Modelo didáctico del bucle de un agente: pasos guionizados y estimación del contexto. */

export type StepKind = 'thought' | 'action' | 'observation' | 'final' | 'stop';

export interface LoopStep {
  kind: StepKind;
  text: string;
}

export interface Scenario {
  id: string;
  title: string;
  task: string;
  steps: LoopStep[];
}

/** Tokens del prompt de sistema y de las descripciones de herramientas (valor ilustrativo). */
export const BASE_TOKENS = 300;

/** Misma aproximación que `ragkit.llm.approx_tokens`: 1 token por cada 4 caracteres. */
export function approxTokens(text: string): number {
  return text ? Math.ceil(text.length / 4) : 0;
}

export const SCENARIOS: Scenario[] = [
  {
    id: 'exito',
    title: 'Dos herramientas y respuesta',
    task: '¿Cuánto cuesta enviar 8 kg en modo exprés y cuándo llegaría?',
    steps: [
      { kind: 'thought', text: 'Necesito el precio y el plazo. Empiezo por el precio.' },
      { kind: 'action', text: 'coste_envio(modo="expres", kilos=8)' },
      { kind: 'observation', text: '{"eur": 34.5}' },
      { kind: 'thought', text: 'Ya tengo el precio. Falta el plazo del modo exprés.' },
      { kind: 'action', text: 'plazo_envio(modo="expres")' },
      { kind: 'observation', text: '{"horas": 24}' },
      { kind: 'final', text: 'Enviar 8 kg en exprés cuesta 34,50 EUR y llega en 24 horas.' },
    ],
  },
  {
    id: 'error',
    title: 'Error de herramienta y recuperación',
    task: '¿Cuánto cuesta enviar 8 kg en modo exprés?',
    steps: [
      { kind: 'thought', text: 'Necesito el precio del envío exprés.' },
      { kind: 'action', text: 'coste_envio(modo="expres", kilos="ocho")' },
      {
        kind: 'observation',
        text: 'error: el argumento "kilos" debe ser number (recibido: string)',
      },
      { kind: 'thought', text: 'Me equivoqué de tipo: kilos debe ser un número, no un texto.' },
      { kind: 'action', text: 'coste_envio(modo="expres", kilos=8)' },
      { kind: 'observation', text: '{"eur": 34.5}' },
      { kind: 'final', text: 'Enviar 8 kg en exprés cuesta 34,50 EUR.' },
    ],
  },
  {
    id: 'bucle',
    title: 'Herramienta caída y guarda de bucle',
    task: '¿Cuánto cuesta enviar 8 kg en modo exprés?',
    steps: [
      { kind: 'thought', text: 'Necesito el precio del envío exprés.' },
      { kind: 'action', text: 'coste_envio(modo="expres", kilos=8)' },
      { kind: 'observation', text: 'error: servicio no disponible' },
      { kind: 'thought', text: 'Falló. Lo vuelvo a intentar.' },
      { kind: 'action', text: 'coste_envio(modo="expres", kilos=8)' },
      { kind: 'observation', text: 'error: servicio no disponible' },
      { kind: 'thought', text: 'Sigue fallando. Pruebo otra vez.' },
      { kind: 'action', text: 'coste_envio(modo="expres", kilos=8)' },
      {
        kind: 'stop',
        text: 'Guarda de bucle: la misma llamada se ha pedido 3 veces. Se detiene el agente sin ejecutarla y se devuelve un error claro al usuario.',
      },
    ],
  },
];

export interface LoopStats {
  /** Tokens que hay en el contexto tras los primeros `upTo` pasos. */
  contextTokens: number;
  /** Tokens de entrada enviados al modelo sumando todas sus llamadas hasta ahora. */
  sentTokens: number;
  /** Llamadas al modelo realizadas (cada pensamiento o respuesta final es una). */
  modelCalls: number;
}

/** Estadísticas tras mostrar los primeros `upTo` pasos de un escenario. */
export function loopStats(scenario: Scenario, upTo: number): LoopStats {
  const shown = Math.max(0, Math.min(upTo, scenario.steps.length));
  let context = BASE_TOKENS + approxTokens(scenario.task);
  let sent = 0;
  let calls = 0;
  for (const step of scenario.steps.slice(0, shown)) {
    if (step.kind === 'thought' || step.kind === 'final') {
      sent += context; // cada llamada al modelo reenvía todo el historial
      calls += 1;
    }
    context += approxTokens(step.text);
  }
  return { contextTokens: context, sentTokens: sent, modelCalls: calls };
}
