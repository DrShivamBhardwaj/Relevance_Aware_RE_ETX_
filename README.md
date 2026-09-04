# Relevance-Aware RE-ETX Semantic Routing for Wireless Sensor Networks

## Overview

This repository contains the simulation framework and experimental results for a relevance-aware RE-ETX based semantic routing approach for wireless sensor networks (WSNs).

The framework integrates routing reliability estimation, energy-aware transmission decisions, and semantic payload optimization to reduce unnecessary communication while maintaining reliable data delivery.

The repository accompanies the research manuscript and provides the implementation, experiment scripts, and generated results required for reproducibility.

---

## Repository Structure

.
├── config.py
├── main.py
├── run_semantic_re_etx.py
│
├── simulator/
│ ├── channel modelling
│ ├── energy model
│ ├── routing modules
│ └── transmission model
│
├── results/
│ ├── ablation results
│ ├── lifetime measurements
│ ├── statistical analysis
│ └── generated figures
│
├── plots/
│
├── run_full_ablation.sh
├── test_ablation_c1.sh
├── test_ablation_c2.sh
└── test_ablation_c3.sh

---

## Requirements

Python 3.x

Install dependencies:

```bash
pip install -r requirements.txt

