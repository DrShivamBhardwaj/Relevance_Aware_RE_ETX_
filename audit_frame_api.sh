#!/bin/bash

set -e

echo "===== FrameModel methods ====="

sed -n '1,170p' simulator/frame.py

echo ""

echo "===== Fragment call location ====="

sed -n '210,230p' simulator/multihop_transmission.py

