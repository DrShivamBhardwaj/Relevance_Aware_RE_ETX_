#!/bin/bash

set -e

FILE="run_semantic_re_etx.py"

echo "Creating backup..."
cp "$FILE" "${FILE}.backup_metric_split"

python3 - <<'PY'
from pathlib import Path

p = Path("run_semantic_re_etx.py")
text = p.read_text()

old = """        if total_radio_bits > 0:
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

new = """        total_full_payload_bits = (
            generated_messages
            *
            config.packet_size
        )

        if total_full_payload_bits > 0:
            semantic_compression_ratio = (
                total_semantic_payload_bits
                /
                total_full_payload_bits
            )

            print(
                f"Semantic compression ratio   : "
                f"{semantic_compression_ratio:.6f}"
            )

        if total_radio_bits > 0:
            semantic_radio_efficiency = (
                total_semantic_payload_bits
                /
                total_radio_bits
            )

            print(
                f"Semantic radio efficiency    : "
                f"{semantic_radio_efficiency:.6f}"
            )
"""

if old not in text:
    raise RuntimeError(
        "Semantic efficiency reporting block not found"
    )

text = text.replace(
    old,
    new,
    1
)

p.write_text(text)

print("Metric split added")

PY

python -m py_compile "$FILE"

echo "Verification:"
grep -n "Semantic compression\|Semantic radio" "$FILE"

echo "DONE"

