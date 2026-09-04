#!/bin/bash

set -e

FILE="run_semantic_re_etx.py"

echo "Creating backup..."
cp "$FILE" "${FILE}.backup_w025"

echo "Changing semantic_weight 0.25 -> 0.50..."

python3 - <<'PY'
from pathlib import Path

p = Path("run_semantic_re_etx.py")
text = p.read_text()

old = "semantic_weight=0.25,"
new = "semantic_weight=0.50,"

count = text.count(old)

if count != 1:
    raise RuntimeError(
        f"Expected exactly 1 occurrence, found {count}"
    )

text = text.replace(old, new)

p.write_text(text)

print("semantic_weight updated")
PY

echo "Verifying..."
grep -n "semantic_weight" "$FILE"

echo "Compiling..."
python -m py_compile "$FILE"

echo "DONE"
