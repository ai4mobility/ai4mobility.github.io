# Module 9 — Optional: How Models and Agents Are Trained

*Part II, AI Agents for Mobility · optional reading, with two labs. Not a lecture.*

## What this module is for

Modules 5&ndash;8 teach how to use powerful models and build agents for your work: less *why*, more *how*. This
optional module is the *why*. It is for anyone who wants to know what happens inside the model an agent runs on,
and above all for PhD students who plan to train or fine-tune a model, or to publish on agents. Nothing in Modules
5&ndash;8 depends on it.

## Overview

The module has four parts, each built around one milestone paper and the transportation papers that already use
its method.

**1. How a model learns to reason.** In this course a model *reasons* when it writes intermediate steps before its
final answer, checks and revises them, and those steps measurably raise its accuracy. Chain-of-thought prompting asks
a model for those steps; reasoning models such as OpenAI's o1 and DeepSeek-R1 are trained to write them on their own,
with reinforcement learning on problems whose answers can be checked. The milestone paper is DeepSeek-R1, and the
training method behind it, GRPO, is explained through an analogy you know: reinforcement learning for traffic signal
control. A clear chain of steps is still not proof that the answer is right. Transportation examples include
Traffic-R1 (signal control) and AlphaDrive (driving decisions).

**2. How a model learns to use tools.** The models you call today were trained to write tool calls in a fixed format.
The milestone paper is Search-R1, which trains a model with reinforcement learning to decide when to search. No
transportation paper yet trains a tool-using agent end to end this way, which makes it an opening for research.

**3. Fine-tuning and LoRA.** Changing the model itself. Full fine-tuning updates every weight. **LoRA** freezes the
original weights and learns a small low-rank change on top of them, which is why it fits on a single GPU.
{doc}`Section 9.1 <notes1-adaptation>` is the decision rule for when any of this is worth it. The short version:
fix the harness first, because it is cheaper; fine-tune when the same mistake keeps coming back, or when agency data
cannot leave the building and a small local model is the only option. Labs 6 and 9 put the rule to work.

**4. Checks.** Can a model check its own work? Mostly not on its own, but it can when a tool does the checking. This
part goes deeper into the evidence behind the checks taught in {doc}`Module 5 <../module5/index>`.

**A crash course in reinforcement learning** comes with the module, for anyone new to RL: signal control at one
intersection on a cellular-automaton model, with a policy trained on the queues of all incoming legs. It covers the
main ideas, the Bellman equation, value and policy iteration, Q-learning, REINFORCE, and PPO, the base of the method
DeepSeek-R1 uses.

**This module's transportation question.** Transportation has unusually good graders: simulators, exact procedures
such as the HCM, conservation of vehicles, and decades of recorded outcomes. Where do they give better rewards and
training data than generic ones, and when is a simulator too poorly calibrated to trust as a judge?

## The module, page by page

<div class="practice-table-wrap">
<table class="practice-table notes-map">
<thead>
<tr><th style="width:32%">Page</th><th style="width:50%">What it covers</th><th style="width:18%">Labs</th></tr>
</thead>
<tbody>
<tr>
  <td><a href="notes1-adaptation.html"><strong>9.1 The adaptation ladder: what your corpus actually needs</strong></a><br><em>Fine-tuning and LoRA</em></td>
  <td>Three different things called fine-tuning; the ladder rung by rung, with what each changes and costs; why retrieval beats a fine-tune for most agency documents; whether your corpus is big enough, and allowed; what &ldquo;it worked&rdquo; has to mean.</td>
  <td><a href="lab6_vit_finetune.html">Lab 6</a>, <a href="lab9_lora_crash_narratives.html">Lab 9</a></td>
</tr>
<tr>
  <td><strong>Handouts</strong><br><em>All four parts</em></td>
  <td>&ldquo;How a model learns to reason,&rdquo; &ldquo;How a model learns to use tools,&rdquo; &ldquo;LoRA and fine-tuning&rdquo; and &ldquo;Checks,&rdquo; plus the RL crash course.</td>
  <td>&mdash;</td>
</tr>
</tbody>
</table>
</div>

## Learning objectives

By the end of this module you will be able to:

- Explain what it means for a model to reason, tell chain-of-thought prompting from a reasoning model, and say why a
  written chain of steps is not proof that the answer is right.
- Describe how reinforcement learning trains a reasoning model, and what makes a problem's reward checkable.
- Explain how a model is trained to call tools, and where a transportation simulator could supply the reward.
- Explain full fine-tuning, LoRA and instruction tuning, and estimate what each costs in trainable parameters and data.
- Decide whether a failure calls for a change to the harness or for fine-tuning, and justify it.

## Topics

- Reasoning: chain-of-thought prompting vs. reasoning models; DeepSeek-R1 and GRPO
- Reinforcement learning, from signal control to language models
- Training tool use: Search-R1, and what a transportation version would need
- The adaptation ladder: prompting, retrieval, fine-tuning (section 9.1)
- Full fine-tuning vs. LoRA; instruction tuning
- Can a model check itself? Self-correction with and without tools

## Recommended readings

- Wei, J., et al. (2022). Chain-of-thought prompting elicits reasoning in large language models. *NeurIPS*.
- DeepSeek-AI (2025). [DeepSeek-R1: Incentivizing reasoning capability in LLMs via reinforcement learning](https://arxiv.org/abs/2501.12948). *arXiv:2501.12948*.
- Shao, Z., et al. (2024). DeepSeekMath: Pushing the limits of mathematical reasoning in open language models. *arXiv:2402.03300*. *(Introduces GRPO.)*
- Jin, B., et al. (2025). Search-R1: Training LLMs to reason and leverage search engines with reinforcement learning. *arXiv:2503.09516*.
- Hu, E. J., et al. (2022). LoRA: Low-rank adaptation of large language models. *ICLR*.
- Ouyang, L., et al. (2022). Training language models to follow instructions with human feedback. *NeurIPS*. *(InstructGPT.)*
- Gururangan, S., et al. (2020). Don't stop pretraining: Adapt language models to domains and tasks. *ACL*.
- Huang, J., et al. (2024). Large language models cannot self-correct reasoning yet. *ICLR*.
- Gou, Z., et al. (2024). CRITIC: Large language models can self-correct with tool-interactive critiquing. *ICLR*.
- Sutton, R. S., & Barto, A. G. (2018). *Reinforcement learning: An introduction* (2nd ed.). MIT Press.

## Labs

- **{doc}`Lab 6 — Fine-tuning a Vision Transformer <lab6_vit_finetune>`** *(available)*. Turn the
  transfer dial on 2,949 real FL511 traffic-camera frames: head only, last block, last four
  blocks, everything. Measure what each setting costs and buys, then find out why the
  after-dark score is higher than it should be. The labels came from a detector, and the last
  third of the lab is about what that costs. Reads with sections 2.7 and 9.1.

- **{doc}`Lab 9 — Fine-tuning a Small Language Model on Crash Narratives <lab9_lora_crash_narratives>`** *(available)*.
  Turn 399 crash narratives into six coded fields with a 0.5B open model, four ways: prompt only,
  fixed examples, retrieved examples, and a LoRA adapter, all scored on 2.13's corridor folds against
  a TF-IDF baseline. Then find out which fields the text never contained. Reads with sections 2.13 and 9.1.
