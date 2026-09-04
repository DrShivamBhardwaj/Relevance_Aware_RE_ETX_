#!/bin/bash

set -e

FILE="run_semantic_re_etx.py"

echo "Creating backup..."
cp "$FILE" "${FILE}.backup_radio_collection"

python3 - <<'PY'
from pathlib import Path

p = Path("run_semantic_re_etx.py")
text = p.read_text()

if "total_radio_bits += result.radio_bits" in text:
    print("Radio collection already exists")
    raise SystemExit

old = """            round_airtime += (
                result.airtime
            )"""

new = """            round_airtime += (
                result.airtime
            )

            total_radio_bits += int(
                result.radio_bits
            )"""

if old not in text:
    raise RuntimeError(
        "Round airtime block not found"
    )

text = text.replace(
    old,
    new,
    1
)

p.write_text(text)

print("Radio bits collection added")

PY

python -m py_compile "$FILE"

echo "Verification:"
grep -n "total_radio_bits += result.radio_bits" "$FILE"

echo "DONE"

