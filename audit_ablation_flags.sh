#!/bin/bash

set -e

echo "===== Config flags ====="

grep -n "semantic_routing_enabled\|semantic_payload_enabled" config.py

echo ""

echo "===== Environment usage ====="

grep -n "SEMANTIC_ROUTING\|SEMANTIC_PAYLOAD" config.py

echo ""

echo "===== Runner router condition ====="

grep -n "semantic_routing_enabled\|semantic_payload_enabled" run_semantic_re_etx.py

