#!/bin/bash

set -e

FILE="run_semantic_re_etx.py"

echo "Creating backup..."
cp "$FILE" "${FILE}.backup_ablation_switches"

python3 - <<'PY'
from pathlib import Path

p = Path("run_semantic_re_etx.py")
text = p.read_text()

# ---------- Payload controller ----------
old = """    semantic_payload_controller = SemanticPayloadController(config)"""

new = """    semantic_payload_controller = None

    if config.semantic_payload_enabled:
        semantic_payload_controller = SemanticPayloadController(config)"""

if old not in text:
    raise RuntimeError("Payload controller block not found")

text = text.replace(old, new, 1)


# ---------- Payload generation ----------
old = """        semantic_payload_bits = (
            semantic_payload_controller.payload_bits(
                relevance
            )
        )"""

new = """        if config.semantic_payload_enabled:
            semantic_payload_bits = (
                semantic_payload_controller.payload_bits(
                    relevance
                )
            )
        else:
            semantic_payload_bits = np.full(
                config.num_nodes,
                config.packet_size,
                dtype=np.int64
            )"""

if old not in text:
    raise RuntimeError("Payload generation block not found")

text = text.replace(old, new, 1)


# ---------- Router semantic weight ----------
old = """            energy_weight=0.25,
            semantic_weight=1.00,
            semantic_age=semantic_age"""

new = """            energy_weight=0.25,
            semantic_weight=(
                1.00
                if config.semantic_routing_enabled
                else 0.0
            ),
            semantic_age=(
                semantic_age
                if config.semantic_routing_enabled
                else np.zeros(
                    config.num_nodes
                )
            )"""

if old not in text:
    raise RuntimeError("Router semantic block not found")

text = text.replace(old, new, 1)

p.write_text(text)

print("Ablation switches integrated")

PY

python -m py_compile "$FILE"

echo "Verification:"
grep -n "semantic_payload_enabled\|semantic_routing_enabled\|semantic_weight" "$FILE"

echo "DONE"

