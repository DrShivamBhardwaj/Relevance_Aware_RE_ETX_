#!/bin/bash

set -e

echo "=============================================="
echo "SEMANTIC WSN PROJECT STATUS CHECK"
echo "=============================================="

echo ""
echo "---- Python Syntax Check ----"

python -m py_compile \
    simulator/*.py \
    run_semantic_re_etx.py

echo "Syntax: PASS"


echo ""
echo "---- Core Simulator Modules ----"

for file in \
    simulator/topology.py \
    simulator/energy.py \
    simulator/channel.py \
    simulator/frame.py \
    simulator/link_graph.py \
    simulator/multihop_transmission.py \
    simulator/routing_re_etx.py \
    simulator/routing_semantic_re_etx.py \
    simulator/semantic_relevance.py \
    simulator/semantic_age.py
do
    if [ -f "$file" ]; then
        echo "[OK] $file"
    else
        echo "[MISSING] $file"
    fi
done


echo ""
echo "---- Semantic Integration Check ----"

grep -n "SemanticResidualEnergyETXRouter" run_semantic_re_etx.py || true

grep -n "SemanticAgeTracker" run_semantic_re_etx.py || true

grep -n "semantic_age" run_semantic_re_etx.py || true

grep -n "semantic_weight" run_semantic_re_etx.py || true


echo ""
echo "---- Routing Semantic Cost Check ----"

grep -n "semantic_weight" simulator/routing_semantic_re_etx.py || true

grep -n "semantic_age" simulator/routing_semantic_re_etx.py || true


echo ""
echo "---- Pending Module Check ----"

for file in \
    simulator/semantic_payload.py \
    simulator/duty_cycle.py \
    simulator/qos_optimizer.py \
    simulator/edge_optimizer.py
do
    if [ -f "$file" ]; then
        echo "[FOUND] $file"
    else
        echo "[PENDING] $file"
    fi
done


echo ""
echo "---- Latest Results ----"

if [ -d results ]; then
    ls -lh results | tail -10
else
    echo "results directory not found"
fi


echo ""
echo "=============================================="
echo "STATUS CHECK COMPLETE"
echo "=============================================="

