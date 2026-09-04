#!/bin/bash

set -e

echo "===== semantic_payload.py ====="
sed -n '1,180p' simulator/semantic_payload.py

echo ""
echo "===== multihop_transmission transmit ====="
sed -n '90,150p' simulator/multihop_transmission.py

echo ""
echo "===== runner around transmit ====="
sed -n '260,330p' run_semantic_re_etx.py

