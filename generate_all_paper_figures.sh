#!/bin/bash

set -e

echo "=============================================="
echo "GENERATING IEEE PAPER FIGURES"
echo "=============================================="

mkdir -p plots
mkdir -p results/architecture

cat > plots/generate_all_figures.py <<'PY'

import os
import numpy as np
import matplotlib.pyplot as plt

OUT = "results/architecture"
os.makedirs(OUT, exist_ok=True)


# Fig 4: Framework Architecture

fig, ax = plt.subplots(figsize=(7,10))
ax.axis("off")

items = [
    ("Sensor Observation Layer\n100 IoT Nodes",0.85),
    ("Semantic Intelligence\nRelevance + Semantic Age",0.70),
    ("Adaptive Communication\nPayload Controller + Fragmentation",0.55),
    ("Semantic RE-ETX Routing\nEnergy + ETX + Semantic Priority",0.40),
    ("Wireless Multi-hop Transmission",0.25),
    ("Base Station / Edge Gateway",0.10)
]

for text,y in items:
    ax.text(
        0.5,y,text,
        ha="center",
        va="center",
        fontsize=11,
        bbox=dict(boxstyle="round")
    )

for i in range(len(items)-1):
    ax.annotate(
        "",
        xy=(0.5,items[i+1][1]+0.05),
        xytext=(0.5,items[i][1]-0.05),
        arrowprops=dict(arrowstyle="->")
    )

plt.title("Semantic-Aware Cross-Layer IoT-WSN Framework")
plt.savefig(
    f"{OUT}/Fig4_Semantic_Framework_Architecture.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()


# Fig 5: Payload Controller

rho=np.linspace(0,1,100)
payload_ratio=0.25+0.75*rho

plt.figure(figsize=(7,4))
plt.plot(rho,payload_ratio)
plt.xlabel("Semantic Relevance")
plt.ylabel("Payload Ratio")
plt.title("Adaptive Semantic Payload Controller")
plt.grid(True)

plt.savefig(
    f"{OUT}/Fig5_Semantic_Payload_Controller.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# Fig 6: Fragmentation

fig,ax=plt.subplots(figsize=(8,4))
ax.axis("off")

ax.text(
    0.25,0.5,
    "Conventional Packet\n\n4000 bits\n5 Frames\n5080 Radio Bits",
    ha="center",
    bbox=dict(boxstyle="round")
)

ax.text(
    0.75,0.5,
    "Semantic Packet\n\nReduced Payload\nFewer Frames\nLower Energy",
    ha="center",
    bbox=dict(boxstyle="round")
)

ax.annotate(
    "",
    xy=(0.58,0.5),
    xytext=(0.42,0.5),
    arrowprops=dict(arrowstyle="->")
)

plt.title("Variable Payload Fragmentation")
plt.savefig(
    f"{OUT}/Fig6_Variable_Frame_Fragmentation.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# Fig 7 Routing

fig,ax=plt.subplots(figsize=(7,5))
ax.axis("off")

nodes=[
("Source",0.2,0.5),
("Relay A\nHigh Energy\nHigh Semantic Age",0.55,0.75),
("Relay B\nLow Energy",0.55,0.25),
("Base Station",0.85,0.5)
]

for t,x,y in nodes:
    ax.text(
        x,y,t,
        ha="center",
        bbox=dict(boxstyle="round")
    )

for x1,y1,x2,y2 in [
    (0.25,0.5,0.5,0.75),
    (0.25,0.5,0.5,0.25),
    (0.6,0.75,0.8,0.5)
]:
    ax.annotate(
        "",
        xy=(x2,y2),
        xytext=(x1,y1),
        arrowprops=dict(arrowstyle="->")
    )

plt.title("Semantic RE-ETX Routing Decision")

plt.savefig(
    f"{OUT}/Fig7_Semantic_RE_ETX_Routing.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# Fig 8 Ablation

fig,ax=plt.subplots(figsize=(6,5))
ax.axis("off")

steps=[
("C1 RE-ETX Baseline",0.8),
("C2 Semantic Routing",0.5),
("C3 Full Semantic Framework",0.2)
]

for s,y in steps:
    ax.text(
        0.5,y,s,
        ha="center",
        bbox=dict(boxstyle="round")
    )

ax.annotate("",xy=(0.5,0.58),xytext=(0.5,0.72),
arrowprops=dict(arrowstyle="->"))

ax.annotate("",xy=(0.5,0.28),xytext=(0.5,0.42),
arrowprops=dict(arrowstyle="->"))

plt.title("Ablation Evolution")

plt.savefig(
    f"{OUT}/Fig8_Ablation_Flow.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# Fig 9 Energy

plt.figure(figsize=(5,5))

plt.pie(
    [70,20,10],
    labels=[
        "Communication",
        "Reception",
        "Semantic Processing"
    ],
    autopct="%1.1f%%"
)

plt.title("Energy Consumption Distribution")

plt.savefig(
    f"{OUT}/Fig9_Energy_Breakdown.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


print("All figures generated successfully")

PY


python plots/generate_all_figures.py


echo ""
echo "Generated Figures:"
ls -lh results/architecture/*.png


echo ""
echo "=============================================="
echo "COMPLETE"
echo "=============================================="

