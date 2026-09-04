#!/bin/bash

set -e

FILE="run_semantic_re_etx.py"

echo "Creating backup..."
cp "$FILE" "${FILE}.backup_efficiency_counter_fix"

python3 - <<'PY'
from pathlib import Path

p = Path("run_semantic_re_etx.py")
text = p.read_text()

if "total_radio_bits = 0" in text:
    print("Counters already exist")
    raise SystemExit

anchor = "payload_bits_history = []"

if anchor not in text:
    raise RuntimeError(
        "payload_bits_history initialization not found"
    )

replacement = """payload_bits_history = []

    total_semantic_payload_bits = 0
    total_full_payload_bits = 0
    total_radio_bits = 0"""

text = text.replace(
    anchor,
    replacement,
    1
)

p.write_text(text)

print("Semantic efficiency counters inserted")

PY

python -m py_compile "$FILE"

echo "Verification:"
grep -n "total_semantic_payload_bits\|total_full_payload_bits\|total_radio_bits" "$FILE"

echo "DONE"
