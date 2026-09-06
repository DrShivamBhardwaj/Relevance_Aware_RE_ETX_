import csv
import os
import re
import shutil
import subprocess
from pathlib import Path

SEEDS = [11, 23, 42, 67, 101, 137, 173, 211, 257, 307]
MODES = ["C1", "C3", "C5"]

PROFILES = {
    "shallow": {
        "area_height": 150,
        "bs_y": 200,
        "link_radius": 25,
        "calibrated_mean_hops": 1.483,
    },
    "medium": {
        "area_height": 400,
        "bs_y": 450,
        "link_radius": 45,
        "calibrated_mean_hops": 2.910,
    },
    "deep": {
        "area_height": 600,
        "bs_y": 650,
        "link_radius": 60,
        "calibrated_mean_hops": 4.929,
    },
}

ROOT = Path("results/master_validation")
LOG_DIR = ROOT / "logs" / "topology_sensitivity"
ROUND_DIR = ROOT / "raw" / "topology_sensitivity_rounds"
OUT = ROOT / "statistics" / "topology_sensitivity_raw.csv"

LOG_DIR.mkdir(parents=True, exist_ok=True)
ROUND_DIR.mkdir(parents=True, exist_ok=True)
OUT.parent.mkdir(parents=True, exist_ok=True)


def number(text, label):
    m = re.search(
        rf"^{re.escape(label)}\s*:\s*([-+]?[0-9]*\.?[0-9]+)",
        text,
        flags=re.MULTILINE,
    )
    if not m:
        raise RuntimeError(f"Missing output field: {label}")
    return float(m.group(1))


existing = {}

if OUT.exists():
    with OUT.open(newline="") as f:
        for row in csv.DictReader(f):
            key = (
                row["profile"],
                row["mode"],
                int(row["seed"]),
            )
            existing[key] = row

rows = list(existing.values())

total = len(PROFILES) * len(MODES) * len(SEEDS)
counter = 0

print("=" * 92)
print("TOPOLOGY-DEPTH SENSITIVITY — C1/C3/C5 × 3 DEPTHS × 10 SEEDS")
print("=" * 92)

for profile, cfg in PROFILES.items():
    for mode in MODES:
        for seed in SEEDS:
            counter += 1
            key = (profile, mode, seed)

            if key in existing:
                print(
                    f"[{counter:02d}/{total}] "
                    f"{profile} {mode} seed={seed} "
                    f"ALREADY COMPLETE - SKIPPED"
                )
                continue

            print(
                f"[{counter:02d}/{total}] "
                f"RUNNING {profile} {mode} seed={seed}"
            )

            env = os.environ.copy()
            env["EXPERIMENT_MODE"] = mode
            env["SEMANTIC_SEED"] = str(seed)
            env["NUM_NODES"] = "100"
            env["AREA_WIDTH_M"] = "100"
            env["AREA_HEIGHT_M"] = str(cfg["area_height"])
            env["BS_X_M"] = "50"
            env["BS_Y_M"] = str(cfg["bs_y"])
            env["MAX_SENSOR_LINK_DISTANCE_M"] = str(
                cfg["link_radius"]
            )
            env["EQUAL_BUDGET_PAYLOAD_BITS"] = "1744"

            result = subprocess.run(
                ["python", "-u", "run_semantic_re_etx.py"],
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )

            log_path = (
                LOG_DIR
                / f"{profile}_{mode}_seed{seed}.log"
            )
            log_path.write_text(result.stdout)

            if result.returncode != 0:
                print(result.stdout)
                raise RuntimeError(
                    f"{profile} {mode} seed={seed} FAILED"
                )

            if (
                "All dynamic minimum-ETX checks PASSED."
                not in result.stdout
            ):
                raise RuntimeError(
                    f"{profile} {mode} seed={seed} "
                    "did not pass simulator checks"
                )

            shutil.copy2(
                "results/minimum_etx_multihop.csv",
                ROUND_DIR
                / f"{profile}_{mode}_seed{seed}_rounds.csv",
            )

            compression = number(
                result.stdout,
                "Semantic compression ratio",
            )

            row = {
                "profile": profile,
                "mode": mode,
                "seed": seed,
                "area_width_m": 100,
                "area_height_m": cfg["area_height"],
                "bs_y_m": cfg["bs_y"],
                "link_radius_m": cfg["link_radius"],
                "calibrated_initial_mean_hops":
                    cfg["calibrated_mean_hops"],
                "FND": int(number(result.stdout, "FND")),
                "HND": int(number(result.stdout, "HND")),
                "LND": int(number(result.stdout, "LND")),
                "PDR_percent": number(
                    result.stdout,
                    "PDR (%)",
                ),
                "average_delivered_hops": number(
                    result.stdout,
                    "Average delivered hops",
                ),
                "average_delay_ms": number(
                    result.stdout,
                    "Average delay",
                ),
                "goodput_kbps": number(
                    result.stdout,
                    "Application goodput",
                ),
                "energy_per_delivered_j": number(
                    result.stdout,
                    "Energy/delivered message",
                ),
                "retransmissions": int(number(
                    result.stdout,
                    "Retransmissions",
                )),
                "generated_messages": int(number(
                    result.stdout,
                    "Generated messages",
                )),
                "attempted_mean_payload_bits":
                    compression * 4000.0,
                "event_report_delivery_ratio": number(
                    result.stdout,
                    "Event report delivery ratio",
                ),
                "event_payload_preservation": number(
                    result.stdout,
                    "Event payload preservation",
                ),
                "event_payload_delivery_ratio": number(
                    result.stdout,
                    "Event payload delivery ratio",
                ),
                "within_round_targeting_gap_bits": number(
                    result.stdout,
                    "Within-round targeting gap",
                ),
            }

            row["retries_per_generated"] = (
                row["retransmissions"]
                / row["generated_messages"]
            )

            rows.append(row)
            existing[key] = row

            fieldnames = list(row.keys())

            normalized = [
                {
                    field: item.get(field, "")
                    for field in fieldnames
                }
                for item in rows
            ]

            profile_order = {
                "shallow": 0,
                "medium": 1,
                "deep": 2,
            }

            mode_order = {
                "C1": 0,
                "C3": 1,
                "C5": 2,
            }

            normalized.sort(
                key=lambda r: (
                    profile_order[r["profile"]],
                    mode_order[r["mode"]],
                    int(r["seed"]),
                )
            )

            with OUT.open("w", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=fieldnames,
                )
                writer.writeheader()
                writer.writerows(normalized)

            print(
                f"SAVED {profile} {mode} seed={seed}"
            )

print("=" * 92)
print("90-RUN TOPOLOGY SENSITIVITY COMPLETE")
print(OUT)
print("=" * 92)
