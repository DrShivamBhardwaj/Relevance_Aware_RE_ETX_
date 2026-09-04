#!/bin/bash

set -e

echo "===== total_full_payload_bits references ====="
grep -n "total_full_payload_bits" run_semantic_re_etx.py

echo ""

echo "===== Around transmission accounting ====="
sed -n '335,360p' run_semantic_re_etx.py

