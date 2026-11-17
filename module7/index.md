# Module 7 — What an Agent Reads and Remembers: Context, RAG, and Memory

*Part II, AI Agents for Mobility. The class schedule is on the {doc}`../syllabus` page.*

## Session topics

- **Context engineering:** what the model reads on each call; why the context grows at every step; lost in the
  middle; feed it less; describe traffic with theory, not raw dumps; summaries that drop a rule
- **Retrieval (RAG):** split, embed, search, answer with citations, then check; the milestone paper; splitting a
  manual along its own structure; field words vs. the manual's words; where retrieval breaks; what RAG cannot do;
  from RAG to an agent that reads
- **Memory:** what an agent should remember, who decides, and how it joins the memory an agency already has

## Overview

A language model keeps nothing between calls. Everything it knows about the task in front of it is the text the
harness sends: the instructions, the tool descriptions, the history so far, and whatever the harness fetched. That
text is the **context**. This module is about what goes into it, how to bring in the right part of a long
document, and what an agent should carry from one task to the next.

**Context.** The context grows at every step, and a longer context is not a better one: models use the start and
the end of a long text better than the middle, and accuracy falls as the context grows even when the right fact is
in it. So the harness should send only what a step needs, in plain text, and describe traffic the way traffic flow
theory does (a queue, a bottleneck, a capacity) rather than as a dump of detector records. Summaries save space but
can drop the one rule that mattered; rules belong in the instructions and the harness.

**Retrieval (RAG).** When the knowledge an agent needs is too long to send, keep it outside the model and look up
the part a question needs. RAG splits a document into pieces, turns each into a vector with a BERT-style encoder
you already know, finds the pieces closest to the question, and has the model answer from them with citations.
Transportation work adds two things a generic setup misses. Manuals have their own structure, so split them along
it: a rule cut in half is worse than useless. And manuals use the field's own language, so a field glossary that
rephrases a question into the manual's words can help, if you test it honestly. Just as important is what RAG
cannot do. It helps only when the answer is written down and matches the question. It will not write a good plan
from an SOP, find what the SOP is missing, or answer whole-document questions such as conflicts between agencies or
how a procedure should be improved. Those need an agent that reads in steps, or a person.

**Memory.** Tools look up the present, RAG quotes the manual, and skills carry the procedure; all three were
written before the agent started work. Memory is the only one written by the work itself. The main idea of this
part: **an agency already has a memory** — event logs, work orders, timing files, after-action reports, and its
staff. Designing memory for an agency agent is mostly deciding how the agent plugs into that memory. Agency memory
also differs from chatbot memory: it is about a place and a time (this intersection, this storm) rather than a
person; it serves whoever is on shift; it may go unused for months until the next hurricane season; and it may be a
public record. So the hard parts are keys, approvals, expiry and records, not the database. The agent proposes a
memory; a person promotes it; the system of record always wins over what the agent remembers.

The running example is again FDOT District 7's hurricane signal SOP, with the MUTCD and the Highway Safety Manual
as further documents to split, search and keep current.

**This module's transportation question.** How should a manual be split, searched and asked so retrieval finds
the right clause, and which questions should never be sent to retrieval at all? What should an agency agent
remember about places, events and decisions, and who approves it?

## The module, page by page

<div class="practice-table-wrap">
<table class="practice-table notes-map">
<thead>
<tr><th style="width:32%">Page</th><th style="width:50%">What it covers</th><th style="width:18%">Labs</th></tr>
</thead>
<tbody>
<tr>
  <td><a href="notes1-context.html"><strong>7.1 Context: what the model reads</strong></a><br><em>Context engineering</em></td>
  <td>The context measured and its growth; lost in the middle; five ways to keep context useful; summaries that drop a rule; keeping the loop light (why a longer context lowers accuracy, measured on the SUMO agent).</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes2-rag.html"><strong>7.2 Retrieval (RAG): looking things up in agency documents</strong></a><br><em>Retrieval</em></td>
  <td><strong>Milestone paper: retrieval-augmented generation</strong>; RAG for a safety analyst; where retrieval breaks; <strong>hands-on companion: RAG on the D7 signal SOP</strong> (split, embed, search, check the answer, where it breaks, what RAG cannot do, and from RAG to an agent that reads).</td>
  <td>Companion exercise</td>
</tr>
<tr>
  <td><strong>Further section</strong><br><em>Memory</em></td>
  <td>What memory means for an agent; four kinds of memory and six design decisions; what today's tools and key papers do; agency memory, the three sorting questions and nine rules; two worked examples (two storms, and a study); research openings &mdash; written up after the session.</td>
  <td>&mdash;</td>
</tr>
</tbody>
</table>
</div>

## Learning objectives

By the end of this module you will be able to:

- Decide what belongs in an agent's context window, and explain why an agent's cost grows with every step it takes.
- Build retrieval (RAG) over a transportation document, split along the document's own structure, and check the
  retriever on its own before judging any answer.
- Say which questions RAG can answer and which it cannot, and what to use instead.
- Decide what an agent should remember between tasks, where it is stored, how it is recalled, and who may change it.
- Connect an agent's memory to the records an agency already keeps, and treat that memory as an agency record.

## Topics

- What the model reads on each call, and how it grows
- Lost in the middle; why a longer context lowers accuracy
- Five ways to keep the context useful; summaries that drift
- Retrieval-augmented generation: splitting, embedding, searching, grounding, citing
- A BERT reminder: one vector per sentence, and why plain BERT needs training on question-answer pairs
- Field words vs. the manual's words; a glossary, tested honestly
- Where retrieval breaks: stale indexes, rules cut in two, conflicting rules, missing answers
- What RAG cannot do, and from RAG to an agent that reads in steps
- Memory: working, episodic, semantic and procedural; six decisions (what, when and where to write; how to recall;
  update and forget; who can see it)
- Agency memory: keys by place and time, review dates, promotion by a person, memory as a public record, poisoned
  memory

## Video lectures

*To be populated.* See the course [YouTube channel](https://www.youtube.com/@hao6247).

## Recommended readings

- Lewis, P., et al. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *NeurIPS*.
- Liu, N. F., et al. (2024). Lost in the middle: How language models use long contexts. *Transactions of the ACL*.
- Anthropic (2025). [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).
- Edge, D., et al. (2024). From local to global: A graph RAG approach to query-focused summarization. *arXiv:2404.16130*.
- Packer, C., et al. (2023). MemGPT: Towards LLMs as operating systems. *arXiv:2310.08560*.
- Sumers, T. R., et al. (2024). Cognitive architectures for language agents. *TMLR*. *(CoALA, the vocabulary for the four kinds of memory.)*
- Wen, L., et al. (2024). DiLu: A knowledge-driven approach to autonomous driving with large language models. *ICLR*.
- Fried, D., & Neubig, G. (2026). [CMU 11-768 AI Agents](https://www.cmu-agents.com/), lectures 2&ndash;4.
- Stanford CS 329Z *Engineering AI Agents* (Fall 2026), lecture 7.

## Labs

- **RAG on the signal SOP** *(companion exercise)*. In the companion in {doc}`7.2 <notes2-rag>`, ask Claude the
  same SOP question three ways (no document, three retrieved pieces, the whole SOP) and grade each answer with one
  checklist.

- **For your project.** Decide what your agent should remember, sort each candidate with the three questions
  (can a tool look it up fresh? will it be true next month, and who says so? would it be fine in a public records
  response?), and say how you would test that memory helps. No notebook.
