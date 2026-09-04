#!/bin/bash

set -e

echo "===== transmitter app_bits ====="
grep -n "app_bits" simulator/multihop_transmission.py

echo ""

echo "===== frame fragmentation call ====="
grep -n "fragment_sizes\|fragment_payloads" simulator/multihop_transmission.py

