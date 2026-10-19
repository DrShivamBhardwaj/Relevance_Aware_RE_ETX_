import csv
import os
import re
import shutil
import subprocess
from pathlib import Path

SEEDS = [11, 23, 42, 67, 101, 137, 173, 211, 257, 307]

MODES = [
    x.strip().upper()
    for x in os.environ.get(
        "CONTROL_MODES",
        "C1,C2,C3,C4,C5,C6,C7"
    ).split(",")
    if x.strip()
]

EQUAL_BUDGET_BITS = int(
    os.environ.get(
        "EQUAL_BUDGET_PAYLOAD_BITS",
        "1744"
    )
)

ROOT = Path("results/master_validation")
LOG_DIR = ROOT / "logs" / "controls"
ROUND_DIR = ROOT / "raw" / "control_rounds"
RAW_PATH = ROOT / "statistics" / "control_multiseed_raw.csv"

LOG_DIR.mkdir(parents=True, exist_ok=True)
ROUND_DIR.mkdir(parents=True, exist_ok=True)
RAW_PATH.parent.mkdir(parents=True, exist_ok=True)


def find_number(text, label, integer=False):
    pattern = (
        rf"^{re.escape(label)}\s*:\s*"
        rf"([-+]?[0-9]*\.?[0-9]+)"
    )

    match = re.search(
        pattern,
        text,
        flags=re.MULTILINE
    )

    if not match:
        return None

    value = float(match.group(1))

    if integer:
        return int(round(value))

    return value


def parse_summary(text, mode, seed):
    row = {
        "mode": mode,
        "seed": seed,
        "equal_budget_payload_bits": (
            EQUAL_BUDGET_BITS
            if mode == "C5"
            else ""
        ),

        "FND": find_number(
            text,
            "FND",
            integer=True
        ),

        "HND": find_number(
            text,
            "HND",
            integer=True
        ),

        "LND": find_number(
            text,
            "LND",
            integer=True
        ),

        "generated_messages": find_number(
            text,
            "Generated messages",
            integer=True
        ),

        "attempted_messages": find_number(
            text,
            "Attempted messages",
            integer=True
        ),

        "delivered_messages": find_number(
            text,
            "Delivered messages",
            integer=True
        ),

        "channel_drops": find_number(
            text,
            "Channel-related drops",
            integer=True
        ),

        "energy_drops": find_number(
            text,
            "Energy-related drops",
            integer=True
        ),

        "route_drops": find_number(
            text,
            "Route-related drops",
            integer=True
        ),

        "fallback_direct": find_number(
            text,
            "Direct fallback assignments",
            integer=True
        ),

        "PDR_percent": find_number(
            text,
            "PDR (%)"
        ),

        "frame_attempts": find_number(
            text,
            "Frame attempts",
            integer=True
        ),

        "retransmissions": find_number(
            text,
            "Retransmissions",
            integer=True
        ),

        "average_hops": find_number(
            text,
            "Average delivered hops"
        ),

        "average_delay_ms": find_number(
            text,
            "Average delay"
        ),

        "channel_time_s": find_number(
            text,
            "Channel elapsed time"
        ),

        "goodput_kbps": find_number(
            text,
            "Application goodput"
        ),

        "energy_per_delivered_j": find_number(
            text,
            "Energy/delivered message"
        ),

        "average_payload_bits_all_positions":
            find_number(
                text,
                "Average semantic payload bits"
            ),

        "minimum_payload_bits": find_number(
            text,
            "Minimum semantic payload bits",
            integer=True
        ),

        "maximum_payload_bits": find_number(
            text,
            "Maximum semantic payload bits",
            integer=True
        ),

        "payload_reduction_percent":
            find_number(
                text,
                "Payload reduction (%)"
            ),

        "attempted_payload_ratio":
            find_number(
                text,
                "Semantic compression ratio"
            ),

        "semantic_radio_efficiency":
            find_number(
                text,
                "Semantic radio efficiency"
            ),

        "cumulative_energy_j":
            find_number(
                text,
                "Cumulative energy used"
            ),
    }

    ratio = row["attempted_payload_ratio"]

    if ratio is not None:
        row["attempted_mean_payload_bits"] = (
            4000.0 * ratio
        )
    else:
        row["attempted_mean_payload_bits"] = None

    generated = row["generated_messages"]
    retransmissions = row["retransmissions"]

    if generated:
        row["retries_per_generated"] = (
            retransmissions / generated
        )
    else:
        row["retries_per_generated"] = None

    return row


existing = {}

if RAW_PATH.exists():
    with RAW_PATH.open(
        newline=""
    ) as f:
        for row in csv.DictReader(f):
            existing[
                (
                    row["mode"],
                    int(row["seed"])
                )
            ] = row


rows = list(existing.values())

total = len(MODES) * len(SEEDS)
counter = 0

print("=" * 90)
print("DUAL-JOURNAL CONTROL EXPERIMENTS")
print("=" * 90)
print("Modes :", MODES)
print("Seeds :", SEEDS)
print(
    "C5 equal-budget payload:",
    EQUAL_BUDGET_BITS,
    "bits"
)
print("=" * 90)

for mode in MODES:
    for seed in SEEDS:
        counter += 1

        key = (mode, seed)

        if key in existing:
            print(
                f"[{counter:02d}/{total}] "
                f"{mode} seed={seed} "
                f"ALREADY COMPLETE - SKIPPED"
            )
            continue

        print()
        print(
            f"[{counter:02d}/{total}] "
            f"RUNNING {mode}, seed={seed}"
        )

        env = os.environ.copy()
        env["EXPERIMENT_MODE"] = mode
        env["SEMANTIC_SEED"] = str(seed)
        env[
            "EQUAL_BUDGET_PAYLOAD_BITS"
        ] = str(EQUAL_BUDGET_BITS)

        process = subprocess.run(
            [
                "python",
                "-u",
                "run_semantic_re_etx.py",
            ],
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        output = process.stdout

        log_path = (
            LOG_DIR
            / f"{mode}_seed{seed}.log"
        )

        log_path.write_text(output)

        print(output)

        if process.returncode != 0:
            raise RuntimeError(
                f"{mode} seed={seed} FAILED. "
                f"See {log_path}"
            )

        if (
            "All dynamic minimum-ETX checks PASSED."
            not in output
        ):
            raise RuntimeError(
                f"{mode} seed={seed} did not "
                f"pass simulator validation."
            )

        source_csv = Path(
            "results/minimum_etx_multihop.csv"
        )

        target_csv = (
            ROUND_DIR
            / f"{mode}_seed{seed}_rounds.csv"
        )

        shutil.copy2(
            source_csv,
            target_csv
        )

        summary = parse_summary(
            output,
            mode,
            seed
        )

        rows.append(summary)
        existing[key] = summary

        fieldnames = list(
            summary.keys()
        )

        normalized = []

        for item in rows:
            normalized.append({
                key_name: item.get(
                    key_name,
                    ""
                )
                for key_name in fieldnames
            })

        normalized.sort(
            key=lambda r: (
                r["mode"],
                int(r["seed"])
            )
        )

        with RAW_PATH.open(
            "w",
            newline=""
        ) as f:
            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames
            )

            writer.writeheader()
            writer.writerows(
                normalized
            )

        print(
            f"SAVED: {mode} seed={seed}"
        )

print()
print("=" * 90)
print("CONTROL RUNNER COMPLETE")
print("Raw summaries:", RAW_PATH)
print("Per-round files:", ROUND_DIR)
print("Logs:", LOG_DIR)
print("=" * 90)
