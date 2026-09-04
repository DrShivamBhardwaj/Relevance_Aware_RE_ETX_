#!/bin/bash

set -e

echo "=============================================="
echo "SEMANTIC PAYLOAD MODULE AUDIT"
echo "=============================================="

FILE="simulator/semantic_payload.py"

if [ ! -f "$FILE" ]; then
    echo "semantic_payload.py missing"
    exit 1
fi

echo ""
echo "---- File Structure ----"
grep -n "^class\|^    def " "$FILE"

echo ""
echo "---- Content Preview ----"
sed -n '1,220p' "$FILE"

echo ""
echo "---- Frame Integration Search ----"
grep -R "semantic_payload\|payload" simulator/frame.py simulator/multihop_transmission.py run_semantic_re_etx.py || true

echo ""
echo "AUDIT COMPLETE"

