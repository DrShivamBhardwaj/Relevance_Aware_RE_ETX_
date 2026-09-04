#!/bin/bash

FILE="run_semantic_re_etx.py"

echo "Fixing corrupted schedule block..."

python3 - <<'PY'
from pathlib import Path

p = Path("run_semantic_re_etx.py")
text = p.read_text()

bad = "schedule = rotate_schedule(results/semantic_w025.txt"

if bad in text:
    text = text.replace(
        bad,
        """schedule = rotate_schedule(
            alive_at_start,
            round_id
        )"""
    )
    p.write_text(text)
    print("Schedule block repaired")
else:
    print("Corrupted schedule block not found - no change")
PY

echo "Checking syntax..."
python -m py_compile "$FILE"

echo "Done"
