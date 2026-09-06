import csv
import os
import re
import shutil
import subprocess
from pathlib import Path

SEEDS = [11, 23, 42, 67, 101, 137, 173, 211, 257, 307]
MODES = ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]
EQUAL_BUDGET_BITS = 1744

ROOT = Path("results/master_validation")
LOG_DIR = ROOT / "logs" / "event_quality"
ROUND_DIR = ROOT / "raw" / "event_quality_rounds"
OUT = ROOT / "statistics" / "event_quality_multiseed_raw.csv"

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


rows = []

print("=" * 80)
print("EVENT-QUALITY MULTI-SEED VALIDATION")
print("=" * 80)

for mode in MODES:
    for seed in SEEDS:
        print(f"RUNNING {mode} seed={seed}")

        env = os.environ.copy()
        env["EXPERIMENT_MODE"] = mode
        env["SEMANTIC_SEED"] = str(seed)
        env["EQUAL_BUDGET_PAYLOAD_BITS"] = str(EQUAL_BUDGET_BITS)

        result = subprocess.run(
            ["python", "-u", "run_semantic_re_etx.py"],
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        log = LOG_DIR / f"{mode}_seed{seed}.log"
        log.write_text(result.stdout)

        if result.returncode != 0:
            print(result.stdout)
            raise RuntimeError(f"{mode} seed={seed} FAILED")

        if "All dynamic minimum-ETX checks PASSED." not in result.stdout:
            raise RuntimeError(f"{mode} seed={seed} validation FAILED")

        shutil.copy2(
            "results/minimum_etx_multihop.csv",
            ROUND_DIR / f"{mode}_seed{seed}_rounds.csv",
        )

        rows.append({
            "mode": mode,
            "seed": seed,
            "event_generated_reports": int(
                number(result.stdout, "Event generated reports")
            ),
            "event_attempted_reports": int(
                number(result.stdout, "Event attempted reports")
            ),
            "event_delivered_reports": int(
                number(result.stdout, "Event delivered reports")
            ),
            "event_report_delivery_ratio": number(
                result.stdout, "Event report delivery ratio"
            ),
            "event_mean_payload_bits": number(
                result.stdout, "Event mean payload bits"
            ),
            "non_event_mean_payload_bits": number(
                result.stdout, "Non-event mean payload bits"
            ),
            "payload_targeting_gap_bits": number(
                result.stdout, "Payload targeting gap bits"
            ),
            "event_payload_preservation": number(
                result.stdout, "Event payload preservation"
            ),
            "event_payload_delivery_ratio": number(
                result.stdout, "Event payload delivery ratio"
            ),
            "pdr_percent": number(
                result.stdout, "PDR (%)"
            ),
            "fnd": int(number(result.stdout, "FND")),
            "hnd": int(number(result.stdout, "HND")),
            "lnd": int(number(result.stdout, "LND")),
        })

        with OUT.open("w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=list(rows[0].keys()),
            )
            writer.writeheader()
            writer.writerows(rows)

        print(f"SAVED {mode} seed={seed}")

print("=" * 80)
print("EVENT-QUALITY 70-RUN VALIDATION COMPLETE")
print(OUT)
print("=" * 80)
