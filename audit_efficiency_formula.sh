#!/bin/bash

set -e

echo "===== Efficiency calculation ====="

sed -n '745,775p' run_semantic_re_etx.py

echo ""
echo "===== Radio bit accumulation ====="

grep -n "total_radio_bits" run_semantic_re_etx.py

echo ""
echo "===== Transmitter radio bits ====="

grep -n "radio_bits" simulator/multihop_transmission.py

