#!/bin/bash

set -e

FILE="run_semantic_re_etx.py"

cp "$FILE" "${FILE}.backup_w050"

python3 - <<'PY'
from pathlib import Path

p = Path("run_semantic_re_etx.py")
text = p.read_text()

old = "semantic_weight=0.50,"
new = "semantic_weight=1.00,"

if text.count(old) != 1:
    raise RuntimeError("semantic_weight=0.50 not found exactly once")

text = text.replace(old, new)

p.write_text(text)

print("semantic_weight updated to 1.00")
PY

grep -n "semantic_weight" "$FILE"

python -m py_compile "$FILE"

echo "DONE"
