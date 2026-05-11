# Prerequisites

## Background you'll need

This is a graduate-level course, but it's designed to be accessible to motivated self-learners. You'll do best if you arrive with:

**Required**

- **Programming.** Comfortable with Python at the level of writing functions, using NumPy/Pandas, and reading other people's code. If you've completed a Python intro course or a few projects, you're set.
- **Math.** Linear algebra (vectors, matrices, dot products) and basic probability (random variables, expectation, distributions). You don't need to be fluent — just willing to brush up as topics come up.
- **Transportation background** *(or willingness to read up)*. Basic familiarity with traffic flow concepts (speed, density, flow). Module 4 leans on this most.

**Helpful but not required**

- Prior exposure to machine learning (a Coursera ML course or similar)
- Familiarity with Jupyter notebooks
- Some experience with PyTorch or TensorFlow

If you're rusty on any of these, the {doc}`resources` page lists short refreshers.

## Tools you'll need

You can run all of the labs in **Google Colab** (free, runs in your browser) with one click from any lab page. No local setup required.

If you'd prefer to run things locally:

```bash
# Create a fresh conda environment
conda create -n aimobility python=3.11
conda activate aimobility

# Core dependencies
pip install numpy pandas matplotlib scikit-learn jupyter

# Deep learning (Module 2+)
pip install torch torchvision

# Computer vision (Module 2)
pip install opencv-python ultralytics

# Traffic simulation (Module 4)
pip install eclipse-sumo  # or install SUMO separately from sumo.dlr.de
```

## Recommended primers

Before Module 1, consider warming up with one of:

- **Python**: [Python Data Science Handbook](https://jakevdp.github.io/PythonDataScienceHandbook/) by Jake VanderPlas (free online)
- **Machine learning**: Andrew Ng's [Machine Learning Specialization](https://www.coursera.org/specializations/machine-learning-introduction) on Coursera (the first course is enough)
- **Traffic flow**: May, *Traffic Flow Fundamentals* — or for free, the [Fundamentals of Transportation](https://en.wikibooks.org/wiki/Fundamentals_of_Transportation) wikibook

You don't need to do all three. Pick whichever is your weakest area.
