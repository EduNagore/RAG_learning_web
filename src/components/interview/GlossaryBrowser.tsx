import { useMemo, useState } from 'react';
import { filterTerms, type GlossaryTerm } from '../../lib/glossary';

export type { GlossaryTerm };

export default function GlossaryBrowser({ terms }: { terms: GlossaryTerm[] }) {
  const [query, setQuery] = useState('');
  const visible = useMemo(() => filterTerms(terms, query), [terms, query]);

  return (
    <div className="space-y-4">
      <label className="block text-sm">
        Buscar un término (español o inglés)
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="mt-1 w-full max-w-md rounded-md border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-900"
        />
      </label>
      <p role="status" className="text-sm font-medium">
        {visible.length} de {terms.length} términos
      </p>
      <dl className="space-y-4">
        {visible.map((t) => (
          <div
            key={t.id}
            id={t.id}
            data-testid="glossary-term"
            className="rounded-lg border border-slate-200 p-4 dark:border-slate-800"
          >
            <dt className="font-semibold">
              {t.es}
              {t.en.toLowerCase() !== t.es.toLowerCase() && (
                <span className="ml-2 font-normal text-slate-500">· {t.en}</span>
              )}
            </dt>
            <dd className="mt-1 text-sm">
              {t.def}
              {t.lessons.length > 0 && (
                <span className="mt-2 block text-slate-600 dark:text-slate-400">
                  Más en:{' '}
                  {t.lessons.map((l, i) => (
                    <span key={l.id}>
                      {i > 0 && ', '}
                      <a
                        href={l.href}
                        className="text-indigo-700 underline underline-offset-2 dark:text-indigo-300"
                      >
                        {l.title}
                      </a>
                    </span>
                  ))}
                </span>
              )}
            </dd>
          </div>
        ))}
      </dl>
      {visible.length === 0 && (
        <p className="text-sm text-slate-500">Ningún término coincide con la búsqueda.</p>
      )}
    </div>
  );
}
