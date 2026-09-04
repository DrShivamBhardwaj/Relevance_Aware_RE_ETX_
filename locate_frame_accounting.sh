#!/bin/bash

set -e

echo "===== Frame accounting region ====="

sed -n '300,430p' simulator/multihop_transmission.py

