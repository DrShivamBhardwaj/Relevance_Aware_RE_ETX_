#!/bin/bash

set -e

echo "===== Semantic payload counter ====="
grep -n "total_semantic_payload_bits" run_semantic_re_etx.py

echo ""

echo "===== Radio bits counter ====="
grep -n "total_radio_bits" run_semantic_re_etx.py

echo ""

echo "===== Around semantic payload accumulation ====="
sed -n '185,210p' run_semantic_re_etx.py

echo ""

echo "===== Around radio accumulation ====="
sed -n '340,360p' run_semantic_re_etx.py

echo ""

echo "===== Efficiency calculation ====="
sed -n '755,775p' run_semantic_re_etx.py

