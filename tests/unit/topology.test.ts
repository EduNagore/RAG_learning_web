import { describe, expect, it } from 'vitest';
import {
  MAX_AGENTS,
  MIN_AGENTS,
  TOPOLOGIES,
  buildTopology,
  teamLeaders,
  topologyMetrics,
  type TopologyId,
} from '../../src/lib/topology';

const ids = TOPOLOGIES.map((t) => t.id);

describe('buildTopology', () => {
  it('los canales de cada topología siguen su fórmula', () => {
    const n = 6;
    expect(topologyMetrics('cadena', n).channels).toBe(n - 1);
    expect(topologyMetrics('supervisor', n).channels).toBe(n);
    expect(topologyMetrics('red', n).channels).toBe((n * (n - 1)) / 2);
    expect(topologyMetrics('blackboard', n).channels).toBe(n);
    expect(topologyMetrics('jerarquia', n).channels).toBe(teamLeaders(n) + n);
  });

  it('la red crece de forma cuadrática y el supervisor de forma lineal', () => {
    const red = (n: number) => topologyMetrics('red', n).channels;
    const sup = (n: number) => topologyMetrics('supervisor', n).channels;
    expect(red(8)).toBe(28);
    expect(sup(8)).toBe(8);
    expect(red(MAX_AGENTS) / red(MAX_AGENTS / 3)).toBeGreaterThan(
      sup(MAX_AGENTS) / sup(MAX_AGENTS / 3),
    );
  });

  it('todas las aristas unen nodos existentes y no hay nodos repetidos', () => {
    for (const id of ids) {
      for (let n = MIN_AGENTS; n <= MAX_AGENTS; n++) {
        const graph = buildTopology(id as TopologyId, n);
        const nodeIds = new Set(graph.nodes.map((node) => node.id));
        expect(nodeIds.size).toBe(graph.nodes.length);
        for (const [a, b] of graph.edges) {
          expect(nodeIds.has(a)).toBe(true);
          expect(nodeIds.has(b)).toBe(true);
          expect(a).not.toBe(b);
        }
      }
    }
  });

  it('hay tantos agentes de trabajo como se piden y los nodos caben en el lienzo', () => {
    for (const id of ids) {
      const graph = buildTopology(id, 5);
      expect(graph.nodes.filter((node) => node.role === 'agente')).toHaveLength(5);
      for (const node of graph.nodes) {
        expect(node.x).toBeGreaterThanOrEqual(0);
        expect(node.x).toBeLessThanOrEqual(440);
        expect(node.y).toBeGreaterThanOrEqual(0);
        expect(node.y).toBeLessThanOrEqual(280);
      }
    }
  });

  it('la jerarquía agrupa los agentes en equipos de hasta 3', () => {
    expect(teamLeaders(2)).toBe(1);
    expect(teamLeaders(3)).toBe(1);
    expect(teamLeaders(4)).toBe(2);
    expect(teamLeaders(9)).toBe(3);
    const graph = buildTopology('jerarquia', 7);
    const perLeader = new Map<string, number>();
    for (const [a, b] of graph.edges) {
      if (a.startsWith('l') && b.startsWith('a')) perLeader.set(a, (perLeader.get(a) ?? 0) + 1);
    }
    expect([...perLeader.values()].sort()).toEqual([1, 3, 3]);
  });

  it('el número de agentes se acota al rango permitido', () => {
    expect(buildTopology('cadena', 0).nodes).toHaveLength(MIN_AGENTS);
    expect(buildTopology('cadena', 99).nodes).toHaveLength(MAX_AGENTS);
  });
});

describe('topologyMetrics', () => {
  it('la cadena tarda tantos saltos como agentes menos uno', () => {
    expect(topologyMetrics('cadena', 5).hops).toBe(4);
  });

  it('indica los puntos únicos de fallo', () => {
    expect(topologyMetrics('supervisor', 4).singlePoints).toMatch(/supervisor/);
    expect(topologyMetrics('blackboard', 4).singlePoints).toMatch(/pizarra/);
    expect(topologyMetrics('jerarquia', 4).singlePoints).toMatch(/jefe/);
  });
});
