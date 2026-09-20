# Experimental evidence summary

This file summarizes the evidence base after the held-out editorial revision.

## Completed evidence layers

- Synthetic correlated system/data heterogeneity.
- Intel Berkeley Lab real sensing data with measured WSN connectivity.
- UCI HAR real inertial sensing with an overlap-safe blocked within-client holdout.
- Compression-matched random/resource/utility controls.
- FedCG-adapted gradient-diversity/capability comparator.
- Disjoint tuning and held-out evaluation seeds.
- Exact paired sign-flip tests, Holm corrections, bootstrap intervals, and effect sizes.
- ns-3.47 IEEE 802.15.4/LR-WPAN replay.
- 13/13 automated tests, including corrected two-level cloud-influence accounting.

## Campaign size

The revised campaign executes 1,000 HFL simulations: 240 tuning-grid runs, 540 held-out real-data comparison runs, 100 held-out ablation runs, and 120 held-out synthetic runs. A separate 400-run ns-3.47 campaign replays held-out synthetic traffic.

## Frozen operating point

Relay-pressure coefficient 5.0, compression-distortion coefficient 0.10, drift V = 0.5.

## Intel held-out result at correlation 0.9

Proposed: RMSE 1.7348 C; MAE 0.7790 C; effective traffic 0.992 Mbit; modeled energy 3.482 J; maximum relay energy 0.0969 J; utility-target JS 0.0118; temperature-coverage JS 0.00375.

Resource-adaptive: RMSE 1.7285 C; effective traffic 0.916 Mbit; modeled energy 3.307 J; maximum relay energy 0.0902 J; utility-target JS 0.0843.

FedCG-adapted: RMSE 1.7362 C; effective traffic 0.980 Mbit; modeled energy 3.454 J; maximum relay energy 0.0964 J; utility-target JS 0.0911.

Interpretation: the proposed method does not dominate the matched resource control. Its distinguishing gain is utility-target alignment, while its independent temperature-coverage metric is worse.

## UCI HAR held-out result at correlation 0.9

Proposed: accuracy 0.8867; Macro-F1 0.8827; effective traffic 11.253 Mbit; modeled energy 19.20 J; maximum relay energy 1.242 J; utility-target JS 0.0275; class-coverage JS 0.000064.

Resource-adaptive: accuracy 0.8751; effective traffic 8.872 Mbit; modeled energy 14.34 J; maximum relay energy 0.170 J.

FedCG-adapted: accuracy 0.8760; effective traffic 9.311 Mbit; modeled energy 15.34 J; maximum relay energy 0.643 J.

Interpretation: proposed improves held-out accuracy over both matched comparators, but at higher traffic, total energy, and relay-hotspot cost. Independent class-coverage differences are small and not statistically significant.

## Compression attribution

Relative to proposed-fixed-50%, adaptive fidelity reduces effective traffic by 58.2% on Intel and 64.0% on HAR. Large communication savings must therefore not be attributed to client scheduling alone.

## Evidence boundary

No physical IEEE 802.15.4 mote/MCU experiment is claimed. Downlink global-model dissemination and scheduler metadata are not fully priced. The FedCG-adapted method is a favorable adaptation, not an exact reproduction of the original FedCG system model.