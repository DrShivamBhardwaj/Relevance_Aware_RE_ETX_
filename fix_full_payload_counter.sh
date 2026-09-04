#!/bin/bash

set -e

FILE="run_semantic_re_etx.py"

echo "Creating backup..."
cp "$FILE" "${FILE}.backup_full_payload_counter"

python3 - <<'PY'
from pathlib import Path

p = Path("run_semantic_re_etx.py")
text = p.read_text()

old = """            total_radio_bits += int(
                result.radio_bits
            )

            if config.semantic_payload_enabled:
"""

new = """            total_radio_bits += int(
                result.radio_bits
            )

            total_full_payload_bits += int(
                config.packet_size
            )

            if config.semantic_payload_enabled:
"""

if old not in text:
    raise RuntimeError(
        "Radio accounting block not found"
    )

text = text.replace(
    old,
    new,
    1
)

p.write_text(text)

print("Full payload counter added")

PY

python -m py_compile "$FILE"

echo "Verification:"
grep -n "total_full_payload_bits" "$FILE"

echo "DONE"

