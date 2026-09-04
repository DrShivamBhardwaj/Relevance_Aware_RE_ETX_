#!/bin/bash

set -e

echo "===== MultiHopResult Definition ====="

grep -n "radio_bits" simulator/multihop_transmission.py

echo ""
echo "===== Result Return Blocks ====="

grep -n "MultiHopResult(" simulator/multihop_transmission.py

echo ""
echo "===== radio_bits Usage ====="

grep -n "result.radio_bits\|radio_bits =" simulator/multihop_transmission.py

