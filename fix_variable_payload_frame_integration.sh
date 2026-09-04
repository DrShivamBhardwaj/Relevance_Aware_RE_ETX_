#!/bin/bash

set -e

FILE="simulator/multihop_transmission.py"

echo "Creating backup..."
cp "$FILE" "${FILE}.backup_variable_payload"

python3 - <<'PY'
from pathlib import Path

p = Path("simulator/multihop_transmission.py")
text = p.read_text()

old = """            for frame_bits in (
                self.frame_model.fragment_sizes()
            ):
"""

new = """            for frame_bits in (
                self.frame_model.fragment_sizes(app_bits)
            ):
"""

if old not in text:
    raise RuntimeError(
        "Fragmentation call not found"
    )

text = text.replace(
    old,
    new,
    1
)

p.write_text(text)

print("Variable payload fragmentation integrated")

PY

python -m py_compile "$FILE"

echo "Verification:"
grep -n "fragment_sizes" "$FILE"

echo "DONE"

