#!/bin/bash

set -e

FILE="run_semantic_re_etx.py"

echo "Creating backup..."
cp "$FILE" "${FILE}.backup_efficiency_numerator"

python3 - <<'PY'
from pathlib import Path

p = Path("run_semantic_re_etx.py")
text = p.read_text()

old = """        else:
            total_semantic_payload_bits += int(
                config.num_nodes
                * config.packet_size
            )"""

new = """        else:
            total_semantic_payload_bits += 0"""

if old not in text:
    raise RuntimeError(
        "Old semantic numerator block not found"
    )

text = text.replace(
    old,
    new,
    1
)

old2 = """            total_radio_bits += int(
                result.radio_bits
            )"""

new2 = """            total_radio_bits += int(
                result.radio_bits
            )

            if config.semantic_payload_enabled:
                total_semantic_payload_bits += int(
                    semantic_payload_bits[source]
                )
            else:
                total_semantic_payload_bits += int(
                    config.packet_size
                )"""

if old2 not in text:
    raise RuntimeError(
        "Radio counter block not found"
    )

text = text.replace(
    old2,
    new2,
    1
)

p.write_text(text)

print("Efficiency numerator aligned with transmissions")

PY

python -m py_compile "$FILE"

echo "Verification:"
grep -n "total_semantic_payload_bits" "$FILE"

echo "DONE"

