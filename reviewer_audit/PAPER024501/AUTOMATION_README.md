# PAPER024501 — unattended, evidence-gated revision workflow

The local user LaunchAgent org.paper024501.checkpoints invokes the existing
checkpoint_sync.sh every 1200 s and once when loaded. The Mac has to remain
powered on and connected; the LaunchAgent cannot run while the Mac is off.

What now runs without invoking ChatGPT:
- Archived result and 90-run parameter statistical consistency checks
- Recomputed statistical tables from 40+40 diagnostic receiver, 60 energy,
  and 15 Cooja transport trials
- Scientific validation memorandum refresh if the underlying evidence changes
- Red-marked IJWMT evidence draft from ~/Downloads/PAPER024501-1.docx
  and the authentic IJWMT guide and template in ~/Downloads
- Machine verification of the original editable Equation (6) safeguards;
  0.0...1.0 payload table, with L(0.50)=3000 bits
- Preservation tests for 43 editable equations, 8 original tables and
  7 figure media parts
- A 32-point reviewer response evidence draft (not yet page-specific)
- Automated 19-page LibreOffice PDF preflight with effective image-DPI
  report; full human layout review remains pending
- Rechecking/archiving one single M3 power-profile experiment, 458482,
  from an already persisted experiment ID, with no duplicate reservation
- Git commits and push retry of changed evidence on the review branch

Cost and scientific gates:
- Do NOT submit more hardware reservations automatically, and do NOT
  submit revised manuscript to journal without source-accurate review.
- Receiver DCT RMSE/F1 is a newly defined diagnostic codec, NOT the
  paper's missing original source codec.
- The 60-run node-energy scenarios rely on assumed overhead values.
  M3 consumption samples may calibrate observed device-level power of
  the NullNet diagnostic but cannot by themselves infer sensing, CPU,
  ACK and RE-ETX routing energy.
- The Cooja and FIT IoT-LAB proof verifies fragmented NullNet transport;
  parent selection, distributed relevance and the full RE-ETX policy are
  not yet ported and must not be claimed as validated.
- Coauthor ORCIDs, photos, verified biographies, all nine declarations,
  DOI citations and journal line/page/visual compliance remain editorial
  release gates.
- Always preserve negative C3/C5/C6 fidelity findings.

Audit documents: unattended_release_status.json,
revision_gate_status.json, manuscript_working/render_preflight.json,
hardware_power_calibration/power_archive_audit.json and
PAPER024501_validation_memorandum.md.
