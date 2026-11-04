#!/bin/sh
# Re-score every finished run and rebuild the notebook. Safe to run while LoRA is still going.
set -e
cd "$(dirname "$0")/../work"
../venv/bin/python make_numbers.py
cp numbers.json ../out/numbers.json
cd ../out && ../venv/bin/python build_lora_crash_lab.py lab9_lora_crash_narratives.ipynb
