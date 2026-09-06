import csv
import os
import re
import shutil
import subprocess
from pathlib import Path

SEEDS = [11, 23, 42, 67, 101, 137, 173, 211, 257, 307]

# Nearest byte-aligned values to the pooled C3 attempted-payload
# means measured separately within each topology profile:
#
# shallow C3 = 1745.53 bits -> 1744
# medium  C3 = 1649.19 bits -> 1648
# deep    C3 = 1570.82 bits -> 1568
PROFILES = {
    "shallow": {
        "area_height": 150,
        "bs_y": 200,
        "link_radius": 25,
        "budget": 1744,
    },
    "medium": {
        "area_height": 400,
        "bs_y": 450,
        "link_radius": 45,
        "budget": 1648,
    },
    "deep": {
        "area_height": 600,
        "bs_y": 650,
        "link_radius": 60,
        "budget": 1568,
    },
}

ROOT = Path("results/master_validation")
CSV_PATH = ROOT / "statistics" / "topology_sensitivity_raw.csv"
LOG_DIR = ROOT / "logs" / "topology_sensitivity_budget_corrected"
ROUND_DIR = ROOT / "raw" / "topology_sensitivity_budget_corrected"

LOG_DIR.mkdir(parents=True, exist_ok=True)
ROUND_DIR.mkdir(parents=True, exist_ok=True)


def number(text, label):
    m = re.search(
        rf"^{re.escape(label)}\s*:\s*([-+]?[0-9]*\.?[0-9]+)",
        text,
        flags=re.MULTILINE,
    )
    if not m:
        raise RuntimeError(f"Missing output field: {label}")
    return float(m.group(1))


df_rows = []

with CSV_PATH.open(newline="") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        df_rows.append(row)

if "equal_budget_payload_bits" not in fieldnames:
    fieldnames = fieldnames + ["equal_budget_payload_bits"]

for row in df_rows:
    if row["mode"] != "C5":
        row["equal_budget_payload_bits"] = ""

for profile, cfg in PROFILES.items():
    for seed in SEEDS:
        print(
            f"RUNNING corrected C5: "
            f"{profile} seed={seed} "
            f"budget={cfg['budget']} bits"
        )

        env = os.environ.copy()
        env["EXPERIMENT_MODE"] = "C5"
        env["SEMANTIC_SEED"] = str(seed)
        env["NUM_NODES"] = "100"
        env["AREA_WIDTH_M"] = "100"
        env["AREA_HEIGHT_M"] = str(cfg["area_height"])
        env["BS_X_M"] = "50"
        env["BS_Y_M"] = str(cfg["bs_y"])
        env["MAX_SENSOR_LINK_DISTANCE_M"] = str(
            cfg["link_radius"]
        )
        env["EQUAL_BUDGET_PAYLOAD_BITS"] = str(
            cfg["budget"]
        )

        result = subprocess.run(
            ["python", "-u", "run_semantic_re_etx.py"],
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        log_path = (
            LOG_DIR
            / f"{profile}_C5_seed{seed}.log"
        )
        log_path.write_text(result.stdout)

        if result.returncode != 0:
            print(result.stdout)
            raise RuntimeError(
                f"{profile} C5 seed={seed} FAILED"
            )

        if (
            "All dynamic minimum-ETX checks PASSED."
            not in result.stdout
        ):
            raise RuntimeError(
                f"{profile} C5 seed={seed} "
                "did not pass simulator checks"
            )

        shutil.copy2(
            "results/minimum_etx_multihop.csv",
            ROUND_DIR
            / f"{profile}_C5_seed{seed}_rounds.csv",
        )

        compression = number(
            result.stdout,
            "Semantic compression ratio",
        )

        replacement = {
            "profile": profile,
            "mode": "C5",
            "seed": str(seed),
            "area_width_m": "100",
            "area_height_m": str(cfg["area_height"]),
            "bs_y_m": str(cfg["bs_y"]),
            "link_radius_m": str(cfg["link_radius"]),
            "calibrated_initial_mean_hops": next(
                row["calibrated_initial_mean_hops"]
                for row in df_rows
                if row["profile"] == profile
                and row["mode"] == "C3"
                and int(row["seed"]) == seed
            ),
            "FND": str(int(number(result.stdout, "FND"))),
            "HND": str(int(number(result.stdout, "HND"))),
            "LND": str(int(number(result.stdout, "LND"))),
            "PDR_percent": str(number(
                result.stdout,
                "PDR (%)",
            )),
            "average_delivered_hops": str(number(
                result.stdout,
                "Average delivered hops",
            )),
            "average_delay_ms": str(number(
                result.stdout,
                "Average delay",
            )),
            "goodput_kbps": str(number(
                result.stdout,
                "Application goodput",
            )),
            "energy_per_delivered_j": str(number(
                result.stdout,
                "Energy/delivered message",
            )),
            "retransmissions": str(int(number(
                result.stdout,
                "Retransmissions",
            ))),
            "generated_messages": str(int(number(
                result.stdout,
                "Generated messages",
            ))),
            "attempted_mean_payload_bits": str(
                compression * 4000.0
            ),
            "event_report_delivery_ratio": str(number(
                result.stdout,
                "Event report delivery ratio",
            )),
            "event_payload_preservation": str(number(
                result.stdout,
                "Event payload preservation",
            )),
            "event_payload_delivery_ratio": str(number(
                result.stdout,
                "Event payload delivery ratio",
            )),
            "within_round_targeting_gap_bits": str(number(
                result.stdout,
                "Within-round targeting gap",
            )),
            "equal_budget_payload_bits": str(
                cfg["budget"]
            ),
        }

        replacement["retries_per_generated"] = str(
            int(replacement["retransmissions"])
            / int(replacement["generated_messages"])
        )

        found = False

        for i, row in enumerate(df_rows):
            if (
                row["profile"] == profile
                and row["mode"] == "C5"
                and int(row["seed"]) == seed
            ):
                df_rows[i] = {
                    key: replacement.get(
                        key,
                        row.get(key, "")
                    )
                    for key in fieldnames
                }
                found = True
                break

        if not found:
            raise RuntimeError(
                f"Could not find original row for "
                f"{profile} C5 seed={seed}"
            )

        print(
            f"SAVED corrected {profile} C5 seed={seed}"
        )

with CSV_PATH.open("w", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames,
    )
    writer.writeheader()
    writer.writerows(df_rows)

print("=" * 80)
print("30 CORRECTED C5 TOPOLOGY RUNS COMPLETE")
print(CSV_PATH)
print("=" * 80)
