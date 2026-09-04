#!/bin/bash

set -e

python3 - <<'PY'
from pathlib import Path

p = Path("config.py")
text = p.read_text()

text = text.replace(
    "semantic_routing_enabled: bool = True",
    "semantic_routing_enabled: bool = True"
)

text = text.replace(
    "semantic_payload_enabled: bool = False",
    "semantic_payload_enabled: bool = True"
)

p.write_text(text)

PY

echo "Running C3 Full Semantic Framework"

python run_semantic_re_etx.py > results/c3_full_semantic_seed42.txt

grep -E "FND|HND|LND|PDR \\(%\\)|Goodput|Payload reduction|Semantic efficiency" \
results/c3_full_semantic_seed42.txt

