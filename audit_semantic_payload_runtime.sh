#!/bin/bash

set -e

FILE="run_semantic_re_etx.py"

echo "=============================================="
echo "SEMANTIC PAYLOAD RUNTIME AUDIT"
echo "=============================================="

cp "$FILE" "${FILE}.backup_payload_audit"

python3 - <<'PY'
from pathlib import Path

p = Path("run_semantic_re_etx.py")
text = p.read_text()

# Add storage
if "payload_bits_history" not in text:

    anchor = "records = []"

    if anchor not in text:
        raise RuntimeError("records initialization not found")

    text = text.replace(
        anchor,
        """records = []

    payload_bits_history = []""",
        1
    )


# Log payload bits after generation
if "payload_bits_history.append" not in text:

    anchor = """semantic_payload_bits = (
            semantic_payload_controller.payload_bits(
                relevance
            )
        )"""

    if anchor not in text:
        raise RuntimeError("semantic payload calculation block not found")

    replacement = anchor + """

        payload_bits_history.extend(
            semantic_payload_bits.tolist()
        )
"""

    text = text.replace(anchor, replacement, 1)


# Add final reporting
if "Average semantic payload bits" not in text:

    anchor = """print(
        f"Residual network energy     : "
        f"{network.total_residual_energy:.9f} J"
    )"""

    if anchor not in text:
        raise RuntimeError("report insertion point not found")

    replacement = """print(
        f"Residual network energy     : "
        f"{network.total_residual_energy:.9f} J"
    )

    if payload_bits_history:
        print(
            f"Average semantic payload bits : "
            f"{np.mean(payload_bits_history):.2f}"
        )

        print(
            f"Minimum semantic payload bits : "
            f"{np.min(payload_bits_history)}"
        )

        print(
            f"Maximum semantic payload bits : "
            f"{np.max(payload_bits_history)}"
        )

        print(
            f"Payload reduction (%)         : "
            f"{(1 - np.mean(payload_bits_history)/config.packet_size)*100:.2f}"
        )
"""

    text = text.replace(anchor, replacement, 1)


p.write_text(text)

print("Payload audit instrumentation added")

PY

python -m py_compile "$FILE"

echo "Audit patch complete"

