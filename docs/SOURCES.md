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
- **Papers (agentes):** Agentic RAG survey (Singh et al., arXiv 2501.09136) si se usa. El resto (ReAct, Reflexion, MAST, etc.) está verificado en F5.
- **Especificaciones:** JSON Schema. MCP, A2A y OpenTelemetry GenAI están verificadas en F4 y F5.
- **Documentación oficial:** Anthropic (engineering blog: Building effective agents, Contextual Retrieval, multi-agent research system, Agent Skills), OpenAI (Agents SDK, Cookbook), Google ADK, Microsoft (Agent Framework, GraphRAG), LangGraph, LlamaIndex, CrewAI, PydanticAI, smolagents, bases vectoriales, RAGAS, DeepEval, Langfuse, Arize Phoenix, Pyodide.
- **Expertos (N2):** Lilian Weng, Chip Huyen (_AI Engineering_), Simon Willison, Hamel Husain y Shreya Shankar, Eugene Yan, Jason Liu; Cognition ("Don't Build Multi-Agents"); OWASP GenAI Security Project.
- **Benchmarks:** MTEB (pendiente si se cita). SWE-bench, GAIA, τ-bench, τ²-bench, WebArena, OSWorld, BFCL y Terminal-Bench están verificados en F5.

## Cómo añadir una fuente

1. Ábrela y comprueba título, autores y año (o la afirmación que vas a citar).
2. Añádela al frontmatter de la lección (`sources`) con `type`, `authors` y `year`.
3. Regístrala en la tabla de arriba con la fecha de verificación.

## Verificadas en F4 (M01–M09)

Fuentes de las lecciones de RAG. Se abrió cada una al redactar la lección y se comprobaron título, autores, año y las afirmaciones concretas que se citan (cifras de los resúmenes y de la documentación). Las cifras de documentación de proveedores son volátiles y figuran en bloques `<Snapshot>` con fecha.

| Fuente | Nivel | Tipo | Año | Usada en | Verificada |
| ------ | ----- | ---- | --- | -------- | ---------- |
| [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) (Lewis et al.) | N1 | paper | 2020 | M01 L1, M01 L3 | 2026-10 |
| [REALM: Retrieval-Augmented Language Model Pre-Training](https://arxiv.org/abs/2002.08909) (Guu et al.) | N1 | paper | 2020 | M01 L1 | 2026-10 |
| [Improving language models by retrieving from trillions of tokens](https://arxiv.org/abs/2112.04426) (Borgeaud et al.) | N1 | paper | 2021 | M01 L1 | 2026-10 |
| [Atlas: Few-shot Learning with Retrieval Augmented Language Models](https://arxiv.org/abs/2208.03299) (Izacard et al.) | N1 | paper | 2022 | M01 L1 | 2026-10 |
| [Retrieval-Augmented Generation for Large Language Models: A Survey](https://arxiv.org/abs/2312.10997) (Gao et al.) | N1 | paper | 2023 | M01 L1, M01 L3, M02 L1, M05 L1, M05 L4, M06 L1, M08 L1, M09 L1 | 2026-10 |
| [Fine-Tuning or Retrieval? Comparing Knowledge Injection in LLMs](https://arxiv.org/abs/2312.05934) (Ovadia et al.) | N1 | paper | 2023 | M01 L2 | 2026-10 |
| [Retrieval Augmented Generation or Long-Context LLMs? A Comprehensive Study and Hybrid Approach](https://arxiv.org/abs/2407.16833) (Li et al.) | N1 | paper | 2024 | M01 L2, M06 L2 | 2026-10 |
| [Agentic Retrieval-Augmented Generation: A Survey on Agentic RAG](https://arxiv.org/abs/2501.09136) (Singh et al.) | N1 | paper | 2025 | M01 L3, M07 L3 | 2026-10 |
| [Docling Technical Report](https://arxiv.org/abs/2408.09869) (Auer et al. (IBM Research)) | N1 | paper | 2024 | M02 L1 | 2026-10 |
| [Dense X Retrieval: What Retrieval Granularity Should We Use?](https://arxiv.org/abs/2312.06648) (Chen et al.) | N1 | paper | 2023 | M02 L2 | 2026-10 |
| [Is Semantic Chunking Worth the Computational Cost?](https://arxiv.org/abs/2410.13070) (Qu, Tu, Bao) | N1 | paper | 2024 | M02 L2 | 2026-10 |
| [Reconstructing Context: Evaluating Advanced Chunking Strategies for Retrieval-Augmented Generation](https://arxiv.org/abs/2504.19754) (Merola, Singh) | N1 | paper | 2025 | M02 L2, M02 L3 | 2026-10 |
| [Introducing Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval) (Anthropic) | N2 | blog | 2024 | M02 L3, M05 L4 | 2026-10 |
| [Late Chunking: Contextual Chunk Embeddings Using Long-Context Embedding Models](https://arxiv.org/abs/2409.04701) (Günther et al.) | N1 | paper | 2024 | M02 L3 | 2026-10 |
| [Dense Passage Retrieval for Open-Domain Question Answering](https://arxiv.org/abs/2004.04906) (Karpukhin et al.) | N1 | paper | 2020 | M03 L1, M03 L3 | 2026-10 |
| [BEIR: A Heterogenous Benchmark for Zero-shot Evaluation of Information Retrieval Models](https://arxiv.org/abs/2104.08663) (Thakur et al.) | N1 | paper | 2021 | M03 L1, M05 L1, M08 L1, M08 L3 | 2026-10 |
| [SPLADE: Sparse Lexical and Expansion Model for First Stage Ranking](https://arxiv.org/abs/2107.05720) (Formal, Piwowarski, Clinchant) | N1 | paper | 2021 | M03 L1 | 2026-10 |
| [MTEB: Massive Text Embedding Benchmark](https://arxiv.org/abs/2210.07316) (Muennighoff et al.) | N1 | paper | 2022 | M03 L1, M03 L2, M08 L1, M08 L3 | 2026-10 |
| [Matryoshka Representation Learning](https://arxiv.org/abs/2205.13147) (Kusupati et al.) | N1 | paper | 2022 | M03 L2 | 2026-10 |
| [Binary and Scalar Embedding Quantization for Significantly Faster & Cheaper Retrieval](https://huggingface.co/blog/embedding-quantization) (Shakir, Aarsen, Lee (Hugging Face)) | N2 | blog | 2024 | M03 L2 | 2026-10 |
| [Vector embeddings (documentación de OpenAI)](https://developers.openai.com/api/docs/guides/embeddings) (OpenAI) | N1 | docs | 2026 | M03 L2, M04 L2 | 2026-10 |
| [M3-Embedding: Multi-Linguality, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation](https://arxiv.org/abs/2402.03216) (Chen et al.) | N1 | paper | 2024 | M03 L3 | 2026-10 |
| [Learning Transferable Visual Models From Natural Language Supervision](https://arxiv.org/abs/2103.00020) (Radford et al. (OpenAI)) | N1 | paper | 2021 | M03 L3 | 2026-10 |
| [ColPali: Efficient Document Retrieval with Vision Language Models](https://arxiv.org/abs/2407.01449) (Faysse et al.) | N1 | paper | 2024 | M03 L3, M07 L4 | 2026-10 |
| [Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs](https://arxiv.org/abs/1603.09320) (Malkov, Yashunin) | N1 | paper | 2016 | M04 L1 | 2026-10 |
| [The Faiss library](https://arxiv.org/abs/2401.08281) (Douze et al.) | N1 | paper | 2024 | M04 L1 | 2026-10 |
| [ANN-Benchmarks: A Benchmarking Tool for Approximate Nearest Neighbor Algorithms](https://arxiv.org/abs/1807.05614) (Aumüller, Bernhardsson, Faithfull) | N1 | paper | 2018 | M04 L1 | 2026-10 |
| [DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node](https://papers.nips.cc/paper/2019/hash/09853c7fb1d3f8ee67a61b6bf4a7f8e6-Abstract.html) (Subramanya et al.) | N1 | paper | 2019 | M04 L1 | 2026-10 |
| [ACORN: Performant and Predicate-Agnostic Search Over Vector Embeddings and Structured Data](https://arxiv.org/abs/2403.04871) (Patel, Kraft, Guestrin, Zaharia) | N1 | paper | 2024 | M04 L2 | 2026-10 |
| [pgvector (repositorio y documentación)](https://github.com/pgvector/pgvector) (pgvector) | N1 | docs | 2026 | M04 L2, M04 L3 | 2026-10 |
| [Qdrant, visión general de la documentación](https://qdrant.tech/documentation/overview/) (Qdrant) | N1 | docs | 2026 | M04 L2, M04 L3 | 2026-10 |
| [Milvus, visión general de la documentación](https://milvus.io/docs/overview.md) (Milvus) | N1 | docs | 2026 | M04 L3 | 2026-10 |
| [Weaviate, visión general de la documentación](https://docs.weaviate.io/weaviate) (Weaviate) | N1 | docs | 2026 | M04 L3 | 2026-10 |
| [Pinecone, vista general de la indexación](https://docs.pinecone.io/guides/index-data/indexing-overview) (Pinecone) | N1 | docs | 2026 | M04 L3 | 2026-10 |
| [Chroma, introducción](https://docs.trychroma.com/docs/overview/introduction) (Chroma) | N1 | docs | 2026 | M04 L3 | 2026-10 |
| [LanceDB, documentación](https://docs.lancedb.com/) (LanceDB) | N1 | docs | 2026 | M04 L3 | 2026-10 |
| [Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf) (Cormack, Clarke, Büttcher) | N1 | paper | 2009 | M05 L1 | 2026-10 |
| [Passage Re-ranking with BERT](https://arxiv.org/abs/1901.04085) (Nogueira, Cho) | N1 | paper | 2019 | M05 L2 | 2026-10 |
| [ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT](https://arxiv.org/abs/2004.12832) (Khattab, Zaharia) | N1 | paper | 2020 | M05 L2 | 2026-10 |
| [ColBERTv2: Effective and Efficient Retrieval via Lightweight Late Interaction](https://arxiv.org/abs/2112.01488) (Santhanam, Khattab, Saad-Falcon, Potts, Zaharia) | N1 | paper | 2021 | M05 L2 | 2026-10 |
| [Is ChatGPT Good at Search? Investigating Large Language Models as Re-Ranking Agents](https://arxiv.org/abs/2304.09542) (Sun et al.) | N1 | paper | 2023 | M05 L2 | 2026-10 |
| [Precise Zero-Shot Dense Retrieval without Relevance Labels (HyDE)](https://arxiv.org/abs/2212.10496) (Gao, Ma, Lin, Callan) | N1 | paper | 2022 | M05 L3 | 2026-10 |
| [Query Rewriting for Retrieval-Augmented Large Language Models](https://arxiv.org/abs/2305.14283) (Ma, Gong, He, Zhao, Duan) | N1 | paper | 2023 | M05 L3, M07 L4 | 2026-10 |
| [Take a Step Back, Evoking Reasoning via Abstraction in Large Language Models](https://arxiv.org/abs/2310.06117) (Zheng et al.) | N1 | paper | 2023 | M05 L3 | 2026-10 |
| [RAG-Fusion: a New Take on Retrieval-Augmented Generation](https://arxiv.org/abs/2402.03367) (Rackauckas) | N1 | paper | 2024 | M05 L3 | 2026-10 |
| [RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval](https://arxiv.org/abs/2401.18059) (Sarthi, Abdullah, Tuli, Khanna, Goldie, Manning) | N1 | paper | 2024 | M05 L4, M07 L1 | 2026-10 |
| [Enabling Large Language Models to Generate Text with Citations](https://arxiv.org/abs/2305.14627) (Gao, Yen, Yu, Chen) | N1 | paper | 2023 | M06 L1, M06 L3, M08 L2 | 2026-10 |
| [Citations (documentación de la API de Claude)](https://platform.claude.com/docs/en/build-with-claude/citations) (Anthropic) | N1 | docs | 2026 | M06 L1 | 2026-10 |
| [LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models](https://arxiv.org/abs/2310.05736) (Jiang, Wu, Lin, Yang, Qiu) | N1 | paper | 2023 | M06 L2 | 2026-10 |
| [Know Your Limits: A Survey of Abstention in Large Language Models](https://arxiv.org/abs/2407.18418) (Wen, Yao, Feng, Xu, Tsvetkov, Howe, Wang) | N1 | paper | 2024 | M06 L3 | 2026-10 |
| [Reduce hallucinations (documentación de Claude)](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations) (Anthropic) | N1 | docs | 2026 | M06 L3, M09 L2 | 2026-10 |
| [From Local to Global: A Graph RAG Approach to Query-Focused Summarization](https://arxiv.org/abs/2404.16130) (Edge et al.) | N1 | paper | 2024 | M07 L1 | 2026-10 |
| [LightRAG: Simple and Fast Retrieval-Augmented Generation](https://arxiv.org/abs/2410.05779) (Guo, Xia, Yu, Ao, Huang) | N1 | paper | 2024 | M07 L1 | 2026-10 |
| [Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection](https://arxiv.org/abs/2310.11511) (Asai, Wu, Wang, Sil, Hajishirzi) | N1 | paper | 2023 | M07 L2 | 2026-10 |
| [Corrective Retrieval Augmented Generation](https://arxiv.org/abs/2401.15884) (Yan, Gu, Zhu, Ling) | N1 | paper | 2024 | M07 L2 | 2026-10 |
| [Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models through Question Complexity](https://arxiv.org/abs/2403.14403) (Jeong, Baek, Cho, Hwang, Park) | N1 | paper | 2024 | M07 L2, M07 L3 | 2026-10 |
| [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) (Yao, Zhao, Yu, Du, Shafran, Narasimhan, Cao) | N1 | paper | 2022 | M07 L3 | 2026-10 |
| [Next-Generation Database Interfaces: A Survey of LLM-based Text-to-SQL](https://arxiv.org/abs/2406.08426) (Hong et al.) | N1 | paper | 2024 | M07 L4 | 2026-10 |
| [Ragas: Automated Evaluation of Retrieval Augmented Generation](https://arxiv.org/abs/2309.15217) (Es, James, Espinosa-Anke, Schockaert) | N1 | paper | 2023 | M08 L2 | 2026-10 |
| [ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems](https://arxiv.org/abs/2311.09476) (Saad-Falcon, Khattab, Potts, Zaharia) | N1 | paper | 2023 | M08 L2, M08 L3 | 2026-10 |
| [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685) (Zheng et al.) | N1 | paper | 2023 | M08 L2 | 2026-10 |
| [MultiHop-RAG: Benchmarking Retrieval-Augmented Generation for Multi-Hop Queries](https://arxiv.org/abs/2401.15391) (Tang, Yang) | N1 | paper | 2024 | M08 L3 | 2026-10 |
| [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/) (OWASP GenAI Security Project) | N1 | docs | 2025 | M09 L1, M09 L2, M09 L3 | 2026-10 |
| [Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection](https://arxiv.org/abs/2302.12173) (Greshake, Abdelnabi, Mishra, Endres, Holz, Fritz) | N1 | paper | 2023 | M09 L2 | 2026-10 |
| [OpenTelemetry Semantic Conventions for Generative AI (repositorio)](https://github.com/open-telemetry/semantic-conventions-genai) (OpenTelemetry) | N1 | docs | 2026 | M09 L3 | 2026-10 |
| [Langfuse, documentación](https://langfuse.com/docs) (Langfuse) | N1 | docs | 2026 | M09 L3 | 2026-10 |
| [Arize Phoenix, documentación](https://arize.com/docs/phoenix) (Arize AI) | N1 | docs | 2026 | M09 L3 | 2026-10 |
| [LangSmith, documentación](https://docs.langchain.com/langsmith/home) (LangChain) | N1 | docs | 2026 | M09 L3 | 2026-10 |

## Verificadas en F5 (M10–M17)

Fuentes de las lecciones de agentes. Se abrió cada una al redactar la lección (título, autores, año y las cifras o afirmaciones citadas). Las cifras de benchmarks son las de los artículos originales y se señalan como tales; los datos volátiles (versiones de protocolos y frameworks, ediciones de OWASP, estado de las convenciones de OpenTelemetry) van en bloques `<Snapshot>` con fecha. Dos fuentes secundarias se usan con cautela y así consta en las lecciones: la nota de la Cloud Security Alliance para el ranking OWASP LLM Top 10 2026 (la lista no estaba en la página de OWASP) y, para el Top 10 agéntico, la página oficial confirma fecha (9-12-2025), participación de más de cien expertos y códigos ASI01–ASI10, pero remite a la descarga para los nombres; las categorías que M17 L2 menciona proceden de resúmenes de terceros y se citan como orientación, con la advertencia de consultar el documento.

| Fuente | Nivel | Tipo | Año | Usada en | Verificada |
| ------ | ----- | ---- | --- | -------- | ---------- |
| [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (Schluntz, Zhang (Anthropic)) | N2 | blog | 2024 | M10 L1, M10 L2, M10 L4, M11 L1, M11 L2, M11 L3, M12 L1, M13 L3, M14 L2, M14 L3, M17 L2, M17 L3 | 2026-10 |
| [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) (Yao, Zhao, Yu, Du, Shafran, Narasimhan, Cao) | N1 | paper | 2022 | M10 L1, M10 L2, M10 L3, M11 L3 | 2026-10 |
| [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (Rajasekaran, Dixon, Ryan, Hadfield (Anthropic)) | N2 | blog | 2025 | M10 L1, M10 L2, M10 L4, M11 L2, M15 L2, M15 L3 | 2026-10 |
| [Tool use with Claude (documentación)](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) (Anthropic) | N1 | docs | 2026 | M10 L2 | 2026-10 |
| [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366) (Shinn, Cassano, Berman, Gopinath, Narasimhan, Yao) | N1 | paper | 2023 | M10 L3 | 2026-10 |
| [Large Language Models Cannot Self-Correct Reasoning Yet](https://arxiv.org/abs/2310.01798) (Huang, Chen, Mishra, Zheng, Yu, Song, Zhou) | N1 | paper | 2023 | M10 L3, M11 L2 | 2026-10 |
| [Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903) (Wei et al.) | N1 | paper | 2022 | M10 L3, M11 L1 | 2026-10 |
| [Lost in the Middle, How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172) (Liu, Lin, Hewitt, Paranjape, Bevilacqua, Petroni, Liang) | N1 | paper | 2023 | M10 L4, M15 L3 | 2026-10 |
| [Self-Consistency Improves Chain of Thought Reasoning in Language Models](https://arxiv.org/abs/2203.11171) (Wang, Wei, Schuurmans, Le, Chi, Narang, Chowdhery, Zhou) | N1 | paper | 2022 | M11 L1 | 2026-10 |
| [Self-Refine: Iterative Refinement with Self-Feedback](https://arxiv.org/abs/2303.17651) (Madaan et al.) | N1 | paper | 2023 | M11 L2 | 2026-10 |
| [ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models](https://arxiv.org/abs/2305.18323) (Xu, Peng, Lei, Mukherjee, Liu, Xu) | N1 | paper | 2023 | M11 L3 | 2026-10 |
| [An LLM Compiler for Parallel Function Calling](https://arxiv.org/abs/2312.04511) (Kim, Moon, Tabrizi, Lee, Mahoney, Keutzer, Gholami) | N1 | paper | 2023 | M11 L3 | 2026-10 |
| [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) (Anthropic) | N2 | blog | 2025 | M12 L1, M12 L2, M12 L4, M15 L1, M15 L3, M17 L3 | 2026-10 |
| [Don't Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents) (Walden Yan (Cognition)) | N2 | blog | 2025 | M12 L1, M12 L2, M12 L4, M15 L3 | 2026-10 |
| [Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657) (Cemri et al.) | N1 | paper | 2025 | M12 L1, M12 L4 | 2026-10 |
| [AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation](https://arxiv.org/abs/2308.08155) (Wu, Bansal, Zhang et al.) | N1 | paper | 2023 | M12 L2 | 2026-10 |
| [Handoffs (OpenAI Agents SDK)](https://openai.github.io/openai-agents-python/handoffs/) (OpenAI) | N1 | docs | 2026 | M12 L2 | 2026-10 |
| [Improving Factuality and Reasoning in Language Models through Multiagent Debate](https://arxiv.org/abs/2305.14325) (Du, Li, Torralba, Tenenbaum, Mordatch) | N1 | paper | 2023 | M12 L3 | 2026-10 |
| [CAMEL: Communicative Agents for Mind Exploration of Large Language Model Society](https://arxiv.org/abs/2303.17760) (Li, Hammoud, Itani, Khizbullin, Ghanem) | N1 | paper | 2023 | M12 L3 | 2026-10 |
| [MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework](https://arxiv.org/abs/2308.00352) (Hong et al.) | N1 | paper | 2023 | M12 L3 | 2026-10 |
| [Communicative Agents for Software Development (ChatDev)](https://arxiv.org/abs/2307.07924) (Qian et al.) | N1 | paper | 2023 | M12 L3 | 2026-10 |
| [Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442) (Park, O'Brien, Cai, Morris, Liang, Bernstein) | N1 | paper | 2023 | M12 L3, M15 L2 | 2026-10 |
| [Model Context Protocol, Specification](https://modelcontextprotocol.io/specification/latest) (Model Context Protocol) | N1 | docs | 2026 | M13 L1, M13 L2, M13 L3 | 2026-10 |
| [Model Context Protocol, Tools](https://modelcontextprotocol.io/specification/latest/server/tools) (Model Context Protocol) | N1 | docs | 2026 | M13 L1, M15 L1 | 2026-10 |
| [Model Context Protocol, Transports](https://modelcontextprotocol.io/specification/latest/basic/transports) (Model Context Protocol) | N1 | docs | 2026 | M13 L1 | 2026-10 |
| [Model Context Protocol, Authorization](https://modelcontextprotocol.io/specification/latest/basic/authorization) (Model Context Protocol) | N1 | docs | 2026 | M13 L1 | 2026-10 |
| [Agent2Agent (A2A) Protocol, Specification](https://a2a-protocol.org/latest/specification/) (A2A Protocol) | N1 | docs | 2026 | M13 L2, M13 L3 | 2026-10 |
| [Agent Skills (documentación de Claude)](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) (Anthropic) | N1 | docs | 2026 | M13 L2, M13 L3 | 2026-10 |
| [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) (LangChain) | N1 | docs | 2026 | M14 L1, M14 L2 | 2026-10 |
| [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) (OpenAI) | N1 | docs | 2026 | M14 L1 | 2026-10 |
| [Agent SDK overview (Claude)](https://code.claude.com/docs/en/agent-sdk/overview) (Anthropic) | N1 | docs | 2026 | M14 L1, M14 L3 | 2026-10 |
| [Microsoft Agent Framework overview](https://learn.microsoft.com/en-us/agent-framework/overview/) (Microsoft) | N1 | docs | 2026 | M14 L1, M14 L2, M14 L3, M15 L1 | 2026-10 |
| [CrewAI introduction](https://docs.crewai.com/en/introduction) (CrewAI) | N1 | docs | 2026 | M14 L1 | 2026-10 |
| [Agent Development Kit (ADK)](https://adk.dev/) (Google) | N1 | docs | 2026 | M14 L1 | 2026-10 |
| [LlamaIndex Workflows](https://developers.llamaindex.ai/python/workflows/) (LlamaIndex) | N1 | docs | 2026 | M14 L1 | 2026-10 |
| [Pydantic AI overview](https://pydantic.dev/docs/ai/overview/) (Pydantic) | N1 | docs | 2026 | M14 L1 | 2026-10 |
| [smolagents](https://huggingface.co/docs/smolagents/index) (Hugging Face) | N1 | docs | 2026 | M14 L1, M14 L3 | 2026-10 |
| [LangGraph, persistencia (hilos, checkpoints y stores)](https://docs.langchain.com/oss/python/langgraph/persistence) (LangChain) | N1 | docs | 2026 | M15 L1, M15 L2 | 2026-10 |
| [LangGraph, interrupciones](https://docs.langchain.com/oss/python/langgraph/interrupts) (LangChain) | N1 | docs | 2026 | M15 L1 | 2026-10 |
| [MemGPT: Towards LLMs as Operating Systems](https://arxiv.org/abs/2310.08560) (Packer, Wooders, Lin, Fang, Patil, Stoica, Gonzalez) | N1 | paper | 2023 | M15 L2 | 2026-10 |
| [Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory](https://arxiv.org/abs/2504.19413) (Chhikara, Khant, Aryan, Singh, Yadav) | N1 | paper | 2025 | M15 L2 | 2026-10 |
| [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) (Anthropic) | N2 | blog | 2026 | M16 L1, M16 L2, M16 L3 | 2026-10 |
| [τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains](https://arxiv.org/abs/2406.12045) (Yao, Shinn, Razavi, Narasimhan) | N1 | paper | 2024 | M16 L1, M16 L2, M16 L3 | 2026-10 |
| [The Berkeley Function Calling Leaderboard (BFCL): From Tool Use to Agentic Evaluation of Large Language Models](https://gorilla.cs.berkeley.edu/leaderboard.html) (Patil et al. (UC Berkeley)) | N1 | docs | 2025 | M16 L1, M16 L3 | 2026-10 |
| [Evaluating Large Language Models Trained on Code](https://arxiv.org/abs/2107.03374) (Chen et al. (OpenAI)) | N1 | paper | 2021 | M16 L2 | 2026-10 |
| [τ²-Bench: Evaluating Conversational Agents in a Dual-Control Environment](https://arxiv.org/abs/2506.07982) (Barres, Dong, Ray, Si, Narasimhan) | N1 | paper | 2025 | M16 L2, M16 L3 | 2026-10 |
| [SWE-bench: Can Language Models Resolve Real-World GitHub Issues?](https://arxiv.org/abs/2310.06770) (Jimenez, Yang, Wettig, Yao, Pei, Press, Narasimhan) | N1 | paper | 2023 | M16 L3 | 2026-10 |
| [SWE-bench Verified](https://www.swebench.com/verified.html) (SWE-bench team, in collaboration with OpenAI) | N1 | docs | 2024 | M16 L3 | 2026-10 |
| [GAIA: a benchmark for General AI Assistants](https://arxiv.org/abs/2311.12983) (Mialon, Fourrier, Swift, Wolf, LeCun, Scialom) | N1 | paper | 2023 | M16 L3 | 2026-10 |
| [WebArena: A Realistic Web Environment for Building Autonomous Agents](https://arxiv.org/abs/2307.13854) (Zhou, Xu, Zhu et al.) | N1 | paper | 2023 | M16 L3 | 2026-10 |
| [OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments](https://arxiv.org/abs/2404.07972) (Xie et al.) | N1 | paper | 2024 | M16 L3 | 2026-10 |
| [Terminal-Bench](https://www.tbench.ai/) (Stanford University, Laude Institute) | N1 | docs | 2025 | M16 L3 | 2026-10 |
| [OpenTelemetry GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai) (OpenTelemetry project) | N1 | docs | 2026 | M16 L3, M17 L3 | 2026-10 |
| [Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection](https://arxiv.org/abs/2302.12173) (Greshake, Abdelnabi, Mishra, Endres, Holz, Fritz) | N1 | paper | 2023 | M17 L1 | 2026-10 |
| [The lethal trifecta for AI agents](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) (Simon Willison) | N2 | blog | 2025 | M17 L1, M17 L2 | 2026-10 |
| [Defeating Prompt Injections by Design](https://arxiv.org/abs/2503.18813) (Debenedetti, Shumailov, Fan, Hayes, Carlini et al.) | N1 | paper | 2025 | M17 L1 | 2026-10 |
| [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/) (OWASP GenAI Security Project) | N1 | docs | 2025 | M17 L1, M17 L2, M17 L3 | 2026-10 |
| [OWASP’s 2026 LLM Top 10: Incident Data Meets Judgment](https://labs.cloudsecurityalliance.org/research/csa-research-note-owasp-llm-top10-2026-incident-weighted-202/) (Cloud Security Alliance) | N2 | blog | 2026 | M17 L1, M17 L3 | 2026-10 |
| [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) (OWASP GenAI Security Project) | N1 | docs | 2025 | M17 L1, M17 L2 | 2026-10 |
| [Beyond permission prompts: making Claude Code more secure and autonomous](https://www.anthropic.com/engineering/claude-code-sandboxing) (Anthropic) | N2 | blog | 2025 | M17 L2 | 2026-10 |


## Verificadas en F6 (M18, proyectos y playground)

Las fuentes de las lecciones de M18 ya constan en las secciones anteriores (guía de agentes de Anthropic, Contextual Retrieval, evaluación de agentes, Lost in the Middle y MAST). Para los proyectos y el playground se abrió la documentación vigente el 2026-10-06 y se comprobaron las versiones en PyPI.

| Fuente | Nivel | Tipo | Usada en | Qué se comprobó |
| ------ | ----- | ---- | -------- | --------------- |
| [PyPI JSON API](https://pypi.org/) (qdrant-client 1.19.1, docling 2.134.0, ragas 0.4.3, langfuse 4.17.0, langgraph 1.2.13, mcp 2.3.0, sentence-transformers 6.1.0, anthropic 1.11.0, python-dotenv 1.2.4) | N1 | registro | `projects/*/pyproject.toml` | Versiones vigentes y `requires-python` (2026-10-06) |
| [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) | N1 | docs | Proyecto 4 | v2: `from mcp.server import MCPServer`, `@mcp.tool()`, `from mcp import Client`, `call_tool`, `structured_content`; arranque con `uv run mcp dev` |
| [Qdrant quickstart](https://qdrant.tech/documentation/quickstart/) | N1 | docs | Proyecto 1 | `QdrantClient`, `create_collection(vectors_config=VectorParams)`, `upsert` con `PointStruct`, `query_points` |
| [LangGraph quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart) | N1 | docs | Proyecto 2 | `StateGraph`, `add_node`, `add_edge`, `add_conditional_edges`, `START`/`END`, `compile`, `invoke` |
| [Docling](https://github.com/docling-project/docling) | N1 | docs | Proyecto 1 | `DocumentConverter().convert(...)` y `result.document.export_to_markdown()`; Python ≥ 3.10 |
| [Claude API overview](https://platform.claude.com/docs/en/api/overview) | N1 | docs | Playground | Endpoint `POST /v1/messages`, cabeceras `x-api-key`, `anthropic-version: 2023-06-01`, `content-type` |
| [anthropic-sdk-typescript](https://github.com/anthropics/anthropic-sdk-typescript) | N1 | docs | Playground | Uso en navegador desactivado por defecto; `dangerouslyAllowBrowser` y aviso sobre credenciales |
| [Claude's API now supports CORS requests](https://simonwillison.net/2024/Aug/23/anthropic-dangerous-direct-browser-access) (Willison) | N2 | blog | Playground | Cabecera `anthropic-dangerous-direct-browser-access: true` (fuente secundaria de 2024; el playground gestiona el fallo de CORS con un mensaje) |


## Verificadas en F8 (sincronización del progreso con Supabase)

Documentación abierta el 2026-10-07. Se usa solo lo que dicen estas páginas.

| Fuente | Nivel | Tipo | Qué se comprobó |
| ------ | ----- | ---- | --------------- |
| [Supabase JS: signInWithOtp](https://supabase.com/docs/reference/javascript/auth-signinwithotp) | N1 | docs | `signInWithOtp({ email, options: { emailRedirectTo } })`; la URL de redirección debe estar en la lista de permitidas; enlace o código según la plantilla; puede crear la cuenta |
| [Supabase JS: initializing](https://supabase.com/docs/reference/javascript/initializing) | N1 | docs | `createClient(url, key, options)` y las opciones de auth `persistSession`, `autoRefreshToken`, `detectSessionInUrl`, `storage`. `storageKey` y `flowType` no figuraban en esa página: se usan por el tipado de `@supabase/supabase-js` 2.117 (`astro check` los acepta) |
| [Supabase JS: onAuthStateChange](https://supabase.com/docs/reference/javascript/auth-onauthstatechange) | N1 | docs | Eventos `INITIAL_SESSION`, `SIGNED_IN`, `SIGNED_OUT`, `TOKEN_REFRESHED`; `data.subscription.unsubscribe()`. La página no avisa de no llamar a Supabase dentro del callback; se aplaza a otro turno por prudencia |
| [Supabase: Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security) | N1 | docs | Sintaxis de las cuatro políticas con `to authenticated` y `(select auth.uid()) = user_id`; sin políticas no hay acceso con la clave pública; una tabla expuesta sin RLS es legible y escribible |
| [Supabase: email passwordless / magic links](https://supabase.com/docs/guides/auth/auth-email-passwordless) | N1 | docs | Un enlace por usuario cada 60 s, caducidad de 1 hora, redirecciones permitidas, y el aviso de que los escáneres de correo pueden consumir los enlaces |
| [Supabase: redirect URLs](https://supabase.com/docs/guides/auth/redirect-urls) | N1 | docs | Site URL y lista de redirecciones; comodines `*` y `**` |
| [Supabase: pricing](https://supabase.com/pricing) | N1 | docs | Plan gratuito: 500 MB, 50 000 usuarios activos al mes, 5 GB de salida, 2 proyectos activos y pausa tras 1 semana de inactividad |
| [Supabase: gestión de datos de usuario](https://supabase.com/docs/guides/auth/managing-user-data) | N1 | docs | La documentación solo menciona `auth.admin.deleteUser()` (servidor); no documenta el borrado de la propia cuenta desde el cliente. Por eso la web solo borra la fila de progreso y lo explica |
| `@supabase/supabase-js` 2.117.2 | N1 | registro | Versión vigente en npm (2026-10-07) |
