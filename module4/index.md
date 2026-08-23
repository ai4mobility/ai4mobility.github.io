# Module 4 — Adapting and Orchestrating Models

*Weeks 6 and 7 of the {doc}`../syllabus` — Oct 1 and Oct 8, 2026.*

## Class meetings

| Date | Session topic | Due before class |
|---|---|---|
| Oct 1 | Prompting, retrieval-augmented generation, fine-tuning, model adaptation, and evaluation for transportation tasks | Revised project proposal and initial data/model plan · *rotating project progress reports begin* |
| Oct 8 | Agentic AI, tool use, API calling, AI-assisted coding, and transportation workflow automation | Baseline method or data acquisition plan · *rotating project progress report* |

## Overview

You will almost never train a foundation model. You will adapt one, and then wire it into a
workflow that does something useful.

This module covers both halves. The first is **adaptation**: prompting, retrieval-augmented
generation, fine-tuning, LoRA, instruction tuning, and RLHF — a ladder of increasingly
expensive interventions, where the practical skill is knowing which rung a problem actually
needs. Most transportation problems that people reach for fine-tuning to solve are retrieval
problems.

The second is **orchestration**: agentic AI, where a model calls tools, holds state across
steps, invokes APIs, writes and runs code, and works through a task that no single prompt
could complete. This is where the productivity gains in agency workflows are, and also where
the failure modes get genuinely difficult to see.

## Learning objectives

By the end of this module you will be able to:

- Choose among prompting, RAG, fine-tuning, and LoRA for a given mobility task, and justify
  the choice on cost, data requirements, and maintenance burden.
- Build a retrieval pipeline over transportation documents, and evaluate retrieval quality
  separately from generation quality.
- Construct an evaluation set for a transportation task before you build the system, and state
  in advance what result would count as good enough to deploy.
- Explain instruction tuning and RLHF, and state what alignment does and does not guarantee.
- Design an agentic workflow with explicit tool calls and a human in the loop at the decision
  points that matter.
- Use AI-assisted coding on a real analysis task, and verify the result rather than trusting it.
- Identify the conditions under which an agentic workflow should not be trusted with a
  transportation decision.

## Topics

- Prompt design, context construction, and structured output
- Retrieval-augmented generation: chunking, embedding, retrieval, reranking, grounding
- Evaluating retrieval independently of the generator
- Full fine-tuning vs. parameter-efficient methods; LoRA and adapters
- Instruction tuning; RLHF and preference optimization
- Alignment: what it addresses, and the failure modes it doesn't
- Evaluation for transportation tasks: building a task-specific test set from real agency
  documents and real queries, rather than borrowing a public benchmark
- Metrics that survive scrutiny — exact-match and grounded-citation checks, human review
  protocols, and where LLM-as-judge is and isn't defensible
- Regression testing a prompt or pipeline, so that last month's fix stays fixed
- Agent loops: tool use, memory, skills, planning, and termination
- API calling, token cost, and latency budgets
- AI-assisted coding for engineering and data analysis
- Human-in-the-loop design: where to put the human, and where it's theater
- Evaluating agentic systems when the output is a process, not a number

## Video lectures

*To be populated.* See the course [YouTube channel](https://www.youtube.com/@hao6247).

## Recommended readings

- Lewis, P., et al. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *NeurIPS*.
- Hu, E. J., et al. (2022). LoRA: Low-rank adaptation of large language models. *ICLR*.
- Ouyang, L., et al. (2022). Training language models to follow instructions with human feedback. *NeurIPS*. *(InstructGPT — the RLHF reference.)*
- Wei, J., et al. (2022). Chain-of-thought prompting elicits reasoning in large language models. *NeurIPS*.
- Yao, S., et al. (2023). ReAct: Synergizing reasoning and acting in language models. *ICLR*.
- Schick, T., et al. (2023). Toolformer: Language models can teach themselves to use tools. *NeurIPS*.

## Labs

- **A retrieval assistant over transportation documents.** Build a RAG pipeline over a real
  corpus — a design manual, a set of agency reports, or a standards document — then measure
  retrieval quality on its own before judging the answers. The lesson most people skip: when
  the output is wrong, it is usually retrieval that failed, not the model.

- **An agentic workflow for a recurring task.** Take an analysis you would otherwise do by
  hand every month, decompose it into tool calls, and build an agent that completes it — with
  a verification step you designed, not one the agent reports on itself.
