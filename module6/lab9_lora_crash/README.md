# AI4Mobility — Lab 9 instructor tooling: Fine-tuning a small language model on crash narratives (Module 6)

These files are instructor tooling, copied into `module6/lab9_lora_crash/` because this site repo does not keep the other labs' reproducers (those live in the class folder, for example `Labs/vit_finetune/`). They were not rewired for this layout.

- The notebook students open is `module6/lab9_lora_crash_narratives.ipynb`, one directory up. Its content was not regenerated here.
- `refresh.sh` still assumes the original working layout: it `cd`s to `../work`, runs `make_numbers.py` with `../venv`, and writes the notebook from `../out`. Do not run it from this folder.
- `build_lora_crash_lab.py` reads `numbers.json` beside itself (or `LAB9_NUMBERS`) and writes the notebook path you pass it.
- `lora_crash/*.py` read `crash_narratives_joined.json` from the working directory. That file is **not** in this repo. The dataset is distributed through Canvas only. Do not add it, and do not add per-report prediction files.

The notes below are the build record from the machine that produced `numbers.json`. Paths in that record (`out/`, `work/`) are the original layout.

## Files
| path | what |
|---|---|
| `lab9_lora_crash_narratives.ipynb` | The notebook (44 cells, 19 code; no saved outputs). Goes to `module6/` |
| `build_lora_crash_lab.py` + `_cells_code.py` | The builder. Every number in the prose is read from `numbers.json`, and a missing key fails loudly. A method that has not run shows **TODO-after-run** instead of a number |
| `numbers.json` | Aggregate results from the build run. No narrative text (checked: 0 of 399 narratives share any 8-word window with it or with the notebook) |
| `refresh.sh` | Re-scores the finished runs, copies numbers.json here and rebuilds the notebook |
| `lora_crash/` | The reproducer scripts (common, llm_core, run_baseline, run_llm, run_lora, run_lora_variant, make_numbers). The per-report prediction files are deliberately not included |
| `labs_card.md` | Draft labs.md changes: hero count, at-a-glance row, card, removing the "coming later" card |
| `toc_entry.md` | Suggested `_toc.yml` entry and module6/index.md edits |

## Data handling (instructor decision: Canvas only)
The data is distributed **only through Canvas**; there is no public URL, and `DATA_URL` stays empty. The setup markdown and cell 2 both tell students to download `crash_narratives_joined.json` from Canvas, then either upload it at the Colab file picker or set `DATA_PATH`. The notebook contains no narrative text, and its outputs are aggregate. The one cell that shows a single narrative (cell 19) is off by default (`SHOW = False`) and tells students to clear its output before they share the notebook.

## What was run (build machine: CPU only, 8 threads, bfloat16; no GPU)
Software: torch 2.15.0+cpu, transformers 5.22.1, peft 0.21.2, scikit-learn 1.9.1. Model: Qwen/Qwen2.5-0.5B-Instruct with greedy decoding and max 80 new tokens. Evaluation uses the same 5 corridor-grouped folds as 2.13 (sizes 79/82/80/79/79). Scores are F1 for yes/no fields and macro-F1 for crash_type and vehicles. An invalid or missing value counts as wrong.

| method | crash_type | pedestrian | vehicles | injury | hit_and_run | distracted | mean | all fields valid | CPU time |
|---|---|---|---|---|---|---|---|---|---|
| majority class | 0.19 | 0 | 0.30 | 0.721 | 0 | 0 | | | |
| **TF-IDF + LR (baseline)** | 0.578 | 0.882 | 0.886 | 0.707 | 0.688 | 0.590 | 0.722 | | 63 s all folds/fields |
| TF-IDF + LR, random split | 0.722 | 0.899 | 0.823 | 0.701 | 0.623 | 0.562 | | | |
| zero-shot | 0.191 | 0 | 0.072 | 0.623 | 0.049 | 0.154 | 0.181 | 70.9% | 2.57 s/report, 17.1 min |
| fixed 3 examples | 0.370 | 0.262 | 0.585 | 0.721 | 0.053 | 0.042 | 0.339 | 99% | 2.29 s, 15.2 min |
| retrieved 3 (train corridors) | 0.492 | 0.667 | 0.686 | 0.697 | 0.327 | 0.528 | 0.566 | 95% | 1.96 s, 13.0 min |
| retrieved 3, leaky (all other reports) | 0.550 | 0.743 | 0.636 | 0.737 | 0.304 | 0.583 | 0.592 | 94% | 9.14 s, 60.8 min* |
| **LoRA r16, 5 folds** | 0.413 | 0.182 | 0.805 | 0.706 | 0.051 | 0.043 | **0.367** | 96.7% (JSON 99.5%) | train 313.6 min total; answer 5.56 s, 37.0 min |

\* Wall-clock on a shared box. Leaky retrieval uses prompts the same length as retrieved-3, so its slower time reflects contention, not the method.

**LoRA per fold** (config: r16, alpha 32, q/k/v/o, lr 1e-4, fp32 adapter, 2 epochs, grad-accum 4, non-finite steps skipped):

| fold | n | crash | ped | veh | inj | hr | distr | mean | final loss | train min | answer min | skipped steps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 79 | 0.203 | 0 | 0.303 | 0.624 | 0 | 0 | 0.188 | 0.064 | 20.9 | 8.8 | 2 |
| 1 | 82 | 0.482 | 0.154 | 0.829 | 0.714 | 0 | 0.174 | 0.392 | 0.041 | 12.8 | 6.4 | 0 |
| 2 | 80 | 0.398 | 0 | 0.867 | 0.769 | 0.5 | 0 | 0.422 | 0.051 | 27.3 | 6.1 | 1 |
| 3 | 79 | 0.382 | 0.211 | 0.881 | 0.747 | 0 | 0 | 0.370 | 0.051 | 159.0 | 12.8 | 0 |
| 4 | 79 | 0.545 | 0.667 | 0.864 | 0.680 | 0 | 0 | 0.459 | 0.040 | 93.5 | 2.9 | 4 |

The per-fold training time ranged from 12.8 to 159 minutes for identical work, which reflects contention on the shared box. Read the short folds as the better guide.

**Verdict as written in the notebook (section 10):** No, not at these settings.
- LoRA averages 0.367. Retrieval from training corridors averages 0.566, and TF-IDF + LR averages 0.722.
- LoRA trails TF-IDF on every field. Injury is a tie: 0.706 vs 0.707.
- LoRA beats retrieval on vehicles (0.805 vs 0.686) and injury (0.706 vs 0.697), and its crash_type accuracy is higher (73.2% vs 67.2%). Its crash_type macro-F1 is lower (0.413 vs 0.492) because it rarely predicts pedestrian_bicycle and never predicts other.
- LoRA collapsed to "no" on the rare binary fields. Across 399 reports it said "yes" 8 times for pedestrian (true count 36), 2 times for hit_and_run (true 37) and 3 times for distracted (true 89).
- Fold 0 collapsed to the majority-class level, even though its training loss looked as healthy as the other folds'. The notebook uses this as the "the loss lied" lesson: format tokens dominate the average loss.
- Leaky retrieval adds +0.026 to the mean, and the effect is mixed by field: crash +0.058, ped +0.076, inj +0.040 and distr +0.055, but veh −0.050 and hr −0.023.

Other numbers in the notebook (all from numbers.json):
- **Availability audit:** how often the coded value is written in the narrative at all. Rain 12.5%, dark 5.0%, wet surface 18.5%, alcohol 77.8% (only 9 cases), hit-and-run 62.2%, pedestrian 97.2%.
- **Hit-and-run recall:** split by whether the narrative mentions it.
- **crash_type:** confusion counts.
- **DistilBERT comparison:** its F1 from 2.13 (distracted 0.453, pedestrian 0.914).

Notebook smoke test (re-run after the final rebuild): CPU cells 2–8 (load, schema, scorer, audit, folds, baseline, random split) were executed from the built notebook on the box against the real file, and they reproduced numbers.json. The model cells (9–19) are the same code as the reproducer scripts, but they have not been run as notebook cells. **Nothing has been run on a Colab T4.** Those timings are marked **TODO-after-run** in sections 5, 7 and 8 and on the card.

## Incidents during the run
- The first LoRA attempt (lr 2e-4, bf16 adapter on the CPU) went to NaN at about step 80 of fold 0. It was restarted with lr 1e-4, an fp32 adapter, and non-finite steps skipped (counted in `fold_meta.skipped`). The notebook cell matches. The note is kept in numbers.json under `lora.config.first_attempt_note`.

## Decided by the instructor
- **Data:** Canvas only. No public URL, and `DATA_URL` stays empty.
- **Model:** Qwen2.5-0.5B-Instruct. Trying 1.5B is left as optional exercise 7.

## Open decisions
1. **LoRA recipe follow-up.** Choose one:
   - (a) keep the rare-field collapse as the lesson (current text), or
   - (b) add a recipe chosen on the training corridors only, such as more epochs, a higher lr, or loss weighted toward the value tokens.

   `lora_crash/run_lora_variant.py` is ready for (b). It trains on one fold and checks 40 training reports first. It has not been run.
2. **Fields dropped.** Weather, light and surface are dropped because the narrative rarely states them. Alcohol is dropped because there are only 9 cases.
3. **2.13 mismatch.** The recomputed TF-IDF distracted AP is 0.614; the published 2.13 page says 0.619.
4. **T4 timings.** These are TODO-after-run in sections 5, 7 and 8 and on the card's "~TODO min on a T4" tag.
5. **Lab number.** The draft uses Lab 9, filed under module6/.
