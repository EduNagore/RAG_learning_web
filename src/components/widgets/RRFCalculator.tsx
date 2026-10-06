import { useMemo, useState } from 'react';
import { parseRanking, rrfFuse } from '../../lib/rrf';

const field =
  'rounded-md border border-slate-300 px-2 py-1 text-sm dark:border-slate-700 dark:bg-slate-900';

export default function RRFCalculator() {
  const [lexical, setLexical] = useState('A, B, C, D');
  const [dense, setDense] = useState('C, A, E, B');
  const [k, setK] = useState(60);

  const fused = useMemo(
    () => rrfFuse([parseRanking(lexical), parseRanking(dense)], k),
    [lexical, dense, k],
  );
  const leader = fused[0];

  return (
    <div className="not-prose my-8 space-y-4 rounded-xl border border-slate-200 p-5 dark:border-slate-800">
      <h3 className="text-lg font-semibold">Calculadora de RRF</h3>
      <p className="text-sm text-slate-600 dark:text-slate-400">
        Escribe los resultados de cada buscador (de mejor a peor, separados por comas) y mueve la
        constante <em>k</em>. Cada documento suma <code>1 / (k + posición)</code> por cada lista
        donde aparece. Prueba <code>k = 0</code> y <code>k = 60</code> y observa cómo cambia el
        primero.
      </p>

      <div className="grid gap-3 sm:grid-cols-2">
        <label className="block text-sm">
          Búsqueda léxica (BM25)
          <input
            value={lexical}
            onChange={(e) => setLexical(e.target.value)}
            className={`${field} mt-1 w-full`}
          />
        </label>
        <label className="block text-sm">
          Búsqueda densa
          <input
            value={dense}
            onChange={(e) => setDense(e.target.value)}
            className={`${field} mt-1 w-full`}
          />
        </label>
      </div>
      <label className="block text-sm">
        Constante k: {k}
        <input
          type="range"
          min={0}
          max={200}
          value={k}
          onChange={(e) => setK(Number(e.target.value))}
          className="ml-2 align-middle"
        />
      </label>

      <p role="status" className="text-sm font-medium">
        {leader
          ? `Primero: ${leader.id} con puntuación ${leader.score.toFixed(5)} (${fused.length} documentos)`
          : 'Escribe al menos un resultado en alguna lista.'}
      </p>

      {fused.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm" aria-label="Resultado de la fusión RRF">
            <thead>
              <tr className="border-b border-slate-300 text-left dark:border-slate-700">
                <th className="p-1">#</th>
                <th className="p-1">Documento</th>
                <th className="p-1">Posición léxica</th>
                <th className="p-1">Posición densa</th>
                <th className="p-1">Puntuación RRF</th>
              </tr>
            </thead>
            <tbody>
              {fused.map((d, i) => (
                <tr key={d.id} className="border-b border-slate-100 dark:border-slate-800">
                  <td className="p-1">{i + 1}</td>
                  <th scope="row" className="p-1 text-left font-medium">
                    {d.id}
                  </th>
                  <td className="p-1">{d.ranks[0] ?? '—'}</td>
                  <td className="p-1">{d.ranks[1] ?? '—'}</td>
                  <td className="p-1 tabular-nums">{d.score.toFixed(5)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
