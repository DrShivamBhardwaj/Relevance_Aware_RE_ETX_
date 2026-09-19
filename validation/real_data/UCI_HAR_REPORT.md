# UCI HAR real-IoT sensing validation

## Dataset and partitioning

The experiment uses the UCI Human Activity Recognition Using Smartphones dataset (DOI: 10.24432/C54S4K): 30 human subjects, six activities, and 561 time/frequency features derived from smartphone accelerometer and gyroscope windows. Each subject is treated as one federated client. The original train/test files are recombined and then split 80/20 within each subject using a fixed partition seed so that every client has local train and held-out test data.

## Experimental design

- 30 subject-clients; synthetic multi-hop WSN/IoT communication substrate with four edge gateways.
- 25 federated rounds; 8 clients selected per round.
- Resource-data correlation: 0.0, 0.5, 0.9.
- 10 paired seeds for every method/condition.
- Linear softmax classifier with Top-k update sparsification and error feedback.

## Results at correlation = 0.9

| Method | Accuracy | Macro-F1 | Worst-client acc. | Effective bits | Energy (J) | Rep. JS | Jain |
|---|---:|---:|---:|---:|---:|---:|---:|
| random | 0.8216 +/- 0.0345 | 0.7949 | 0.6479 | 41416156 | 70.83 | 0.0590 | 0.8875 |
| resource | 0.8754 +/- 0.0196 | 0.8724 | 0.6814 | 29651089 | 45.92 | 0.1634 | 0.6518 |
| utility | 0.7188 +/- 0.0303 | 0.6626 | 0.5682 | 42333751 | 72.35 | 0.0763 | 0.5963 |
| proposed | 0.9061 +/- 0.0022 | 0.9060 | 0.7169 | 11638512 | 20.03 | 0.0327 | 0.8318 |

Against the resource-only baseline at correlation 0.9:

- Accuracy: +3.51% relative (+0.0308 absolute).
- Macro-F1: +3.85%.
- Worst-client accuracy: +5.22%.
- Effective communication burden: -60.75% (negative is lower).
- Modeled energy: -56.38%.
- Representation divergence: -79.97%.

Exact paired sign-flip p-values across the 10 matched seeds are stored in `results/uci_har/paired_contrasts.csv`.

## Evidence boundary

This validates the learning side on a real inertial-sensing dataset. Its communication topology is simulated; the Intel Lab experiment separately provides real WSN topology/connectivity plus real sensor readings. Together they test different sides of the claimed cross-layer coupling.