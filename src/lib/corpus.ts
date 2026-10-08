/** Corpus ficticio de Nimbus Logística (el mismo que usan los laboratorios), tipado para las páginas. */
import corpusJson from '../../public/data/nimbus/corpus.json';
import goldenJson from '../../public/data/nimbus/golden.json';
import { url } from './url';

export interface CorpusDoc {
  id: string;
  title: string;
  department: string;
  kind: 'policy' | 'faq' | 'manual' | 'incident';
  updated: string;
  access: 'public' | 'internal' | 'restricted';
  text: string;
}

export interface GoldenQuestion {
  id: string;
  question: string;
  relevant_ids: string[];
  reference_answer: string;
  answerable: boolean;
  requires_access: 'public' | 'internal' | 'restricted';
}

export const corpus = corpusJson as CorpusDoc[];
export const golden = goldenJson as GoldenQuestion[];

export const KIND_LABELS: Record<CorpusDoc['kind'], string> = {
  policy: 'Política',
  faq: 'Preguntas frecuentes',
  manual: 'Manual',
  incident: 'Incidencia',
};

export const ACCESS_LABELS: Record<CorpusDoc['access'], string> = {
  public: 'Público',
  internal: 'Interno',
  restricted: 'Restringido',
};

export const docHref = (id: string) => url(`/corpus/${id}/`);

/** Preguntas del conjunto dorado cuya evidencia incluye este documento. */
export const questionsForDoc = (id: string): GoldenQuestion[] =>
  golden.filter((q) => q.relevant_ids.includes(id));
