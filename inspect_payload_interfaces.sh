#!/bin/bash

set -e

echo "===== SEMANTIC PAYLOAD CLASS ====="
grep -n "^class\|^    def " simulator/semantic_payload.py

echo ""
echo "===== FRAME METHODS ====="
grep -n "^class\|^    def " simulator/frame.py

echo ""
echo "===== TRANSMITTER METHODS ====="
grep -n "^class\|^    def " simulator/multihop_transmission.py

echo ""
echo "===== RUNNER PAYLOAD GENERATION ====="
grep -n "packet_size\|payload\|transmit\|send" run_semantic_re_etx.py

