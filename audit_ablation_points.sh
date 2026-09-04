#!/bin/bash

set -e

echo "===== Router initialization ====="
sed -n '200,220p' run_semantic_re_etx.py

echo ""
echo "===== Payload initialization ====="
sed -n '85,100p' run_semantic_re_etx.py

echo ""
echo "===== Payload generation ====="
sed -n '170,185p' run_semantic_re_etx.py

