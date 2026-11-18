# M14 Original Simulator Provenance

The original 70-run control campaign is attributable to an Apple M1 MacBook Air (MacBookAir10,1), 8 GB RAM, macOS Tahoe 26.6.2 by reconstruction from local and archived records. The archived software snapshot lists Python 3.14.7, NumPy 2.4.6, pandas 3.0.5, SciPy 1.17.1 and Matplotlib 3.11.1.

| Evidence | Finding |
|---|---|
| Local shell history | The history records creation and execution of run_control_multiseed.py, using tee to save control_multiseed_70runs.log, then packaging of the control_rounds directory used for the submission archive. |
| Runner identity | The runner reconstructed from the shell history matches the frozen Git runner byte for byte after normalising line endings and the final newline. Both have 402 lines. |
| Run identity | All 70 mode–seed pairs in the round archive match all 70 rows of the control summary. The 70 round files carry the connected Mac account’s owner and group and have modification times from 2026-09-05 17:24:34 to 17:43:59 UTC. |
| Host hardware | The connected machine reports Apple M1, MacBookAir10,1 and 8,589,934,592 bytes of memory. |
| OS on the study date | The same machine’s installation history records macOS Tahoe 26.6.2 installed 31 August 2026, before the archive timestamps, with macOS 27 installed 18 September 2026. |
| Software | The frozen tag’s results/master_validation/python_version.txt and requirements_snapshot.txt list the reported versions. |

The original tee log and a contemporaneous stand-alone hardware manifest were unavailable during the audit. Hardware and OS attribution therefore comes from the converging records above. The November Mac audit, its 60-round smoke test and the Linux Appendix D experiments are separately documented.

## Frozen inputs

- Git tag `submission-ready-v1` resolves to `b5d5ac75c981b1eff0171a8cb885ef5764183d85`.
- Runner `run_control_multiseed.py` SHA-256 `04404ab7d668600853705e2d925ef1f66c75587d4576a8f91b6d6d1da0291eaf`.
- Round-file archive SHA-256 `e480698cc11cfa5e0525ce293de9eda034042ca4e61006f5d33de03df22bca5f`.
- Control-study summary SHA-256 `d21bbca98204b80f3ecfaa4592e4e89073b3278d2afb4c2a1bface61a6f7306d`.
