#!/bin/bash

set -e

FILE="run_semantic_re_etx.py"

echo "Creating backup..."
cp "$FILE" "${FILE}.backup_remove_debug"

python3 - <<'PY'
from pathlib import Path

p = Path("run_semantic_re_etx.py")
text = p.read_text()

old = """    print(
        f"DEBUG full payload bits        : {total_full_payload_bits}"
    )
    print(
        f"DEBUG semantic payload bits    : {total_semantic_payload_bits}"
    )
    print(
        f"DEBUG radio bits               : {total_radio_bits}"
    )

"""

if old not in text:
    raise RuntimeError(
        "Debug block not found"
    )

text = text.replace(old, "", 1)

p.write_text(text)

print("Debug instrumentation removed")

PY

python -m py_compile "$FILE"

echo "DONE"

