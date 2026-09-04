#!/bin/bash

set -e

FILE="simulator/multihop_transmission.py"

echo "Creating backup..."
cp "$FILE" "${FILE}.backup_radio_bits"

python3 - <<'PY'
from pathlib import Path

p = Path("simulator/multihop_transmission.py")
text = p.read_text()

if "radio_bits += frame_bits" in text:
    print("radio_bits accounting already exists")
    raise SystemExit

old = """                for attempt in range(
                    self.max_attempts
                ):"""

new = """                for attempt in range(
                    self.max_attempts
                ):

                    # Count every physical frame attempt,
                    # including retransmissions.
                    radio_bits += frame_bits"""

if old not in text:
    raise RuntimeError(
        "Frame retry loop not found"
    )

text = text.replace(
    old,
    new,
    1
)

p.write_text(text)

print("Radio bit accounting inserted")

PY

python -m py_compile "$FILE"

echo "Verification:"
grep -n "radio_bits += frame_bits" "$FILE"

echo "DONE"

