/**
 * En las lecciones, las referencias a los documentos del corpus de ejemplo (`doc-001`...) se pueden
 * pulsar para leer el documento sin salir de la lección. El texto de la lección no cambia: cada
 * referencia que existe se envuelve en un botón con el mismo texto. Las inventadas a propósito en
 * los ejemplos (`doc-099`) se dejan tal cual. Si el corpus no se puede descargar, la página queda intacta.
 */
import { hasDocRef, splitDocRefs } from '../lib/docrefs';
import { url } from '../lib/url';

interface Doc {
  id: string;
  title: string;
  department: string;
  kind: string;
  updated: string;
  access: string;
  text: string;
}

const KINDS: Record<string, string> = {
  policy: 'Política',
  faq: 'Preguntas frecuentes',
  manual: 'Manual',
  incident: 'Incidencia',
};
const ACCESS: Record<string, string> = {
  public: 'Público',
  internal: 'Interno',
  restricted: 'Restringido',
};
/** Dónde NO se tocan los textos: enlaces, botones, componentes interactivos, diagramas y código editable. */
const SKIP =
  'a, button, astro-island, svg, script, style, textarea, dialog, .mermaid-diagram, .cm-editor';

let dialog: HTMLDialogElement | null = null;

function ensureDialog(): HTMLDialogElement {
  if (dialog) return dialog;
  dialog = document.createElement('dialog');
  dialog.className = 'doc-dialog';
  dialog.setAttribute('aria-labelledby', 'doc-dialog-title');
  dialog.addEventListener('click', (e) => {
    if (e.target === dialog) dialog?.close(); // clic en el fondo
  });
  document.body.append(dialog);
  return dialog;
}

function openDoc(doc: Doc): void {
  const d = ensureDialog();
  d.replaceChildren();

  const title = document.createElement('h2');
  title.id = 'doc-dialog-title';
  title.textContent = doc.title;

  const meta = document.createElement('p');
  meta.className = 'doc-dialog-meta';
  meta.textContent = `${doc.id} · ${doc.department} · ${KINDS[doc.kind] ?? doc.kind} · actualizado ${doc.updated} · acceso: ${ACCESS[doc.access] ?? doc.access}`;

  const body = document.createElement('div');
  for (const paragraph of doc.text.split(/\n{2,}/)) {
    const p = document.createElement('p');
    p.textContent = paragraph;
    body.append(p);
  }

  const note = document.createElement('p');
  note.className = 'doc-dialog-meta';
  note.textContent = 'Documento ficticio del corpus de ejemplo de Nimbus Logística.';

  const links = document.createElement('p');
  links.className = 'doc-dialog-links';
  const full = document.createElement('a');
  full.href = url(`/corpus/${doc.id}/`);
  full.textContent = 'Ver la ficha completa';
  const all = document.createElement('a');
  all.href = url('/corpus/');
  all.textContent = 'Todos los documentos de ejemplo';
  links.append(full, ' · ', all);

  const close = document.createElement('button');
  close.type = 'button';
  close.className = 'doc-dialog-close';
  close.textContent = 'Cerrar';
  close.addEventListener('click', () => d.close());

  d.append(title, meta, body, note, links, close);
  d.showModal();
}

function textNodes(root: Element): Text[] {
  const nodes: Text[] = [];
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    const text = n as Text;
    if (hasDocRef(text.data) && !text.parentElement?.closest(SKIP)) nodes.push(text);
  }
  return nodes;
}

async function init(): Promise<void> {
  const root =
    document.querySelector('article[data-pagefind-body] .prose') ??
    document.querySelector('article[data-pagefind-body]');
  if (!root || !hasDocRef(root.textContent ?? '')) return; // sin referencias: ni se descarga el corpus

  let docs: Doc[];
  try {
    const response = await fetch(url('data/nimbus/corpus.json'));
    if (!response.ok) return;
    docs = (await response.json()) as Doc[];
  } catch {
    return;
  }
  const byId = new Map(docs.map((d) => [d.id, d]));
  const known = new Set(byId.keys());

  for (const node of textNodes(root)) {
    const pieces = splitDocRefs(node.data, known);
    if (!pieces.some((p) => p.docId)) continue;
    const fragment = document.createDocumentFragment();
    for (const piece of pieces) {
      if (!piece.docId) {
        fragment.append(piece.text);
        continue;
      }
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'doc-ref';
      button.dataset.doc = piece.docId;
      button.title = `Leer el documento: ${byId.get(piece.docId)?.title ?? piece.docId}`;
      button.textContent = piece.text;
      fragment.append(button);
    }
    node.replaceWith(fragment);
  }

  root.addEventListener('click', (e) => {
    const button = (e.target as Element).closest<HTMLButtonElement>('button.doc-ref');
    const doc = button?.dataset.doc ? byId.get(button.dataset.doc) : undefined;
    if (doc) openDoc(doc);
  });
}

void init();
