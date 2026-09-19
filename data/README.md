# External datasets

This directory now includes the compressed/raw dataset archives needed to reproduce the executed real-data experiments. The extracted UCI HAR folder remains intentionally excluded because it duplicates the archive and unnecessarily expands the repository size.

## Intel Berkeley Research Lab WSN

Source: https://db.csail.mit.edu/labdata/labdata.html

Committed files in `data/intel_lab/`:

- `data.txt.gz`
- `mote_locs.txt`
- `connectivity.txt`

The experiment records SHA-256 checksums in `results/intel_lab/run_manifest.json`.

## UCI Human Activity Recognition Using Smartphones

Dataset DOI: `10.24432/C54S4K`

Source: https://archive.ics.uci.edu/dataset/240/human+activity+recognition+using+smartphones

Committed file:

- `data/uci_har/har.zip`

Before running `run_har_experiment.py`, extract the nested `UCI HAR Dataset.zip` contained in `har.zip` so that `data/uci_har/unpacked/UCI HAR Dataset/` contains the train/test files. The current local machine already has the extracted copy, but the extracted duplicate is not committed.

The experiment records the archive SHA-256 checksum in `results/uci_har/run_manifest.json`.
