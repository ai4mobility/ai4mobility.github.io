# AI Mobility Technologies

An open graduate-level course on artificial intelligence applications in transportation.

- **Live site:** https://ai4mobility.github.io
- **Video lectures:** https://www.youtube.com/@hao6247
- **License:** Course content under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); build infrastructure under MIT. See `LICENSE.md`.

## What this is

This repository hosts the source for the *AI Mobility Technologies* course site, built with [Jupyter Book](https://jupyterbook.org/). The site rebuilds and publishes automatically whenever changes are pushed to `main`.

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

### A new lecture page

1. Create a new markdown file in the appropriate module folder, e.g. `module2/lecture1.md`.
2. Add it to `_toc.yml` under that module's `sections` list:

   ```yaml
   - file: module2/index
     sections:
       - file: module2/lecture1
   ```

3. Commit and push — the site rebuilds automatically.

### A new lab notebook

1. Drop the `.ipynb` file into a module folder (e.g. `module2/lab1.ipynb`).
2. Add it to `_toc.yml` the same way you would a markdown page.
3. Notebooks get an automatic "Open in Colab" rocket button thanks to the `launch_buttons` config in `_config.yml`.

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
├── resources.md
├── module1/
│   ├── index.md            # Module 1 overview
│   ├── lecture1.md         # Sample lecture
│   └── lab1.ipynb          # Python + ML warmup lab
├── module2/index.md
├── module3/index.md
├── module4/index.md
├── _static/
│   └── custom.css          # USF brand color overrides
├── requirements.txt
├── .github/workflows/deploy.yml
├── .gitignore
├── LICENSE.md
└── README.md (this file)
```

## Contact

Hao Zhou — haozhou1@usf.edu  
University of South Florida, Department of Civil & Environmental Engineering
