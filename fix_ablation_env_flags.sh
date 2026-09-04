#!/bin/bash

set -e

FILE="config.py"

echo "Creating backup..."
cp "$FILE" "${FILE}.backup_env_flags"

python3 - <<'PY'
from pathlib import Path

p = Path("config.py")
text = p.read_text()

old = """    semantic_routing_enabled: bool = True
    semantic_payload_enabled: bool = True
"""

new = """    semantic_routing_enabled: bool = (
        os.environ.get(
            "SEMANTIC_ROUTING_ENABLED",
            "true"
        ).lower()
        == "true"
    )

    semantic_payload_enabled: bool = (
        os.environ.get(
            "SEMANTIC_PAYLOAD_ENABLED",
            "true"
        ).lower()
        == "true"
    )
"""

if old not in text:
    raise RuntimeError(
        "Static ablation flags not found"
    )

text = text.replace(
    old,
    new,
    1
)

p.write_text(text)

print("Environment-controlled ablation flags added")

PY

python -m py_compile "$FILE"

echo "Verification:"
grep -n "semantic_routing_enabled\|semantic_payload_enabled" "$FILE"

echo "DONE"

