import { useState } from 'react';
import {
  MAX_AGENTS,
  MIN_AGENTS,
  TOPOLOGIES,
  buildTopology,
  topologyMetrics,
  type TopologyId,
} from '../../lib/topology';

const NODE_STYLES = {
  coordinador: 'fill-violet-200 stroke-violet-600 dark:fill-violet-900',
  agente: 'fill-sky-100 stroke-sky-600 dark:fill-sky-900',
  pizarra: 'fill-amber-100 stroke-amber-600 dark:fill-amber-900',
} as const;

export default function TopologyExplorer() {
  const [topology, setTopology] = useState<TopologyId>('supervisor');
  const [agents, setAgents] = useState(6);
  const info = TOPOLOGIES.find((t) => t.id === topology) ?? TOPOLOGIES[0];
  const graph = buildTopology(topology, agents);
  const metrics = topologyMetrics(topology, agents);
  const byId = new Map(graph.nodes.map((n) => [n.id, n]));

  return (
    <div className="not-prose my-8 space-y-4 rounded-xl border border-slate-200 p-5 dark:border-slate-800">
      <h3 className="text-lg font-semibold">Explorador de topologías multiagente</h3>
      <p className="text-sm text-slate-600 dark:text-slate-400">
        Cambia la topología y el número de agentes de trabajo: el grafo se redibuja y se recalculan
        los canales de comunicación que hay que diseñar, probar y vigilar. Fíjate en cómo crece cada
        una.
      </p>

      <div className="flex flex-wrap items-center gap-4">
        <label className="block text-sm">
          Topología
          <select
            value={topology}
            onChange={(e) => setTopology(e.target.value as TopologyId)}
            className="ml-2 rounded-md border border-slate-300 px-2 py-1 text-sm dark:border-slate-700 dark:bg-slate-900"
          >
            {TOPOLOGIES.map((t) => (
              <option key={t.id} value={t.id}>
                {t.title}
              </option>
            ))}
          </select>
        </label>
        <label className="block text-sm">
          Agentes de trabajo: {agents}
          <input
            type="range"
            min={MIN_AGENTS}
            max={MAX_AGENTS}
            value={agents}
            onChange={(e) => setAgents(Number(e.target.value))}
            className="ml-2 align-middle"
          />
        </label>
      </div>

      <p className="text-sm">{info.description}</p>

      <svg
        viewBox="0 0 440 280"
        role="img"
        aria-label={`Grafo de la topología ${info.title} con ${agents} agentes de trabajo y ${metrics.channels} canales`}
        className="w-full max-w-xl rounded-md border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950"
      >
        {graph.edges.map(([a, b]) => {
          const from = byId.get(a)!;
          const to = byId.get(b)!;
          return (
            <line
              key={`${a}-${b}`}
              x1={from.x}
              y1={from.y}
              x2={to.x}
              y2={to.y}
              className="stroke-slate-400 dark:stroke-slate-600"
              strokeWidth={1.5}
            />
          );
        })}
        {graph.nodes.map((node) => (
          <g key={node.id}>
            <circle
              cx={node.x}
              cy={node.y}
              r={17}
              strokeWidth={2}
              className={NODE_STYLES[node.role]}
            />
            <text
              x={node.x}
              y={node.y + 4}
              textAnchor="middle"
              className="fill-slate-900 text-[10px] font-medium dark:fill-slate-100"
            >
              {node.label}
            </text>
          </g>
        ))}
      </svg>

      <p role="status" className="text-sm font-medium">
        {metrics.channels} canales de comunicación para {metrics.workers} agentes · saltos mínimos
        de un reparto: {metrics.hops} · puntos únicos de fallo: {metrics.singlePoints}
      </p>

      <p className="text-xs text-slate-500">
        Modelo simplificado: cuenta canales y saltos del grafo, no tokens ni calidad. Los costes
        reales dependen de lo que se diga por cada canal (véase la economía de tokens).
      </p>
    </div>
  );
}
