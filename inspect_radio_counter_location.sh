#!/bin/bash

set -e

sed -n '335,360p' run_semantic_re_etx.py

echo "----------------"

sed -n '755,772p' run_semantic_re_etx.py

