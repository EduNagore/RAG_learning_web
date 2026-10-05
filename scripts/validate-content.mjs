// Validación de contenido: referencias cruzadas y estructura que el esquema Zod no puede comprobar.
// Uso: node scripts/validate-content.mjs   (sale con código 1 si hay errores)
import { readdirSync, readFileSync, existsSync } from 'node:fs';
import { join, relative, sep } from 'node:path';
import { parse as parseYaml } from 'yaml';
import GithubSlugger from 'github-slugger';

const ROOT = new URL('..', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1');
const CONTENT = join(ROOT, 'src', 'content');
const MIN_WORDS = 1500; // PLAN.md §7.1: 1.500-3.000 palabras por lección (sin contar código)

const errors = [];
const warnings = [];
const err = (file, msg) => errors.push(`${file}: ${msg}`);
const warn = (file, msg) => warnings.push(`${file}: ${msg}`);

const walk = (dir, ext) =>
  existsSync(dir)
    ? readdirSync(dir, { withFileTypes: true }).flatMap((d) =>
        d.isDirectory()
          ? walk(join(dir, d.name), ext)
          : d.name.endsWith(ext)
            ? [join(dir, d.name)]
            : [],
      )
    : [];
const rel = (p) => relative(ROOT, p).split(sep).join('/');
const idOf = (base, file) =>
  relative(base, file)
    .split(sep)
    .join('/')
    .replace(/\.[^.]+$/, '');

function splitFrontmatter(text) {
  const m = text.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
  return m ? { data: parseYaml(m[1]), body: m[2] } : null;
}

const stripCode = (body) => body.replace(/```[\s\S]*?```/g, '');

// --- Módulos -----------------------------------------------------------------
const moduleIds = new Set(
  walk(join(CONTENT, 'modules'), '.yaml').map((f) => idOf(join(CONTENT, 'modules'), f)),
);
const moduleOrders = new Map();
for (const f of walk(join(CONTENT, 'modules'), '.yaml')) {
  const { order } = parseYaml(readFileSync(f, 'utf8'));
  if (moduleOrders.has(order))
    err(rel(f), `order ${order} repetido (también en ${moduleOrders.get(order)})`);
  moduleOrders.set(order, rel(f));
}

// --- Lecciones ---------------------------------------------------------------
const lessonsDir = join(CONTENT, 'lessons');
const lessons = new Map(); // id -> { file, data, body, anchors }
for (const file of walk(lessonsDir, '.mdx')) {
  const id = idOf(lessonsDir, file);
  const fm = splitFrontmatter(readFileSync(file, 'utf8'));
  if (!fm) {
    err(rel(file), 'falta el frontmatter');
    continue;
  }
  const slugger = new GithubSlugger();
  const anchors = new Set(
    [...stripCode(fm.body).matchAll(/^#{2,4}\s+(.+)$/gm)].map((m) =>
      slugger.slug(
        m[1]
          .replace(/`/g, '')
          .replace(/[*_]/g, '')
          .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1'),
      ),
    ),
  );
  lessons.set(id, { file, data: fm.data, body: fm.body, anchors });
}

const orderByModule = new Map();
for (const [id, { file, data, body }] of lessons) {
  const f = rel(file);
  const folder = id.split('/')[0];
  if (data.module !== folder)
    err(f, `module "${data.module}" no coincide con la carpeta "${folder}"`);
  if (!moduleIds.has(data.module))
    err(f, `el módulo "${data.module}" no existe en src/content/modules`);

  const key = `${data.module}#${data.order}`;
  if (orderByModule.has(key))
    err(f, `order ${data.order} repetido en ${data.module} (también en ${orderByModule.get(key)})`);
  orderByModule.set(key, f);

  for (const p of data.prerequisites ?? []) {
    if (!lessons.has(p)) err(f, `prerequisito inexistente: ${p}`);
    if (p === id) err(f, 'es prerequisito de sí misma');
  }

  const urls = (data.sources ?? []).map((s) => s.url);
  if (new Set(urls).size !== urls.length) err(f, 'fuentes con URL repetida');
  if (new Date(data.lastReviewed) > new Date())
    err(f, `lastReviewed en el futuro: ${data.lastReviewed}`);
  if (data.volatility === 'high' && !/<Snapshot\b/.test(body))
    err(f, 'volatility high requiere al menos un <Snapshot date="...">');
  for (const m of body.matchAll(/<Snapshot\b[^>]*date="([^"]*)"/g))
    if (!/^\d{4}-\d{2}(-\d{2})?$/.test(m[1]))
      err(f, `<Snapshot date="${m[1]}"> debe ser AAAA-MM o AAAA-MM-DD`);

  // Estructura de lección (PLAN.md §9)
  const prose = stripCode(body);
  if (!/^## .*Trade-offs/m.test(prose)) err(f, 'falta una sección "## … Trade-offs …"');
  if (!/^## Errores comunes/m.test(prose)) err(f, 'falta la sección "## Errores comunes …"');
  if (!/<Callout\s+type="entrevista"/.test(body)) err(f, 'falta el <Callout type="entrevista">');
  if (!/<KeyTakeaways>/.test(body)) err(f, 'falta <KeyTakeaways>');
  if (!/<Diagram\b/.test(body)) warn(f, 'sin <Diagram> (se espera al menos uno por módulo)');

  const words = prose
    .replace(/<[^>]+>/g, ' ')
    .split(/\s+/)
    .filter(Boolean).length;
  if (words < MIN_WORDS) err(f, `${words} palabras (mínimo ${MIN_WORDS} sin contar código)`);
  if (words > 3200) warn(f, `${words} palabras (el plan recomienda ≤ 3000)`);
}

// --- Quizzes -----------------------------------------------------------------
const quizzesDir = join(CONTENT, 'quizzes');
const questionIds = new Map();
const tfByModule = new Map(); // módulo -> { v: nº verdaderas, f: nº falsas }
for (const file of walk(quizzesDir, '.yaml')) {
  const f = rel(file);
  const quiz = parseYaml(readFileSync(file, 'utf8'));
  const lesson = lessons.get(quiz.lesson);
  if (!lesson) {
    err(f, `la lección "${quiz.lesson}" no existe`);
    continue;
  }
  if (idOf(quizzesDir, file) !== quiz.lesson)
    err(f, `el nombre del archivo debe coincidir con la lección (${quiz.lesson})`);
  if (quiz.questions.length < 6 || quiz.questions.length > 10)
    warn(f, `${quiz.questions.length} preguntas (se esperan 6-10)`);
  for (const q of quiz.questions) {
    if (questionIds.has(q.id))
      err(f, `id de pregunta repetido: ${q.id} (también en ${questionIds.get(q.id)})`);
    questionIds.set(q.id, f);
    if (q.ref && !lesson.anchors.has(q.ref.replace(/^#/, '')))
      err(f, `${q.id}: ancla "${q.ref}" no existe en la lección`);
    if (!q.explanation || q.explanation.trim().length < 40)
      err(f, `${q.id}: explicación demasiado corta`);
    if (q.type === 'truefalse') {
      const t = tfByModule.get(lesson.data.module) ?? { v: 0, f: 0 };
      if (q.answer[0] === 0) t.v++;
      else t.f++;
      tfByModule.set(lesson.data.module, t);
    }
  }
}
// Si casi todas las verdadero/falso de un módulo tienen la misma respuesta, se acierta sin saber.
for (const [mod, { v, f }] of tfByModule) {
  const total = v + f;
  if (total >= 4 && Math.max(v, f) / total >= 0.8)
    err(
      `quizzes/${mod}`,
      `verdadero/falso desequilibradas (${v} verdaderas, ${f} falsas): reparte las respuestas`,
    );
}
for (const [id, { data }] of lessons) {
  if (!existsSync(join(quizzesDir, `${id}.yaml`))) warn(`lessons/${id}`, 'sin quiz asociado');
  for (const lab of data.relatedLabs ?? []) {
    if (!existsSync(join(CONTENT, 'labs', lab)))
      err(`lessons/${id}`, `lab relacionado inexistente: ${lab}`);
  }
}

// --- Informe -----------------------------------------------------------------
console.log(
  `Módulos: ${moduleIds.size} · Lecciones: ${lessons.size} · Preguntas: ${questionIds.size}`,
);
for (const w of warnings) console.warn(`  aviso  ${w}`);
for (const e of errors) console.error(`  ERROR  ${e}`);
if (errors.length) {
  console.error(`\n${errors.length} error(es) de contenido.`);
  process.exit(1);
}
console.log('Contenido válido.');
