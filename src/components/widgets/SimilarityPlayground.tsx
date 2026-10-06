import { useMemo, useState } from 'react';
import { HashingEmbedder, cosine } from '../../lib/embeddings';

const SAMPLE = [
  'El reembolso tarda 7 días hábiles en llegar',
  'Cuánto tarda el reembolso de un pedido',
  'El envío exprés cuesta 9,95 euros',
  'Horario del chat de atención al cliente',
  'Plazo para devolver un artículo',
].join('\n');

/** Escala de color: blanco (0) a índigo (1). Los negativos se muestran en gris. */
const shade = (v: number) =>
  v < 0 ? 'rgb(226 232 240)' : `rgba(79, 70, 229, ${Math.min(1, Math.max(0, v)).toFixed(2)})`;

export default function SimilarityPlayground() {
  const [text, setText] = useState(SAMPLE);
  const [query, setQuery] = useState('¿En cuánto tiempo me devuelven el dinero?');
  const [dim, setDim] = useState(512);

  const sentences = useMemo(
    () =>
      text
        .split('\n')
        .map((s) => s.trim())
        .filter(Boolean)
        .slice(0, 8),
    [text],
  );
  const embedder = useMemo(() => new HashingEmbedder(dim), [dim]);
  const vectors = useMemo(() => sentences.map((s) => embedder.embed(s)), [sentences, embedder]);
  const ranking = useMemo(() => {
    const q = embedder.embed(query);
    return sentences
      .map((s, i) => ({ s, score: cosine(q, vectors[i]) }))
      .sort((a, b) => b.score - a.score);
  }, [query, sentences, vectors, embedder]);

  const field =
    'rounded-md border border-slate-300 px-2 py-1 text-sm dark:border-slate-700 dark:bg-slate-900';

  return (
    <div className="not-prose my-8 space-y-4 rounded-xl border border-slate-200 p-5 dark:border-slate-800">
      <h3 className="text-lg font-semibold">Laboratorio de similitud</h3>
      <p className="text-sm text-slate-600 dark:text-slate-400">
        Escribe una frase por línea (máximo 8) y mira la matriz de similitud coseno. Usa el embedder
        de juguete del curso (hashing): comparte palabras, pero{' '}
        <strong>no entiende sinónimos</strong>, a diferencia de un modelo real. Prueba la consulta
        de abajo, que no comparte casi ninguna palabra con la frase del reembolso.
      </p>

      <label className="block text-sm">
        Frases
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={5}
          className={`${field} mt-1 w-full`}
        />
      </label>
      <label className="block text-sm">
        Dimensión del vector: {dim}
        <input
          type="range"
          min={32}
          max={1024}
          step={32}
          value={dim}
          onChange={(e) => setDim(Number(e.target.value))}
          className="ml-2 align-middle"
        />
      </label>

      <div className="overflow-x-auto">
        <table className="border-collapse text-xs" aria-label="Matriz de similitud coseno">
          <thead>
            <tr>
              <th className="p-1" />
              {sentences.map((_, j) => (
                <th key={j} className="p-1 font-medium">
                  F{j + 1}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sentences.map((s, i) => (
              <tr key={i}>
                <th scope="row" className="max-w-48 truncate p-1 text-left font-medium" title={s}>
                  F{i + 1} · {s}
                </th>
                {sentences.map((_, j) => {
                  const v = cosine(vectors[i], vectors[j]);
                  return (
                    <td
                      key={j}
                      className="size-12 border border-white text-center dark:border-slate-950"
                      style={{ background: shade(v), color: v > 0.5 ? 'white' : undefined }}
                    >
                      {v.toFixed(2)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <label className="block text-sm">
        Consulta
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className={`${field} mt-1 w-full`}
        />
      </label>
      <ol className="space-y-1 text-sm" aria-label="Frases ordenadas por similitud con la consulta">
        {ranking.map((r, i) => (
          <li key={r.s} className="flex gap-3">
            <span className="w-12 font-mono">{r.score.toFixed(3)}</span>
            <span className={i === 0 ? 'font-semibold' : ''}>{r.s}</span>
          </li>
        ))}
      </ol>
    </div>
  );
}
