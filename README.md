# AI for Mobility

An open graduate-level course on artificial intelligence applications in transportation.

- **Live site:** https://ai4mobility.github.io
- **Video lectures:** https://www.youtube.com/@hao6247
- **License:** Course content under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); build infrastructure under MIT. See `LICENSE.md`.

## What this is

This repository hosts the source for the *AI for Mobility* course site, built with [Jupyter Book](https://jupyterbook.org/). The site rebuilds and publishes automatically whenever changes are pushed to `main`.

## Course outline

- **Module 1** — Foundations of AI for Mobility
- **Module 2** — AI Sensing for Traffic Monitoring
- **Module 3** — AI for Driving Automation and Connectivity
- **Module 4** — AI Traffic Simulation and Digital Twin

## First-time deployment

1. Clone your existing `ai4mobility/ai4mobility.github.io` repository locally (it currently has only a default README).
2. Copy every file and folder from this `ai4mobility-site/` directory into the cloned repo root, **including** the hidden `.github/` and `.gitignore`.
3. On GitHub, go to **Settings → Pages**. Under "Build and deployment," change the **Source** from "Deploy from a branch" to **"GitHub Actions"**. (This step is essential — without it the workflow will run but Pages won't pick up the output.)
4. Commit and push to `main`. The included workflow (`.github/workflows/deploy.yml`) will build the book and publish it.

After the first successful run (you can watch it under the **Actions** tab on GitHub), the site will be live at https://ai4mobility.github.io.

### Exact commands

```bash
# In a working directory of your choice
git clone https://github.com/ai4mobility/ai4mobility.github.io.git
cd ai4mobility.github.io

# Copy the scaffold contents in (adjust the source path for your machine)
cp -R "/path/to/ai4mobility-site/." .

git add .
git commit -m "Initial JupyterBook scaffold"
git push origin main
```

## Editing locally (optional but recommended for big changes)

```bash
# One-time setup
pip install -r requirements.txt

# Build the book
jupyter-book build .

# Open _build/html/index.html in your browser
```

## How to add content

### A new notes section page

Modules are organized by **section**, not by lecture — `moduleN/notesK-slug.md`,
one file per section, listed directly under the module index. There is no
intermediate "Notes" page. See `NOTES_GUIDE.md` for the page template.

1. Create the file in the module folder, e.g. `module2/notes1-attention.md`.
2. Add it to `_toc.yml` under that module's `sections` list:

   ```yaml
   - file: module2/index
     sections:
       - file: module2/notes1-attention
         title: "2.1 Attention, from a lane-change decision"
   ```

3. Add its row to the page-by-page map table on `module2/index.md`.
4. Add a row to `_ledger.yml`, then commit and push — the site rebuilds automatically.

### A new lab notebook

1. Drop the `.ipynb` file into a module folder (e.g. `module2/lab1.ipynb`).
2. Add it to `_toc.yml` under the **Labs** part, nested beneath `labs`, with an
   explicit `title:` in the `Lab N — Short Name` form. Lab notebooks are listed
   there rather than under their module, so every lab in the course has one home.
3. Add it to `labs.md` in two places: the at-a-glance table (change its status
   from *In development* to *Available*) and a card in the "Available Now" grid.
4. Add a short row to the module's own `## Labs` table so the module page still
   names it.
5. Notebooks get an automatic "Open in Colab" rocket button thanks to the
   `launch_buttons` config in `_config.yml`.

### Embedding a YouTube lecture

The simplest approach is a plain markdown link:

```markdown
[Watch Lecture 2.1 on YouTube](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)
```

If you'd like inline embedded players, install `sphinxcontrib-youtube` (`pip install sphinxcontrib-youtube`), add it to `requirements.txt`, register it as a Sphinx extension in `_config.yml`, then use:

````markdown
```{youtube} YOUR_VIDEO_ID
```
````

## Repository layout

```
.
├── _config.yml             # JupyterBook configuration
├── _toc.yml                # Table of contents
├── intro.md                # Home page
├── prerequisites.md
├── syllabus.md
├── course-intro.md         # Week 1 — course introduction
├── labs.md                 # All Labs — course-wide lab directory
├── resources.md
├── hardware.md
├── module1/
│   ├── index.md            # Module 1 overview + page-by-page map
│   ├── notes1-networks.md  # 1.1 … one file per section, no "Notes" wrapper
│   ├── notes2-learning.md  # 1.2
│   ├── notes3-cnn.md       # 1.3
│   ├── notes4-cnn-in-practice.md   # 1.4
│   ├── notes5-embeddings.md        # 1.5
│   ├── notes6-labs.md      # Practice, exercises, further reading
│   └── lab1.ipynb …        # four lab notebooks, listed under the Labs part
├── module2/ … module8/     # index.md each; module7 also has notes.md
├── capstone/index.md
├── _ledger.yml             # content inventory — one row per artifact
├── NOTES_GUIDE.md          # how to write a notes section page
├── _static/
│   ├── custom.css          # USF brand color overrides
│   └── companions/         # interactive companion pages
├── requirements.txt
├── .github/workflows/deploy.yml
├── .gitignore
├── LICENSE.md
└── README.md (this file)
```

## Contact

Hao Zhou — haozhou1@usf.edu  
University of South Florida, Department of Civil & Environmental Engineering
