#!/bin/bash

set -e

mkdir -p results/semantic_multiseed

SEEDS=(11 23 42 67 101 137 173 211 257 307)

echo "=============================================="
echo "SEMANTIC MULTI-SEED EXPERIMENT"
echo "=============================================="

for SEED in "${SEEDS[@]}"
do
    echo ""
    echo "Running seed: $SEED"

    export SEMANTIC_SEED=$SEED

    python run_semantic_re_etx.py \
        > results/semantic_multiseed/seed_${SEED}.txt

done

echo ""
echo "All semantic seeds completed"

