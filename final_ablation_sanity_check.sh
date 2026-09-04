#!/bin/bash

set -e

echo "=============================================="
echo "FINAL ABLATION SANITY CHECK"
echo "=============================================="

echo ""
echo "Python compile..."
python -m py_compile run_semantic_re_etx.py

echo ""
echo "Running current configuration..."

python run_semantic_re_etx.py | grep -E \
"FND|HND|LND|PDR|Payload reduction|Semantic compression|Semantic radio"

echo ""
echo "SANITY CHECK COMPLETE"

