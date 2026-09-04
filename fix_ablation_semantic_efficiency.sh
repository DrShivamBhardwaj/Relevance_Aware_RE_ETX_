#!/bin/bash

set -e

FILE="run_semantic_re_etx.py"

echo "Creating backup..."
cp "$FILE" "${FILE}.backup_efficiency_fix"

python3 - <<'PY'
from pathlib import Path

p = Path("run_semantic_re_etx.py")
text = p.read_text()

old = """        total_semantic_payload_bits += int(
            np.sum(semantic_payload_bits)
        )"""

new = """        if config.semantic_payload_enabled:
            total_semantic_payload_bits += int(
                np.sum(semantic_payload_bits)
            )
        else:
            total_semantic_payload_bits += int(
                config.num_nodes
                * config.packet_size
            )"""

if old not in text:
    raise RuntimeError(
        "Semantic payload counter block not found"
    )

text = text.replace(
    old,
    new,
    1
)

p.write_text(text)

print("Semantic efficiency accounting fixed")

PY

python -m py_compile "$FILE"

echo "Verification:"
grep -n "total_semantic_payload_bits" "$FILE"

echo "DONE"

