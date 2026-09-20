# Consistency audit after held-out editorial revision

Status: PASS.

- Operating point in code and documentation: relay-pressure 5.0, compression-distortion 0.10, V = 0.5.
- Tuning and evaluation seeds are disjoint.
- Two-level cloud influence is corrected and unit-tested.
- Manuscript uses utility-target JS rather than treating the controller target as independent representativeness.
- Intel and HAR independent coverage metrics are reported separately.
- Compression-matched controls and the FedCG-adapted comparator are present in final real-data comparisons.
- UCI HAR uses the overlap-safe blocked within-client holdout and is not presented as unseen-subject evaluation.
- Adverse Intel/HAR network trade-offs are retained in the manuscript and frozen-table tests.
- Frozen tables are hash-checked.
- Python test suite: 13/13 passing.
- Final HFL campaign: 1,000 runs; ns-3.47 replay: 400 runs.