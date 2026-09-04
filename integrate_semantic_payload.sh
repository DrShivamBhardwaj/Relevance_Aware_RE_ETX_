#!/bin/bash

set -e

FILE="run_semantic_re_etx.py"

echo "Creating backup..."
cp "$FILE" "${FILE}.backup_before_payload"

python3 - <<'PY'
from pathlib import Path
import re

p = Path("run_semantic_re_etx.py")
text = p.read_text()

# Add import
if "from simulator.semantic_payload import SemanticPayloadController" not in text:
    anchor = "from simulator.semantic_age import SemanticAgeTracker"
    if anchor not in text:
        raise RuntimeError("SemanticAgeTracker import not found")

    text = text.replace(
        anchor,
        anchor + "\nfrom simulator.semantic_payload import SemanticPayloadController",
        1
    )


# Add controller initialization
if "semantic_payload_controller =" not in text:

    anchor = "semantic_tracker = SemanticAgeTracker("

    idx = text.find(anchor)

    if idx == -1:
        raise RuntimeError("SemanticAgeTracker initialization not found")

    end = text.find(")", idx)

    if end == -1:
        raise RuntimeError("Initialization end not found")

    end += 1

    text = (
        text[:end]
        +
        "\n\n    semantic_payload_controller = SemanticPayloadController(config)"
        +
        text[end:]
    )


# Add payload calculation after semantic_age
if "semantic_payload_bits =" not in text:

    anchor = """semantic_age = semantic_tracker.semantic_age(
            relevance
        )"""

    if anchor not in text:
        raise RuntimeError("Semantic age calculation block not found")

    replacement = anchor + """

        semantic_payload_bits = (
            semantic_payload_controller.payload_bits(
                relevance
            )
        )
"""

    text = text.replace(anchor, replacement, 1)


# Replace transmitter call
old = """result = transmitter.transmit(
                network,
                path,
                round_id=round_id
            )"""

new = """result = transmitter.transmit(
                network,
                path,
                round_id=round_id,
                app_bits=int(
                    semantic_payload_bits[source]
                )
            )"""

if old not in text:
    raise RuntimeError("Transmit block not found")

text = text.replace(old, new, 1)


# Replace metrics accounting
old = """packet_size=
                        config.packet_size"""

new = """packet_size=
                        int(
                            semantic_payload_bits[source]
                        )"""

if old not in text:
    raise RuntimeError("Metrics packet size block not found")

text = text.replace(old, new, 1)


p.write_text(text)

print("Semantic payload integration completed")

PY

echo "Compiling..."

python -m py_compile "$FILE"

echo "Checking integration..."

grep -n "SemanticPayloadController" "$FILE"
grep -n "semantic_payload_bits" "$FILE"
grep -n "app_bits" "$FILE"

echo "DONE"

