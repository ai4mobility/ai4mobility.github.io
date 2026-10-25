# Module 6 — Making Agents Better: Evaluation and Fine-Tuning

*Part II, AI Agents for Mobility · lecture 3 of 5. The class schedule is on the {doc}`../syllabus` page.*

## Session topics

- **Making agents better:** evaluating agents; fine-tuning — full fine-tuning, LoRA, instruction tuning,
  training on agent runs; agents that learn from experience

## Overview

You cannot improve what you cannot measure, so this module starts with **evaluation**. An agent's output
is a process, not one number. Check separately that it chose the right tool, filled in the right
arguments, took the steps in a sensible order, and reached the right result. Do it on tasks whose answers
you already know, run each task several times because agents are random, and use a check that does not
rely on the agent's own report of what it did.

Then **fine-tuning**: changing the model itself. Full fine-tuning updates every weight. **LoRA** freezes
the original weights and learns a small low-rank change on top of them, which is why it fits on a single
GPU. Instruction tuning teaches a model to follow requests in a particular format, and the same idea
applied to recorded agent runs teaches it to use tools. {doc}`Section 6.1 <notes1-adaptation>` is the
decision rule for when any of this is worth it. The short version: fix the harness first, because it is
cheaper; fine-tune when the same mistake keeps coming back, or when agency data cannot leave the building
and a small local model is the only option.

A brief look at **reinforcement learning** follows. Transportation has something most fields lack:
simulators that score outcomes, such as delay in SUMO, which can serve as the reward an agent is trained
on. The module ends with **agents that learn from experience** — saving lessons and skills from their own
past runs — and why the quality of the judge that decides what counts as a success limits how far that
can go.

The examples: fine-tuning a small model to turn crash narratives into structured fields (this module's
lab), scoring an agent that drafts post-storm damage reports from dashcam frames against inspectors'
labels, and SimSkill, a published agent that builds up a library of skills from its own SUMO runs.

**This week's transportation question.** Transportation has unusually good graders: simulators, exact
calculations such as HCM procedures, conservation of vehicles, and decades of recorded outcomes. Where do
they give better training data, rewards and judges than generic ones — and when is a simulator too poorly
calibrated to trust as a judge?

## The module, page by page

<div class="practice-table-wrap">
<table class="practice-table notes-map">
<thead>
<tr><th style="width:32%">Page</th><th style="width:50%">What it covers</th><th style="width:18%">Labs</th></tr>
</thead>
<tbody>
<tr>
  <td><a href="notes1-adaptation.html"><strong>6.1 The adaptation ladder: what your corpus actually needs</strong></a><br><em>Making agents better</em></td>
  <td>Three different things called fine-tuning; the ladder rung by rung, with what each changes and costs; why retrieval beats a fine-tune for most agency documents; whether your corpus is big enough, and allowed; what &ldquo;it worked&rdquo; has to mean.</td>
  <td><a href="lab6_vit_finetune.html">Lab 6</a></td>
</tr>
<tr>
  <td><strong>Further sections</strong><br><em>Making agents better</em></td>
  <td>Evaluating agents, LoRA and instruction tuning, training on agent runs, agents that learn from experience &mdash; written up after the session.</td>
  <td>LoRA lab <em>(in development)</em></td>
</tr>
</tbody>
</table>
</div>

## Learning objectives

By the end of this module you will be able to:

- Build an evaluation set for an agent before building the agent, and check tool choice, arguments,
  order and outcome separately.
- Explain full fine-tuning, LoRA and instruction tuning, and estimate what each costs in trainable
  parameters and data.
- Decide whether a failure calls for a change to the harness or for fine-tuning, and justify it.
- Explain how an agent can improve from its own past runs, and why the quality of the judge limits it.

## Topics

- Evaluating agents: tasks with known answers, repeated runs, checks independent of the agent, cost and steps
- The adaptation ladder: prompting, retrieval, fine-tuning (section 6.1)
- Full fine-tuning vs. LoRA; instruction tuning
- Fine-tuning on recorded agent runs
- Reinforcement learning, briefly: simulators as a source of reward
- Agents that learn from experience: reflection, and skills learned from past runs

## Video lectures

*To be populated.* See the course [YouTube channel](https://www.youtube.com/@hao6247).

## Recommended readings

- Hu, E. J., et al. (2022). LoRA: Low-rank adaptation of large language models. *ICLR*.
- Ouyang, L., et al. (2022). Training language models to follow instructions with human feedback. *NeurIPS*. *(InstructGPT.)*
- Gururangan, S., et al. (2020). Don't stop pretraining: Adapt language models to domains and tasks. *ACL*.
- Shinn, N., et al. (2023). Reflexion: Language agents with verbal reinforcement learning. *NeurIPS*.
- Liu, Q., et al. (2026). [SimSkill: A self-evolving LLM agent for skill and knowledge accumulation in traffic simulation](https://arxiv.org/abs/2609.03753). *arXiv:2609.03753*.
- Fried, D., & Neubig, G. (2026). [CMU 11-768 AI Agents](https://www.cmu-agents.com/), lectures 8–9.

## Labs

- **{doc}`Lab 6 — Fine-tuning a Vision Transformer <lab6_vit_finetune>`** *(available)*. Turn the
  transfer dial on 2,949 real FL511 traffic-camera frames: head only, last block, last four
  blocks, everything. Measure what each setting costs and buys, then find out why the
  after-dark score is higher than it should be. The labels came from a detector, and the last
  third of the lab is about what that costs. Reads with sections 2.7 and 6.1.

- **Fine-tuning a small language model on crash narratives** *(in development)*. Use LoRA to teach a
  small open model to turn crash narratives into structured fields, and compare it with prompting alone
  and with retrieval, on a split you can defend.
