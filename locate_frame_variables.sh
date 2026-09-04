#!/bin/bash

set -e

echo "===== Frame variables ====="

grep -n "frame_size\|fragment\|payloads\|frame_airtime\|for .*frame" simulator/multihop_transmission.py

echo ""
echo "===== Region around frame loop ====="

sed -n '220,330p' simulator/multihop_transmission.py

