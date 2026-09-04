#!/bin/bash

set -e

FILE="run_semantic_re_etx.py"

echo "Creating backup..."
cp "$FILE" "${FILE}.backup_double_count"

python3 - <<'PY'
from pathlib import Path

p = Path("run_semantic_re_etx.py")
text = p.read_text()

old = """        if config.semantic_payload_enabled:
            total_semantic_payload_bits += int(
                np.sum(semantic_payload_bits)
            )
        else:
            total_semantic_payload_bits += 0

"""

if old not in text:
    raise RuntimeError(
        "Round-level semantic counter block not found"
    )

text = text.replace(
    old,
    "",
    1
)

p.write_text(text)

print("Removed semantic payload double counting")

PY

python -m py_compile "$FILE"

echo "Verification:"
grep -n "total_semantic_payload_bits" "$FILE"

echo "DONE"

