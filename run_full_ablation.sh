#!/bin/bash

set -e

mkdir -p results/ablation

SEEDS=(11 23 42 67 101 137 173 211 257 307)

run_case () {

    CASE=$1
    ROUTING=$2
    PAYLOAD=$3

    echo "=============================================="
    echo "Running $CASE"
    echo "semantic_routing=$ROUTING"
    echo "semantic_payload=$PAYLOAD"
    echo "=============================================="

    for SEED in "${SEEDS[@]}"
    do
        echo "Seed: $SEED"

        SEMANTIC_SEED=$SEED \
        SEMANTIC_ROUTING_ENABLED=$ROUTING \
        SEMANTIC_PAYLOAD_ENABLED=$PAYLOAD \
        python run_semantic_re_etx.py \
        > results/ablation/${CASE}_seed_${SEED}.txt

    done
}

run_case C1_RE_ETX false false

run_case C2_SEMANTIC_ROUTING true false

run_case C3_FULL_SEMANTIC true true


echo "=============================================="
echo "ABLATION COMPLETE"
echo "=============================================="

