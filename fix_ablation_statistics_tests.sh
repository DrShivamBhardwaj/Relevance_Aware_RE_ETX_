#!/bin/bash

set -e

echo "=============================================="
echo "PATCHING STATISTICAL TEST HANDLING"
echo "=============================================="

python3 - <<'PY'
from pathlib import Path

p = Path("generate_ablation_statistics_tests.sh")

text = p.read_text()

text = text.replace(
"""    pooled = np.sqrt(
        (
            (na-1)*np.var(a, ddof=1)
            +
            (nb-1)*np.var(b, ddof=1)
        )
        /
        (na+nb-2)
    )

    return (
        np.mean(a)-np.mean(b)
    ) / pooled
""",
"""    pooled = np.sqrt(
        (
            (na-1)*np.var(a, ddof=1)
            +
            (nb-1)*np.var(b, ddof=1)
        )
        /
        (na+nb-2)
    )

    if pooled == 0:
        return np.nan

    return (
        np.mean(a)-np.mean(b)
    ) / pooled
"""
)

text = text.replace(
"""        stat,p=ttest_ind(
            x,
            y,
            equal_var=False
        )
""",
"""        if (
            np.std(x, ddof=1) == 0
            and np.std(y, ddof=1) == 0
        ):
            stat = np.nan
            p = np.nan
        else:
            stat,p=ttest_ind(
                x,
                y,
                equal_var=False
            )
"""
)

p.write_text(text)

print("Statistical handling patched")

PY

echo "DONE"

