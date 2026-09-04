#!/bin/bash

set -e

FILE="config.py"

echo "Creating backup..."
cp "$FILE" "${FILE}.backup_seed_env"

python3 - <<'PY'
from pathlib import Path

p = Path("config.py")
text = p.read_text()

old = """seed: int = 42"""

new = """seed: int = int(
        os.environ.get(
            "SEMANTIC_SEED",
            42
        )
    )"""

if old not in text:
    raise RuntimeError(
        "Seed definition not found"
    )

if "import os" not in text:
    text = "import os\n\n" + text

text = text.replace(
    old,
    new,
    1
)

p.write_text(text)

print("Environment seed override added")

PY

python -m py_compile "$FILE"

grep -n "seed" "$FILE"

echo "DONE"

