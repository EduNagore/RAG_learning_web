import { useMemo, useState } from 'react';
import { chunkFixed, chunkMarkdown, chunkRecursive } from '../../lib/chunking';

const SAMPLE = `# Devoluciones

Los clientes particulares disponen de 14 días naturales desde la fecha de entrega para devolver un pedido sin necesidad de justificación. El artículo debe estar sin usar, con sus etiquetas y en el embalaje original.

## Plazos

Los clientes empresa disponen de 7 días naturales. Pasado ese plazo no se aceptan devoluciones, salvo defecto de fabricación cubierto por la garantía.

## Reembolsos

El reembolso se realiza por el mismo medio de pago y tarda un máximo de 7 días hábiles desde que el paquete devuelto llega al almacén y supera la inspección.`;

type Strategy = 'fixed' | 'recursive' | 'markdown';

const COLORS = [
  'bg-indigo-100 dark:bg-indigo-950',
  'bg-emerald-100 dark:bg-emerald-950',
  'bg-amber-100 dark:bg-amber-950',
  'bg-sky-100 dark:bg-sky-950',
  'bg-rose-100 dark:bg-rose-950',
];

export default function ChunkingVisualizer() {
  const [text, setText] = useState(SAMPLE);
  const [strategy, setStrategy] = useState<Strategy>('recursive');
  const [size, setSize] = useState(25);
  const [overlap, setOverlap] = useState(5);
  const [maxChars, setMaxChars] = useState(200);

  const safeOverlap = Math.min(overlap, size - 1);
  const chunks = useMemo(() => {
    if (strategy === 'fixed')
      return chunkFixed(text, size, safeOverlap).map((t) => ({ text: t, path: '' }));
    if (strategy === 'recursive')
      return chunkRecursive(text, maxChars).map((t) => ({ text: t, path: '' }));
    return chunkMarkdown(text, maxChars).map((c) => ({ text: c.text, path: c.path }));
  }, [text, strategy, size, safeOverlap, maxChars]);

  const lengths = chunks.map((c) => c.text.length);
  const avg = lengths.length ? Math.round(lengths.reduce((a, b) => a + b, 0) / lengths.length) : 0;
  const field =
    'rounded-md border border-slate-300 px-2 py-1 text-sm dark:border-slate-700 dark:bg-slate-900';

  return (
    <div className="not-prose my-8 space-y-4 rounded-xl border border-slate-200 p-5 dark:border-slate-800">
      <h3 className="text-lg font-semibold">Visualizador de chunking</h3>
      <p className="text-sm text-slate-600 dark:text-slate-400">
        Pega un texto, elige una estrategia y mueve los controles para ver cómo se corta. Usa la
        misma lógica que las soluciones de los laboratorios.
      </p>

      <label className="block text-sm">
        Texto
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={6}
          className={`${field} mt-1 w-full font-mono`}
        />
      </label>

      <div className="flex flex-wrap items-end gap-4">
        <label className="text-sm">
          Estrategia
          <select
            value={strategy}
            onChange={(e) => setStrategy(e.target.value as Strategy)}
            className={`${field} ml-2`}
          >
            <option value="fixed">Tamaño fijo (palabras)</option>
            <option value="recursive">Recursivo (caracteres)</option>
            <option value="markdown">Por encabezados Markdown</option>
          </select>
        </label>
        {strategy === 'fixed' ? (
          <>
            <label className="text-sm">
              Tamaño: {size} palabras
              <input
                type="range"
                min={5}
                max={80}
                value={size}
                onChange={(e) => setSize(Number(e.target.value))}
                className="ml-2 align-middle"
              />
            </label>
            <label className="text-sm">
              Solape: {safeOverlap} palabras
              <input
                type="range"
                min={0}
                max={Math.max(size - 1, 0)}
                value={safeOverlap}
                onChange={(e) => setOverlap(Number(e.target.value))}
                className="ml-2 align-middle"
              />
            </label>
          </>
        ) : (
          <label className="text-sm">
            Máximo: {maxChars} caracteres
            <input
              type="range"
              min={60}
              max={600}
              step={10}
              value={maxChars}
              onChange={(e) => setMaxChars(Number(e.target.value))}
              className="ml-2 align-middle"
            />
          </label>
        )}
      </div>

      <p role="status" className="text-sm font-medium">
        {chunks.length} fragmentos · longitud media {avg} caracteres
        {lengths.length ? ` · máximo ${Math.max(...lengths)}` : ''}
      </p>

      <ol className="space-y-2">
        {chunks.map((c, i) => (
          <li key={i} className={`rounded-lg p-3 text-sm ${COLORS[i % COLORS.length]}`}>
            <p className="mb-1 text-xs text-slate-600 dark:text-slate-400">
              Fragmento {i + 1} · {c.text.length} caracteres
              {c.path && ` · ruta: ${c.path}`}
            </p>
            <p className="whitespace-pre-wrap">
              {strategy === 'fixed' && i > 0 && safeOverlap > 0 ? (
                <>
                  <mark className="rounded bg-yellow-200 px-0.5 dark:bg-yellow-700">
                    {c.text.split(' ').slice(0, safeOverlap).join(' ')}
                  </mark>{' '}
                  {c.text.split(' ').slice(safeOverlap).join(' ')}
                </>
              ) : (
                c.text
              )}
            </p>
          </li>
        ))}
      </ol>
      {strategy === 'fixed' && safeOverlap > 0 && (
        <p className="text-xs text-slate-500">
          Lo resaltado en amarillo es el solape: palabras que el fragmento comparte con el anterior.
        </p>
      )}
    </div>
  );
}
