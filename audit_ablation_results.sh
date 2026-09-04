#!/bin/bash

set -e

echo "=============================================="
echo "ABLATION RESULT FILE CHECK"
echo "=============================================="

ls -lh results/ablation

echo ""

echo "File count:"
ls results/ablation/*.txt | wc -l

echo ""

echo "Sample C1:"
grep -E "FND|HND|LND|PDR \(%\)|Payload reduction|Semantic compression|Semantic radio" \
results/ablation/C1_RE_ETX_seed_42.txt

echo ""

echo "Sample C3:"
grep -E "FND|HND|LND|PDR \(%\)|Payload reduction|Semantic compression|Semantic radio" \
results/ablation/C3_FULL_SEMANTIC_seed_42.txt

