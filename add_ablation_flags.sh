#!/bin/bash

set -e

FILE="config.py"

echo "Creating backup..."
cp "$FILE" "${FILE}.backup_ablation_flags"

python3 - <<'PY'
from pathlib import Path

p = Path("config.py")
text = p.read_text()

if "semantic_routing_enabled" in text:
    print("Ablation flags already exist")
    raise SystemExit

anchor = """    semantic_high_recall_min_ratio: float = 0.75"""

replacement = """    semantic_high_recall_min_ratio: float = 0.75

    # Ablation control switches
    semantic_routing_enabled: bool = True
    semantic_payload_enabled: bool = True"""

if anchor not in text:
    raise RuntimeError(
        "Semantic configuration anchor not found"
    )

text = text.replace(
    anchor,
    replacement,
    1
)

p.write_text(text)

print("Ablation flags added")

PY

python -m py_compile "$FILE"

echo "Verification:"
grep -n "semantic_.*enabled" "$FILE"

echo "DONE"

