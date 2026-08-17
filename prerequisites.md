# Prerequisites

## Background you'll need

There are **no formal prerequisites** for CGN 6933, and no prior AI or machine learning
coursework is required. The course does not assume everyone arrives with the same
background, but it does assume you'll be proactive about filling gaps. You'll do best with:

**Recommended**

- **Programming.** Comfortable with Python at the level of writing functions, using
  NumPy/Pandas, and reading other people's code. If you've completed a Python intro course or
  a few projects, you're set. Advanced programming experience is not required — and the
  course spends real time on AI-assisted coding, which helps here.
- **Math.** Linear algebra (vectors, matrices, dot products) and basic probability (random
  variables, expectation, distributions). You don't need fluency — just a willingness to
  brush up as topics come up.
- **Transportation context** *(or willingness to read up)*. Basic familiarity with traffic
  flow concepts (speed, density, flow). The traffic simulation, digital twin, and safety
  analysis material leans on this most. Students coming from computer science or electrical
  engineering do fine — the transportation framing is introduced as we go.

**Helpful but not required**

- Prior exposure to machine learning (a Coursera ML course or similar)
- Familiarity with Jupyter notebooks
- Some experience with PyTorch
- Having used an LLM chat tool or coding assistant seriously for something

If you're rusty on any of these, the {doc}`resources` page lists short refreshers.

## Tools you'll need

You can run the labs in **Google Colab** (free, runs in your browser) with one click from any
lab page. No local setup required, and Colab's free GPU is enough for the course labs.

Bring a laptop to class — many sessions are hands-on.

If you'd prefer to run things locally:

```bash
# Create a fresh conda environment
conda create -n aimobility python=3.11
conda activate aimobility

# Core dependencies
pip install numpy pandas matplotlib scikit-learn jupyter

# Deep learning
pip install torch torchvision

# Transformers, embeddings, generative models
pip install transformers datasets accelerate diffusers sentence-transformers

# Computer vision
pip install opencv-python ultralytics

# Traffic simulation
pip install eclipse-sumo  # or install SUMO separately from sumo.dlr.de
```

**API access.** A few labs call hosted language or vision-language models. Free tiers are
sufficient; instructions and any course-provided keys are posted on Canvas. You will never be
required to pay out of pocket for a graded assignment.

**Hardware.** Sessions using AI edge devices, the comma 3x self-driving development device,
NVIDIA Jetson, and M5Stack robots use instructor-provided equipment under supervision. You do
not need to buy anything, and no student is required to supply a vehicle.

## Recommended primers

Before the first few weeks, consider warming up with one of:

- **Python**: [Python Data Science Handbook](https://jakevdp.github.io/PythonDataScienceHandbook/) by Jake VanderPlas (free online)
- **Machine learning**: Andrew Ng's [Machine Learning Specialization](https://www.coursera.org/specializations/machine-learning-introduction) on Coursera (the first course is enough)
- **Traffic flow**: May, *Traffic Flow Fundamentals* — or for free, the [Fundamentals of Transportation](https://en.wikibooks.org/wiki/Fundamentals_of_Transportation) wikibook

You don't need to do all three. Pick whichever is your weakest area.
