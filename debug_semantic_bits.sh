#!/bin/bash

set -e

echo "===== semantic payload counter ====="

grep -n "total_semantic_payload_bits" run_semantic_re_etx.py

echo ""
echo "===== payload generation block ====="

sed -n '165,185p' run_semantic_re_etx.py

echo ""
echo "===== radio collection block ====="

sed -n '285,310p' run_semantic_re_etx.py

