# Controlled phase-resolved M3 power probe

This firmware alternates 20-second idle, CPU busy-work and NullNet radio
broadcast periods, logging phase markers with device ID, phase index and
cycle number. Its purpose is to estimate *incremental total-board power*
from same-node phase differences. It is **not** a sensor-acquisition or
RE-ETX firmware implementation.

Evidence completion requires a linked three-node FIT IoT-LAB power-profile
reservation, raw timestamped OML data, matching serial phase logs,
successful firmware flashes, transition-boundary exclusion and paired
within-node comparisons. This workflow must not claim a calibrated original
energy ledger, independent CPU current or PHY radio-state current.
