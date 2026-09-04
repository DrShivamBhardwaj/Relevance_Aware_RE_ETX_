#!/bin/bash

set -e

FILE="run_semantic_re_etx.py"

echo "Creating backup..."
cp "$FILE" "${FILE}.backup_efficiency_fix"

python3 - <<'PY'
from pathlib import Path

p = Path("run_semantic_re_etx.py")
text = p.read_text()

if "Semantic efficiency" in text:
    print("Semantic efficiency reporting already exists")
    raise SystemExit

marker = "Payload reduction (%)"

idx = text.find(marker)

if idx == -1:
    raise RuntimeError(
        "Payload reduction reporting marker not found"
    )

# Find end of the print statement containing payload reduction
end = text.find("\n\n", idx)

if end == -1:
    raise RuntimeError(
        "Could not locate report block end"
    )

insert = """

        if total_radio_bits > 0:
            semantic_efficiency = (
                total_semantic_payload_bits
                /
                total_radio_bits
            )

            print(
                f"Semantic efficiency          : "
                f"{semantic_efficiency:.6f}"
            )
"""

text = text[:end] + insert + text[end:]

p.write_text(text)

print("Semantic efficiency reporting inserted")

PY

python -m py_compile "$FILE"

echo "Verification:"
grep -n "Semantic efficiency" "$FILE"

echo "DONE"
