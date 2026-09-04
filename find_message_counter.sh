#!/bin/bash

set -e

echo "===== Message counters ====="

grep -n "generated\|attempted\|delivered" run_semantic_re_etx.py

echo ""

echo "===== Around counter initialization ====="

sed -n '120,150p' run_semantic_re_etx.py

