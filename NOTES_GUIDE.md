# How the course notes get built

Internal process doc. Not in `_toc.yml`, so it is never rendered or shipped to
students. The inventory it refers to lives in `_ledger.yml`.

---

## What the notes are

The notes are the course textbook, authored once as chapters inside this
Jupyter Book and exported to PDF via LaTeX at the end of the semester. There is
no second HTML site and no separate manuscript. A chapter is a *module*, not a
class meeting — a module's sessions are `##` sections inside it.

They are **not** a transcript of the slides. A deck is a prompt for a chapter,
never its content. The four editorial principles hold everywhere:

1. **Transportation intuition is the on-ramp.** Each AI concept enters as a
   generalization of something the reader already knows. Binary logit → sigmoid.
   Multinomial logit → softmax. Macroscopic state reduction → VAE latent space.
   Controller arbitration → attention. Never open a section with a math-first
   definition.
2. **Borrow the math, own the translation.** Do not re-derive backpropagation or
   the ELBO. Cite Bishop and the papers in `literature/`. The originality is the
   mobility framing, the worked examples, and the judgment.
3. **Every chapter answers the practitioner's questions.** What data does this
   need, do agencies have it, is it worth it against the classical baseline, how
   do you evaluate a vendor claim, what does deployment and maintenance cost,
   and when should you not use this at all.
4. **Keep the skeptical engineering voice.** Beat a tuned baseline. Does it
   replicate. Does it deploy.

Two rules with no exceptions:

- **No invented numbers.** Every figure in a chapter is either verified in code
  first, or cited to a source, or absent. If a companion page deliberately
  refuses to show illustrative performance numbers, the chapter does too.
- **Student-facing voice.** These pages are read by students. Never write
  instructor-directed phrasing ("questions for your students", "have them run").

---

## Chapter skeleton

```markdown
# Module N — <title>

*Sessions: <dates>. <One line on what the module is for.>*

:::{admonition} How to read this chapter
:class: tip
<what to read before class, what the labs prove, what is assessed>
:::

## N.0 The problem                      <- the mobility problem, before any AI
## N.1 <Session 1 topic>
   ### transportation intuition bridge
   ### the concept as a generalization  <- math referenced out, not re-derived
   ### where it breaks
   :::{admonition} Before you trust this result
   <the three questions — see below>
   :::
## N.2 <Session 2 topic>
   ...
## Labs                                  <- what each lab proves, not how to run it
## Using this on the job                 <- agency practice, procurement, vendor claims
## Critical reading                      <- papers + what to interrogate in each
## Exercises
## Where this goes next
```

### The standing evaluation close

Every section that produces a result ends with the same three questions:

> **What is the baseline?** · **How was the data split, and why is that honest?**
> · **What does it do on the ugly cases?**

This is deliberate repetition. SLO #3 (evaluation) has no room in the ~130
minutes of real teaching time per content week, so the notes are where it gets
taught. Use the `{admonition}` block, not prose, so it is visually the same
object every time.

---

## Embedding a companion

Interactive HTML companions are *not* rewritten into MyST. They are copied
verbatim into `_static/companions/` and iframed:

```html
<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion — Short Title</span>
    <a href="../_static/companions/File_Name.html" target="_blank" rel="noopener">
      Open full screen ↗</a>
  </div>
  <iframe src="../_static/companions/File_Name.html"
          title="Short Title" loading="lazy"></iframe>
</div>
```

- Path is `../_static/...` from a `moduleN/` page.
- `.companion-embed` styling lives at the end of `_static/custom.css`.
- Always give the full-screen link — the companions assume ~1040 px of width and
  are cramped inside the book's content column.
- Mount by copying on the device, not by staging through the container:
  `cp <file>.html ai4mobility.github.io/_static/companions/`.
- Check the file size first. Anything over ~500 KB (e.g.
  `VAE_to_Diffusion_Lab.html` at 2 MB) needs a decision about repo weight before
  it goes in.

Notebooks need none of this — Jupyter Book renders `.ipynb` natively. Reference
them with `{doc}` and describe *what the lab proves*, not how to run it.

---

## The weekly pass

Target: one chapter section per teaching week, running one week behind lecture.
Roughly 30–45 minutes of instructor time.

1. **Drop.** After class, put the deck and anything else new into `inbox/`
   at the top of the class folder. Any format — `.pptx`, `.pdf`, `.md`.
2. **Sweep.** The session lists `inbox/`, diffs it against `_ledger.yml`, and
   adds a row for anything new with `status: raw`.
3. **Draft.** The deck becomes chapter prose by *expansion* — every bullet
   becomes at least a paragraph, and the parts that were said out loud in class
   but never made it onto a slide are the parts most worth writing down.
   Status goes `raw → drafted`.
4. **Review.** Instructor reads the diff. Corrections land in the chapter and,
   if they are a general rule rather than a one-off, in project memory.
   Status goes `drafted → integrated`.
5. **Ship.** `jupyter-book build .`, commit, and hand the push back —
   the device workspace has no network, so `git push` always happens on the
   instructor's own machine. Status goes `integrated → published`.

### When a week runs short

Ten labs for Modules 4–8 are unbuilt and lab-building outranks note-writing.
When a week has no time, the chapter section gets a **stub**: the session's
topic line, the lab link, the three evaluation questions, and nothing else. Then
set that ledger row to `debt`. A stub with a `debt` row is honest; a chapter
that quietly skips a week is not.

---

## Building and shipping

```bash
pip install "jupyter-book<2"      # plain `jupyter-book` resolves to the v2
                                  # mystmd rewrite, which cannot build this repo
jupyter-book build .
```

Expected build noise, all harmless: `toctree contains reference to document ...
that doesn't have a title` from empty notebook stubs, and `image file not
readable` for missing `_static` assets when building a scratch copy. Anything
else is a real problem.

Git from a Cowork session over the Dropbox mount: the mount blocks `unlink`, so
every git command leaves a stale `.git/index.lock` that blocks the next one.
Sweep stale locks into `_to_delete/stale-git-locks/` **before and after** every
git command, as separate sequential calls — never batched alongside the git
command itself.

---

## Where decisions live

- `_ledger.yml` — the inventory. What exists, where it goes, what state it is in.
- This file — the process and the template.
- Project memory — the *why*: framing decisions, rejected alternatives, verified
  numbers, build gotchas. Anything a future session would otherwise re-litigate.
