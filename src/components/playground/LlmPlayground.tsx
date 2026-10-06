import { useEffect, useState } from 'react';
import {
  DEFAULT_MODEL,
  KEY_STORAGE,
  MODEL_STORAGE,
  PROFILES,
  buildRequest,
  buildUserPrompt,
  invalidCitations,
  maskKey,
  parseResponse,
  retrieve,
  type NimbusDoc,
  type ParsedResponse,
  type Profile,
  type RetrievedDoc,
} from '../../lib/playground';

const field =
  'rounded-md border border-slate-300 px-2 py-1 text-sm dark:border-slate-700 dark:bg-slate-900';
const button =
  'rounded-md border border-slate-300 px-3 py-1 text-sm hover:bg-slate-100 disabled:opacity-40 dark:border-slate-700 dark:hover:bg-slate-800';

function readStorage(key: string): string {
  try {
    return localStorage.getItem(key) ?? '';
  } catch {
    return '';
  }
}

function writeStorage(key: string, value: string) {
  try {
    if (value) localStorage.setItem(key, value);
    else localStorage.removeItem(key);
  } catch {
    /* sin almacenamiento disponible: la clave solo vive mientras la página esté abierta */
  }
}

export default function LlmPlayground({ corpusUrl }: { corpusUrl: string }) {
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState(DEFAULT_MODEL);
  const [remember, setRemember] = useState(false);
  const [question, setQuestion] = useState('¿Cuál es el plazo de devolución de un pedido?');
  const [profile, setProfile] = useState<Profile>('publico');
  const [k, setK] = useState(3);
  const [corpus, setCorpus] = useState<NimbusDoc[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [docs, setDocs] = useState<RetrievedDoc[]>([]);
  const [result, setResult] = useState<ParsedResponse | null>(null);
  const [fatal, setFatal] = useState('');

  useEffect(() => {
    const stored = readStorage(KEY_STORAGE);
    if (stored) {
      setApiKey(stored);
      setRemember(true);
    }
    setModel(readStorage(MODEL_STORAGE) || DEFAULT_MODEL);
    fetch(corpusUrl)
      .then((r) => r.json())
      .then((data: NimbusDoc[]) => setCorpus(data))
      .catch(() => setFatal('No se pudo cargar el corpus de demostración.'));
  }, [corpusUrl]);

  const clearKey = () => {
    writeStorage(KEY_STORAGE, '');
    setApiKey('');
    setRemember(false);
  };

  const run = async () => {
    if (!corpus) return;
    setFatal('');
    setResult(null);
    writeStorage(KEY_STORAGE, remember ? apiKey : '');
    writeStorage(MODEL_STORAGE, model);
    const retrieved = retrieve(corpus, question, k, profile);
    setDocs(retrieved);
    const req = buildRequest(apiKey, model, buildUserPrompt(question, retrieved));
    setLoading(true);
    try {
      const response = await fetch(req.url, req.init);
      setResult(parseResponse(await response.json()));
    } catch {
      setFatal(
        'No se pudo completar la petición. Comprueba la conexión y que el proveedor admita peticiones desde el navegador (CORS).',
      );
    } finally {
      setLoading(false);
    }
  };

  const bad = result && !result.error ? invalidCitations(result.text, docs) : [];

  return (
    <div className="space-y-5">
      <div
        role="note"
        className="rounded-lg border border-amber-300 bg-amber-50 p-4 text-sm dark:border-amber-800 dark:bg-amber-950/40"
      >
        <p className="font-semibold">Antes de usar tu clave</p>
        <ul className="mt-1 list-disc space-y-1 pl-5">
          <li>
            La clave se envía <strong>solo</strong> a <code>api.anthropic.com</code>. Esta web no
            tiene servidor y no la recibe.
          </li>
          <li>
            Si marcas «Recordar», se guarda en el <code>localStorage</code> de este navegador, donde
            puede leerla cualquiera con acceso al equipo y cualquier extensión con permisos.
          </li>
          <li>
            Usa una clave con <strong>límite de gasto</strong> y bórrala al terminar. Cada pregunta
            cuesta tokens reales.
          </li>
        </ul>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <label className="block text-sm">
          Clave de API
          <input
            type="password"
            autoComplete="off"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            className={`${field} mt-1 w-full`}
          />
          {apiKey && <span className="text-xs text-slate-500">Clave: {maskKey(apiKey)}</span>}
        </label>
        <label className="block text-sm">
          Modelo
          <input
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className={`${field} mt-1 w-full`}
          />
          <span className="text-xs text-slate-500">
            Consulta en la documentación del proveedor los modelos vigentes.
          </span>
        </label>
      </div>
      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} />
        Recordar la clave en este navegador
      </label>

      <label className="block text-sm">
        Pregunta sobre el corpus de Nimbus
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          rows={2}
          className={`${field} mt-1 w-full`}
        />
      </label>
      <div className="flex flex-wrap gap-4">
        <label className="block text-sm">
          Perfil de acceso
          <select
            value={profile}
            onChange={(e) => setProfile(e.target.value as Profile)}
            className={`${field} ml-2`}
          >
            {(Object.keys(PROFILES) as Profile[]).map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </label>
        <label className="block text-sm">
          Documentos (k): {k}
          <input
            type="range"
            min={1}
            max={8}
            value={k}
            onChange={(e) => setK(Number(e.target.value))}
            className="ml-2 align-middle"
          />
        </label>
      </div>

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          className={button}
          onClick={run}
          disabled={!apiKey || !question.trim() || !corpus || loading}
        >
          {loading ? 'Consultando…' : 'Preguntar'}
        </button>
        <button type="button" className={button} onClick={clearKey} disabled={!apiKey}>
          Borrar la clave
        </button>
      </div>

      {fatal && (
        <p role="alert" className="text-sm text-red-700 dark:text-red-300">
          {fatal}
        </p>
      )}
      {result?.error && (
        <p role="alert" className="text-sm text-red-700 dark:text-red-300">
          Error de la API: {result.error}
        </p>
      )}

      {docs.length > 0 && (
        <section aria-labelledby="recuperados">
          <h2 id="recuperados" className="text-lg font-semibold">
            Documentos recuperados (perfil {profile})
          </h2>
          <ul className="mt-2 space-y-1 text-sm">
            {docs.map((d) => (
              <li key={d.id}>
                <code>{d.id}</code> · {d.title} · {d.access} · similitud {d.score.toFixed(3)}
              </li>
            ))}
          </ul>
        </section>
      )}

      {result && !result.error && (
        <section aria-labelledby="respuesta">
          <h2 id="respuesta" className="text-lg font-semibold">
            Respuesta
          </h2>
          <p className="mt-2 whitespace-pre-line text-sm" data-testid="answer">
            {result.text}
          </p>
          <p role="status" className="mt-2 text-xs text-slate-500">
            {result.abstained ? 'El modelo se abstuvo. ' : ''}
            {result.inputTokens !== undefined
              ? `Tokens: ${result.inputTokens} de entrada y ${result.outputTokens ?? '?'} de salida. `
              : ''}
            {bad.length > 0
              ? `Citas a documentos no recuperados: ${bad.join(', ')}.`
              : 'Todas las citas corresponden a documentos recuperados.'}
          </p>
        </section>
      )}
    </div>
  );
}
