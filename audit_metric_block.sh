#!/bin/bash

set -e

echo "===== Efficiency reporting area ====="

sed -n '745,785p' run_semantic_re_etx.py

echo ""

echo "===== Semantic labels ====="

grep -n "Semantic efficiency\|semantic_efficiency\|compression\|radio" run_semantic_re_etx.py

