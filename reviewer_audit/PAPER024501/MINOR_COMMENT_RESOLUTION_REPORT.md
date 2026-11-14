# PAPER024501 — Minor-comment resolution report

**Scope:** 16 minor reviewer comments. The revised working manuscript is `manuscript_working/PAPER024501_IJWMT_RED_MARKED_EVIDENCE_DRAFT.docx`. Each comment has a separate commit pushed to `review/PAPER024501-audit`.

## Disposition

- **m1: completed — executable mapping verified and Table 4 added.** Location: Section 4.2, Equation (6), Table 4. Evidence: Working DOCX; simulator/semantic_payload.py; Equation (6) OMML audit.
- **m2: completed — comparison table added.** Location: Section 2.2, Table 2. Evidence: Working DOCX, Table 2.
- **m3: completed — depth figure and qualified mechanism discussion added.** Location: Sections 6.5–6.7, Fig. 8, Table 10. Evidence: Fig8_topology_depth.png; Fig8_topology_depth_source.csv; Working DOCX.
- **m4: completed — contribution statement specifies controlled attribution.** Location: Section 1, contribution paragraph. Evidence: Working DOCX.
- **m5: completed — event wording corrected.** Location: Section 3.1. Evidence: Working DOCX.
- **m6: completed — Dijkstra non-negative-cost condition clarified.** Location: Section 4.3. Evidence: Working DOCX; simulator/routing_semantic_re_etx.py.
- **m7: completed — C1/C2 comparison clarified.** Location: Section 6.2, Table 6. Evidence: Working DOCX.
- **m8: completed — subjective wording replaced.** Location: Section 7. Evidence: Working DOCX.
- **m9: completed — long conclusion sentence split.** Location: Section 8. Evidence: Working DOCX.
- **m10: completed — title revised to foreground controlled attribution.** Location: Title. Evidence: Working DOCX.
- **m11: completed — exact percentages and scope limitations added.** Location: Abstract. Evidence: Working DOCX; Section 6.3 numerical comparison.
- **m12: completed — methodological comparison with Arnaiz et al. added.** Location: Section 2.1. Evidence: Working DOCX; verified reference [11].
- **m13: completed — C3 pseudocode and time-complexity derivation added.** Location: Section 4.4, Algorithm 1. Evidence: Working DOCX; run_semantic_re_etx.py; semantic_relevance.py; routing_semantic_re_etx.py.
- **m14: partial — current audit host and smoke test documented; historical 10-seed execution host/package manifest was not preserved.** Location: Section 5.1 and Section 7 evidence boundary. Evidence: minor_revision_environment_2026-11-14.json; 60-round C3 smoke-test output; NEW_EVIDENCE_ARCHIVE_2026-11-14.md.
- **m15: completed — parameter-selection limitation added.** Location: Section 8, Conclusion. Evidence: Working DOCX.
- **m16: completed — verified 2025 and 2026 semantic-communication references added.** Location: Section 2.2 and References [23]–[24]. Evidence: Working DOCX; DOI records 10.3390/s25092823 and 10.3390/s26196124.

## Structural verification

- The working DOCX retains all **43 editable equation elements** and all seven original embedded images.
- Two comparison/mapping tables were added, bringing the total to **10 tables**.
- A new topology-depth figure was added at **600 dpi**, with its source CSV retained.
- The Equation (6) OMML was retained; the executable controller confirms the 3000-bit floor at relevance 0.50 and 4000 bits at 0.85. The byte-aligned mapping is reported in Table 4.
- The stale FIT IoT-LAB identifiers 458478 and 458482 were removed from the working manuscript. The verified partial physical pilot is 458578; it is not represented as full RE-ETX hardware validation.
- All textual additions/changes are red-marked. The original equation inventory and media inventory were checked after editing.

## Remaining qualification

Comment m14 is **partially addressed**, not closed: the current audit host and a separate 60-round C3 smoke test are documented, but the archived ten-seed campaign does not preserve its historical CPU/OS/package manifest. A full reproduction on a documented host is still needed to close that detail.

The report does not imply that any major scientific issue or mandatory editorial requirement is resolved. Receiver-side fidelity, calibrated component energy, full RE-ETX hardware validation, final template pagination, author profiles and declarations remain separate release gates.
