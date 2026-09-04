#!/bin/bash

set -e

FILE="run_semantic_re_etx.py"

echo "Creating backup..."
cp "$FILE" "${FILE}.backup_semantic_counter"

python3 - <<'PY'
from pathlib import Path

p = Path("run_semantic_re_etx.py")
text = p.read_text()

if "total_semantic_payload_bits +=" in text:
    print("Semantic payload counter already exists")
    raise SystemExit

old = """        payload_bits_history.extend(
            semantic_payload_bits.tolist()
        )"""

new = """        payload_bits_history.extend(
            semantic_payload_bits.tolist()
        )

        total_semantic_payload_bits += int(
            np.sum(semantic_payload_bits)
        )"""

if old not in text:
    raise RuntimeError(
        "Payload history block not found"
    )

text = text.replace(
    old,
    new,
    1
)

p.write_text(text)

print("Semantic payload accumulation inserted")

PY

python -m py_compile "$FILE"

echo "Verification:"
grep -n "total_semantic_payload_bits +=" "$FILE"

echo "DONE"

