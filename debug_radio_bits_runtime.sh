#!/bin/bash

set -e

FILE="run_semantic_re_etx.py"

echo "===== total_radio_bits references ====="

grep -n "total_radio_bits" "$FILE"

echo ""
echo "===== result.radio_bits references ====="

grep -n "result.radio_bits" "$FILE"

echo ""
echo "===== MultiHopResult radio_bits return ====="

grep -n "radio_bits" simulator/multihop_transmission.py

