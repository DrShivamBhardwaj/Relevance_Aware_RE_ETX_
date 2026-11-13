# PAPER024501 controlled Cooja payload transport diagnostic

This is a new Contiki-NG NullNet/CSMA **transport and reassembly probe**, not a
port of RE-ETX routing, energy-based parent selection, or receiver waveform codec.
It tests the source's guarded payload bit rule and delivery of up to 4000-bit
application reports as up to eight short 802.15.4 frames. No physical testbed
claims follow from Cooja. Logs explicitly distinguish TX requests from
RX_COMPLETE reassembled reports.

The three-mote topology and random seed derive from the installed Contiki-NG
stock NullNet configuration, with the source/Makefile replaced by this probe.
Run headless with Cooja's Gradle runner, with GNU Make 4+.
