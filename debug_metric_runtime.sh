#!/bin/bash

set -e

python3 - <<'PY'
from pathlib import Path

p = Path("run_semantic_re_etx.py")
text = p.read_text()

old = """    if payload_bits_history:
        print(
            f"Average semantic payload bits : "
            f"{np.mean(payload_bits_history):.2f}"
        )
"""

new = """    print(
        f"DEBUG full payload bits        : {total_full_payload_bits}"
    )
    print(
        f"DEBUG semantic payload bits    : {total_semantic_payload_bits}"
    )
    print(
        f"DEBUG radio bits               : {total_radio_bits}"
    )

    if payload_bits_history:
        print(
            f"Average semantic payload bits : "
            f"{np.mean(payload_bits_history):.2f}"
        )
"""

if old not in text:
    raise RuntimeError("Debug insertion point not found")

text = text.replace(old, new, 1)

p.write_text(text)

PY

python -m py_compile run_semantic_re_etx.py

python run_semantic_re_etx.py | grep -E "DEBUG|Payload reduction|Semantic"

