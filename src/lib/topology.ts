/** Topologías multiagente: grafo de comunicación y métricas de coordinación (modelo simplificado). */

export type TopologyId = 'cadena' | 'supervisor' | 'jerarquia' | 'red' | 'blackboard';

export interface TopologyNode {
  id: string;
  label: string;
  x: number;
  y: number;
  role: 'coordinador' | 'agente' | 'pizarra';
}

export interface TopologyGraph {
  nodes: TopologyNode[];
  edges: [string, string][];
}

export interface TopologyMetrics {
  /** Agentes de trabajo (sin contar coordinadores ni pizarra). */
  workers: number;
  /** Canales de comunicación distintos en el grafo. */
  channels: number;
  /** Saltos mínimos que recorre un mensaje de un extremo a otro en el peor caso de un reparto. */
  hops: number;
  /** Componentes cuyo fallo detiene todo o parte del sistema. */
  singlePoints: string;
}

export interface TopologyInfo {
  id: TopologyId;
  title: string;
  description: string;
}

export const TOPOLOGIES: TopologyInfo[] = [
  {
    id: 'cadena',
    title: 'Cadena (pipeline)',
    description:
      'Cada agente pasa su resultado al siguiente. Simple y predecible, pero secuencial.',
  },
  {
    id: 'supervisor',
    title: 'Supervisor',
    description:
      'Un coordinador reparte el trabajo y recoge los resultados. Un único punto de decisión.',
  },
  {
    id: 'jerarquia',
    title: 'Jerarquía',
    description:
      'Un coordinador general delega en jefes de equipo (de hasta 3 agentes) que a su vez reparten. Escala el reparto.',
  },
  {
    id: 'red',
    title: 'Red (todos con todos)',
    description:
      'Cualquier agente puede hablar con cualquier otro. Flexible, pero la coordinación crece rápido.',
  },
  {
    id: 'blackboard',
    title: 'Pizarra compartida',
    description:
      'Los agentes leen y escriben en un estado compartido en lugar de hablarse. Desacopla, pero concentra el estado.',
  },
];

export const MIN_AGENTS = 2;
export const MAX_AGENTS = 9;
export const TEAM_SIZE = 3;

const W = 440;
const H = 280;

function clamp(n: number): number {
  return Math.max(MIN_AGENTS, Math.min(MAX_AGENTS, Math.round(n)));
}

function row(
  count: number,
  y: number,
  prefix: string,
  label: (i: number) => string,
): TopologyNode[] {
  return Array.from({ length: count }, (_, i) => ({
    id: `${prefix}${i + 1}`,
    label: label(i),
    x: ((i + 1) * W) / (count + 1),
    y,
    role: 'agente' as const,
  }));
}

function circle(count: number, prefix: string, cx: number, cy: number, r: number): TopologyNode[] {
  return Array.from({ length: count }, (_, i) => {
    const angle = -Math.PI / 2 + (2 * Math.PI * i) / count;
    return {
      id: `${prefix}${i + 1}`,
      label: `A${i + 1}`,
      x: Math.round(cx + r * Math.cos(angle)),
      y: Math.round(cy + r * Math.sin(angle)),
      role: 'agente' as const,
    };
  });
}

/** Número de jefes de equipo de una jerarquía con `n` agentes de trabajo. */
export function teamLeaders(n: number): number {
  return Math.ceil(clamp(n) / TEAM_SIZE);
}

/** Grafo de la topología para `n` agentes de trabajo (se acota entre 2 y 9). */
export function buildTopology(id: TopologyId, agents: number): TopologyGraph {
  const n = clamp(agents);
  const edges: [string, string][] = [];

  if (id === 'cadena') {
    const nodes = row(n, H / 2, 'a', (i) => `A${i + 1}`);
    for (let i = 0; i < n - 1; i++) edges.push([nodes[i].id, nodes[i + 1].id]);
    return { nodes, edges };
  }

  if (id === 'supervisor') {
    const sup: TopologyNode = { id: 's', label: 'Sup', x: W / 2, y: 40, role: 'coordinador' };
    const workers = row(n, H - 50, 'a', (i) => `A${i + 1}`);
    for (const w of workers) edges.push([sup.id, w.id]);
    return { nodes: [sup, ...workers], edges };
  }

  if (id === 'jerarquia') {
    const leaders = teamLeaders(n);
    const top: TopologyNode = { id: 's', label: 'Sup', x: W / 2, y: 32, role: 'coordinador' };
    const leaderNodes = row(leaders, 125, 'l', (i) => `J${i + 1}`).map((node) => ({
      ...node,
      role: 'coordinador' as const,
    }));
    const workers = row(n, H - 40, 'a', (i) => `A${i + 1}`);
    for (const l of leaderNodes) edges.push([top.id, l.id]);
    workers.forEach((w, i) => edges.push([leaderNodes[Math.floor(i / TEAM_SIZE)].id, w.id]));
    return { nodes: [top, ...leaderNodes, ...workers], edges };
  }

  if (id === 'red') {
    const nodes = circle(n, 'a', W / 2, H / 2, 100);
    for (let i = 0; i < n; i++) {
      for (let j = i + 1; j < n; j++) edges.push([nodes[i].id, nodes[j].id]);
    }
    return { nodes, edges };
  }

  const board: TopologyNode = { id: 'p', label: 'Pizarra', x: W / 2, y: H / 2, role: 'pizarra' };
  const nodes = circle(n, 'a', W / 2, H / 2, 105);
  for (const node of nodes) edges.push([node.id, board.id]);
  return { nodes: [board, ...nodes], edges };
}

/** Métricas de coordinación con la misma definición que el grafo (los canales se cuentan de ahí). */
export function topologyMetrics(id: TopologyId, agents: number): TopologyMetrics {
  const n = clamp(agents);
  const channels = buildTopology(id, n).edges.length;
  switch (id) {
    case 'cadena':
      return { workers: n, channels, hops: n - 1, singlePoints: 'cualquier agente de la cadena' };
    case 'supervisor':
      return { workers: n, channels, hops: 1, singlePoints: 'el supervisor' };
    case 'jerarquia':
      return { workers: n, channels, hops: 2, singlePoints: 'el supervisor y cada jefe de equipo' };
    case 'red':
      return {
        workers: n,
        channels,
        hops: 1,
        singlePoints: 'ninguno, pero cada agente depende de todos',
      };
    case 'blackboard':
      return { workers: n, channels, hops: 2, singlePoints: 'la pizarra' };
  }
}
