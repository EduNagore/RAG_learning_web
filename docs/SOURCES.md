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
