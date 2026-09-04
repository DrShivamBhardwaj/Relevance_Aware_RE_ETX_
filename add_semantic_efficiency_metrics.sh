#!/bin/bash

set -e

FILE="run_semantic_re_etx.py"

echo "Creating backup..."
cp "$FILE" "${FILE}.backup_semantic_efficiency"

python3 - <<'PY'
from pathlib import Path

p = Path("run_semantic_re_etx.py")
text = p.read_text()

# Add counters
if "total_semantic_payload_bits" not in text:

    anchor = "payload_bits_history = []"

    if anchor not in text:
        raise RuntimeError("Payload history block not found")

    text = text.replace(
        anchor,
        """payload_bits_history = []

    total_semantic_payload_bits = 0
    total_full_payload_bits = 0
    total_radio_bits = 0""",
        1
    )


# Add accumulation after payload generation
if "total_semantic_payload_bits +=" not in text:

    anchor = """payload_bits_history.extend(
            semantic_payload_bits.tolist()
        )"""

    if anchor not in text:
        raise RuntimeError("Payload history insertion point not found")

    text = text.replace(
        anchor,
        """payload_bits_history.extend(
            semantic_payload_bits.tolist()
        )

        total_semantic_payload_bits += int(
            np.sum(semantic_payload_bits)
        )

        total_full_payload_bits += (
            config.num_nodes
            *
            config.packet_size
        )""",
        1
    )


# Add radio bits accumulation after transmission result
if "total_radio_bits +=" not in text:

    anchor = """round_airtime += (
                result.airtime
            )"""

    if anchor not in text:
        raise RuntimeError("Transmission accounting block not found")

    text = text.replace(
        anchor,
        """round_airtime += (
                result.airtime
            )

            total_radio_bits += int(
                result.radio_bits
            )""",
        1
    )


# Add final reporting
if "Semantic efficiency" not in text:

    anchor = """print(
        f"Payload reduction (%)         : "
        f"{(1 - np.mean(payload_bits_history)/config.packet_size)*100:.2f}"
    )"""

    if anchor not in text:
        raise RuntimeError("Payload report block not found")

    text = text.replace(
        anchor,
        """print(
            f"Payload reduction (%)         : "
            f"{(1 - np.mean(payload_bits_history)/config.packet_size)*100:.2f}"
        )

        if total_radio_bits > 0:
            semantic_efficiency = (
                total_semantic_payload_bits
                /
                total_radio_bits
            )

            print(
                f"Semantic efficiency          : "
                f"{semantic_efficiency:.6f}"
            )""",
        1
    )


p.write_text(text)

print("Semantic efficiency metrics added")

PY

python -m py_compile "$FILE"

echo "DONE"

