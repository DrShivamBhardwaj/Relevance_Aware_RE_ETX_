#!/bin/bash

set -e

echo "===== Reporting section ====="

sed -n '740,805p' run_semantic_re_etx.py

echo ""

echo "===== Counter values print search ====="

grep -n "Semantic compression ratio\|Semantic radio efficiency\|total_full_payload_bits\|total_radio_bits" run_semantic_re_etx.py

