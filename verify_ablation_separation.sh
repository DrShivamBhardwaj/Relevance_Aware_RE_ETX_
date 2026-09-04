#!/bin/bash

set -e

echo "===== C1 sample ====="

grep -E \
"FND|HND|LND|PDR \(%\)|Payload reduction|Semantic compression|Semantic radio" \
results/ablation/C1_RE_ETX_seed_42.txt

echo ""

echo "===== C2 sample ====="

grep -E \
"FND|HND|LND|PDR \(%\)|Payload reduction|Semantic compression|Semantic radio" \
results/ablation/C2_SEMANTIC_ROUTING_seed_42.txt

echo ""

echo "===== C3 sample ====="

grep -E \
"FND|HND|LND|PDR \(%\)|Payload reduction|Semantic compression|Semantic radio" \
results/ablation/C3_FULL_SEMANTIC_seed_42.txt

