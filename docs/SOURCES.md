# Registro de fuentes

Fuentes usadas en el curso y su estado de verificación. Una fuente figura como **verificada** cuando se abrió la página y se comprobaron título, autores y año (o, en documentación, las afirmaciones concretas que se citan). Las listadas como **pendientes** son las fuentes de referencia del plan (`PLAN.md` §8) que se verificarán al redactar las lecciones que las usen.

Jerarquía (PLAN §8): **N1** primarias (papers, especificaciones, documentación oficial) · **N2** expertos y blogs técnicos de empresas · **N3** no válidas como fuente única.

## Verificadas

| Fuente | Nivel | Tipo | Año | Usada en | Verificada |
| ------ | ----- | ---- | --- | -------- | ---------- |
| [Attention Is All You Need](https://arxiv.org/abs/1706.03762) (Vaswani et al.) | N1 | paper | 2017 | M00 L1, L2, L6 | 2026-10-05 |
| [Neural Machine Translation of Rare Words with Subword Units](https://arxiv.org/abs/1508.07909) (Sennrich, Haddow, Birch) | N1 | paper | 2015 | M00 L1 | 2026-10-05 |
| [The Curious Case of Neural Text Degeneration](https://arxiv.org/abs/1904.09751) (Holtzman et al.) | N1 | paper | 2019 | M00 L2 | 2026-10-05 |
| [Lost in the Middle](https://arxiv.org/abs/2307.03172) (Liu et al.) | N1 | paper | 2023 | M00 L1, L3, L8 | 2026-10-05 |
| [Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903) (Wei et al.) | N1 | paper | 2022 | M00 L3 | 2026-10-05 |
| [Efficient Guided Generation for Large Language Models](https://arxiv.org/abs/2307.09702) (Willard, Louf) | N1 | paper | 2023 | M00 L4 | 2026-10-05 |
| [Toolformer](https://arxiv.org/abs/2302.04761) (Schick et al.) | N1 | paper | 2023 | M00 L5 | 2026-10-05 |
| [Efficient Estimation of Word Representations in Vector Space](https://arxiv.org/abs/1301.3781) (Mikolov et al.) | N1 | paper | 2013 | M00 L6 | 2026-10-05 |
| [Sentence-BERT](https://arxiv.org/abs/1908.10084) (Reimers, Gurevych) | N1 | paper | 2019 | M00 L6 | 2026-10-05 |
| [Survey of Hallucination in Natural Language Generation](https://arxiv.org/abs/2202.03629) (Ji et al.) | N1 | paper | 2022 | M00 L8 | 2026-10-05 (título, autores y año) |
| [Why Language Models Hallucinate](https://arxiv.org/abs/2509.04664) (Kalai, Nachum, Vempala, Zhang) | N1 | paper | 2025 | M00 L8 | 2026-10-05 |
| [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows) (Anthropic) | N1 | docs | 2026 | M00 L1, L7, L8 | 2026-10-05 |
| [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) (Anthropic) | N1 | docs | 2026 | M00 L7 | 2026-10-05 |
| [Tool use with Claude](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) (Anthropic) | N1 | docs | 2026 | M00 L5, L7, L8 | 2026-10-05 |
| [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) (Anthropic) | N1 | docs | 2026 | M00 L4 | 2026-10-05 |
| [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) (Anthropic) | N1 | docs | 2026 | M00 L3 | 2026-10-05 |
| [Messages API reference](https://platform.claude.com/docs/en/api/messages) (Anthropic) | N1 | docs | 2026 | M00 L2 | 2026-10-05 (nota de `temperature`) |
| [Migrating to Claude Sonnet 5.5](https://platform.claude.com/docs/en/models/sonnet-5-5/migration-guide) (Anthropic) | N1 | docs | 2026 | M00 L2 | 2026-10-05 |
| [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs) (OpenAI) | N1 | docs | 2026 | M00 L4 | 2026-10-05 |
| [Function calling](https://developers.openai.com/api/docs/guides/function-calling) (OpenAI) | N1 | docs | 2026 | M00 L5 | 2026-10-05 |
| [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (Rajasekaran, Dixon, Ryan, Hadfield) | N2 | blog | 2025 | M00 L1, L3 | 2026-10-05 |
| [tiktoken](https://github.com/openai/tiktoken) (OpenAI) | N1 | docs | 2026 | M00 L1 (cifras reproducibles) | 2026-10-05 (ejecutado) |

**Nota sobre Ji et al.** Solo se verificaron título, autores y año; la distinción entre alucinación que contradice la fuente y alucinación no verificable se cita como clasificación del estudio y conviene contrastarla con el texto completo en una revisión futura.

## Pendientes de verificar al usarlas

- **Papers (RAG):** RAG (Lewis et al. 2020), REALM, DPR, ColBERT/ColBERTv2, RETRO, HyDE, Self-RAG, CRAG, RAPTOR, GraphRAG (Edge et al. 2024), LightRAG, RAGAS, ARES, BEIR, MTEB, SPLADE, Matryoshka Representation Learning, Late Chunking, ColPali.
- **Papers (agentes):** ReAct, Reflexion, Generative Agents, CAMEL, MetaGPT, ChatDev, AutoGen, multi-agent debate (Du et al.), "Why Do Multi-Agent LLM Systems Fail?" (MAST), Agentic RAG survey (Singh et al., arXiv 2501.09136).
- **Especificaciones:** Model Context Protocol, A2A Protocol, OpenTelemetry GenAI semantic conventions, JSON Schema.
- **Documentación oficial:** Anthropic (engineering blog: Building effective agents, Contextual Retrieval, multi-agent research system, Agent Skills), OpenAI (Agents SDK, Cookbook), Google ADK, Microsoft (Agent Framework, GraphRAG), LangGraph, LlamaIndex, CrewAI, PydanticAI, smolagents, bases vectoriales, RAGAS, DeepEval, Langfuse, Arize Phoenix, Pyodide.
- **Expertos (N2):** Lilian Weng, Chip Huyen (_AI Engineering_), Simon Willison, Hamel Husain y Shreya Shankar, Eugene Yan, Jason Liu; Cognition ("Don't Build Multi-Agents"); OWASP GenAI Security Project.
- **Benchmarks:** MTEB, SWE-bench, GAIA, τ-bench, BFCL, Terminal-Bench.

## Cómo añadir una fuente

1. Ábrela y comprueba título, autores y año (o la afirmación que vas a citar).
2. Añádela al frontmatter de la lección (`sources`) con `type`, `authors` y `year`.
3. Regístrala en la tabla de arriba con la fecha de verificación.
