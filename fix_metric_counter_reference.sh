#!/bin/bash

set -e

FILE="run_semantic_re_etx.py"

echo "Creating backup..."
cp "$FILE" "${FILE}.backup_counter_reference"

python3 - <<'PY'
from pathlib import Path

p = Path("run_semantic_re_etx.py")
text = p.read_text()

old = """        total_full_payload_bits = (
            generated_messages
            *
            config.packet_size
        )

        if total_full_payload_bits > 0:
"""

new = """        if total_full_payload_bits > 0:
"""

if old not in text:
    raise RuntimeError(
        "Invalid generated_messages block not found"
    )

text = text.replace(old, new, 1)

p.write_text(text)

print("Metric counter reference corrected")

PY

python -m py_compile "$FILE"

echo "Verification:"
grep -n "generated_messages\|total_full_payload_bits" "$FILE"

echo "DONE"

