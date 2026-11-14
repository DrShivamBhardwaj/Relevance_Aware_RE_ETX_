# PAPER024501 — Draft point-by-point revision response

**NOT FOR SUBMISSION: scientific gates and author confirmation incomplete.**

The minor-comment responses below record changes verified in the current working DOCX. They remain draft responses until the five major scientific issues and eleven mandatory editorial requirements are closed and the final journal-template, pagination and visual checks are complete.

## Major comments

### M1. Uncharged central neighbour context exchange
**Proposed response:** Analytical per-exchange and report-normalized energy bounds; full distributed energy/network evaluation pending.
**Revised location:** Pending final manuscript page and paragraph check.
**Evidence/verification:** Pending release-gate confirmation.

### M2. Insufficient weight/threshold sensitivity
**Proposed response:** 90 executed network runs with 10 paired seeds and Holm-corrected output; no global optimum claim.
**Revised location:** Pending final manuscript page and paragraph check.
**Evidence/verification:** Pending release-gate confirmation.

### M3. Missing receiver reconstruction or event F1
**Proposed response:** Blocked until documented source codec, receiver decoder and timestamped packet records exist.
**Revised location:** Pending final manuscript page and paragraph check.
**Evidence/verification:** Pending release-gate confirmation.

### M4. Missing sensing, computation, routing-control and idle energy
**Proposed response:** Analytical per-generated-report sensitivity; full node-level ledger and lifetime reruns pending.
**Revised location:** Pending final manuscript page and paragraph check.
**Evidence/verification:** Pending release-gate confirmation.

### M5. Ambiguous deep-topology mechanisms
**Proposed response:** Paired 3-profile contrasts generated; packet-level information age/staleness not measured.
**Revised location:** Pending final manuscript page and paragraph check.
**Evidence/verification:** Pending release-gate confirmation.
## Minor comments

### m1. Equation (6) versus 3000 bits at v=0.50
**Response:** Equation (6) was checked against the editable OMML expression and the executable controller. The existing piecewise safeguard is retained: for 0.50 ≤ v < 0.85, the ratio is floored at 0.75, so L(0.50) = 3000 bits; at v = 0.85 the full 4000-bit payload is selected. Table 4 reports the executable, byte-aligned mapping at 0.1 increments. The reviewer’s 2500-bit result follows only if the max(0.75, …) safeguard is omitted.
**Revised location:** Section 4.2, Equation (6), Table 4. Page number pending final pagination.
**Evidence/verification:** Equation (6) OMML retained; equation count remains 43; values generated from simulator/semantic_payload.py.
**Disposition:** RESOLVED.

### m2. Statistical novelty versus semantic information distinction
**Response:** A new comparison table separates statistical novelty from semantic communication by definition, calculation, transmission action, receiver requirement and evaluation metric. The manuscript now states that the proposed controller is a statistical novelty-to-payload rule, not a semantic encoder/decoder system.
**Revised location:** Section 2.2, Table 2. Page number pending final pagination.
**Evidence/verification:** Working DOCX, Table 2; citations [15,16,19,20,23,24].
**Disposition:** RESOLVED.

### m3. Expand C3 versus C5 deep topology discussion
**Response:** The discussion now distinguishes the persistent event-payload targeting effect from its topology-dependent network consequences. Fig. 8 plots HND, LND, PDR and energy per delivered report for C3 and equal-budget C5 across the three archived route-depth profiles. The deep-profile LND reversal is discussed as a plausible hop-weighted framing/retry-cost mechanism, not as proven relevance staleness; the absence of per-report hop-weighted energy decomposition is stated.
**Revised location:** Sections 6.5–6.7, Fig. 8 and Table 10. Page number pending final pagination.
**Evidence/verification:** 600-dpi Fig8_topology_depth.png and source CSV; values copied from the archived ten-seed topology table.
**Disposition:** RESOLVED.

### m4. Contributions too vague
**Response:** The contribution statement now identifies controlled attribution as the principal contribution and names the equal-budget fixed and shuffled-allocation controls used to separate traffic-volume effects from relevance-directed allocation.
**Revised location:** Section 1, contribution paragraph. Page number pending final pagination.
**Evidence/verification:** Revised working DOCX.
**Disposition:** RESOLVED.

### m5. Section 3.1 'Observations add'
**Response:** The sentence now reads: “A spatial Gaussian event of amplitude 3 and width 18 m is superimposed on the observations.”
**Revised location:** Section 3.1. Page number pending final pagination.
**Evidence/verification:** Revised working DOCX; embedded equations preserved.
**Disposition:** RESOLVED.

### m6. Section 4.3 Dijkstra wording
**Response:** The routing description now states that the strictly positive edge costs satisfy the non-negative-weight condition required by Dijkstra’s algorithm.
**Revised location:** Section 4.3. Page number pending final pagination.
**Evidence/verification:** Revised working DOCX; implementation checked in simulator/routing_semantic_re_etx.py.
**Disposition:** RESOLVED.

### m7. Section 6.2 imprecise C1/C2 wording
**Response:** The comparison now states that C1 and C2 exhibit negligible differences across all reported metrics in Table 6.
**Revised location:** Section 6.2, Table 6. Page number pending final pagination.
**Evidence/verification:** Revised working DOCX.
**Disposition:** RESOLVED.

### m8. Section 7 'useful' wording
**Response:** The subjective term “useful” has been replaced with “informative”.
**Revised location:** Section 7. Page number pending final pagination.
**Evidence/verification:** Revised working DOCX.
**Disposition:** RESOLVED.

### m9. Section 8 long sentence
**Response:** The long conclusion sentence has been split into two sentences. Receiver reconstruction and downstream task utility are separated from the additional distributed-context and full-energy-accounting requirements.
**Revised location:** Section 8. Page number pending final pagination.
**Evidence/verification:** Revised working DOCX.
**Disposition:** RESOLVED.

### m10. Title lacks attribution contribution
**Response:** The title has been revised to foreground the controlled attribution design: “Isolating Traffic Reduction from Relevance-Directed Allocation: A Controlled Evaluation of Adaptive Payload Length over RE-ETX Routing in WSNs”.
**Revised location:** Title. Page number pending final pagination.
**Evidence/verification:** Revised working DOCX.
**Disposition:** RESOLVED.

### m11. Abstract limitations and numerical precision
**Response:** The abstract now reports the exact reductions of 54.0% in mean delay and 54.2% in communication energy per delivered report. It also identifies the central-neighbour-context assumption, the excluded sensing/computation/control/ACK/idle energy components, and the absence of receiver-side reconstruction and downstream task-utility evidence.
**Revised location:** Abstract. Page number pending final pagination.
**Evidence/verification:** Percentages agree with the results text; revised working DOCX.
**Disposition:** RESOLVED.

### m12. Arnaiz et al. comparison
**Response:** The related-work discussion now compares control granularity and evaluation design. Arnaiz et al. coordinate sampling-period adaptation with dual prediction and evaluate monitoring accuracy under a battery-life target; the present method retains the sampling process and maps statistical novelty to raw report length, without an implemented source decoder.
**Revised location:** Section 2.1. Page number pending final pagination.
**Evidence/verification:** Reference [11] verified against DOI 10.1016/j.vlsi.2023.102097; revised working DOCX.
**Disposition:** RESOLVED.

### m13. Algorithm pseudocode and complexity
**Response:** Algorithm 1 now gives the C3 execution flow from sensing and relevance calculation through payload selection, RE-ETX graph construction, Dijkstra routing, fragmentation, retries and energy/counter updates. The accompanying per-round complexity expression accounts for dense neighbour scans, heap-based Dijkstra and per-report multi-hop frame attempts; the O(N²) memory bound is retained.
**Revised location:** Section 4.4, Algorithm 1 and complexity paragraph. Page number pending final pagination.
**Evidence/verification:** Algorithm cross-checked against run_semantic_re_etx.py, semantic_relevance.py and routing_semantic_re_etx.py.
**Disposition:** RESOLVED.

### m14. Hardware and simulation environment
**Response:** The current revision-audit host and software stack are now recorded: Apple M1, 8 GB RAM, macOS 27.2, Python 3.14.7 and the listed scientific packages. A 60-round C3 smoke test is documented separately from the archived ten-seed results. The historical host/package manifest for those archived runs was not retained; therefore this requirement remains partially addressed until the full archived campaign is reproduced on a fully documented host.
**Revised location:** Section 5.1; supplementary evidence boundary in Section 7. Page number pending final pagination.
**Evidence/verification:** minor_revision_environment_2026-11-14.json; FIT IoT-LAB experiment 458578 archive.
**Disposition:** PARTIAL.

### m15. Conclusion parameter-selection limitation
**Response:** The conclusion now states that the current study does not establish a global optimum for the 0.6/0.4 relevance weights, 0.50/0.85 payload safeguards or 0.25 routing-energy weight, and calls for broader sensitivity analysis using independent seed sets.
**Revised location:** Section 8, Conclusion. Page number pending final pagination.
**Evidence/verification:** Revised working DOCX.
**Disposition:** RESOLVED.

### m16. Recent semantic communication references
**Response:** Two recent studies have been added: Yang et al. (2025) on scalable semantic adaptive communication for WSN task requirements, and Kaya et al. (2026) on prediction-aided adaptive semantic communication for IoT sensor streams under outdated channel-state information. Their DOI metadata and stated methods were checked before citation.
**Revised location:** Section 2.2 and References [23]–[24]. Page number pending final pagination.
**Evidence/verification:** DOIs 10.3390/s25092823 and 10.3390/s26196124 verified against publisher records.
**Disposition:** RESOLVED.

### R1. Editable consecutively numbered equations
**Proposed response:** Verify and apply formatting requirement in camera-ready manuscript.
**Revised location:** Pending final manuscript page and paragraph check.
**Evidence/verification:** Pending release-gate confirmation.

### R2. Three-line primary tables, bordered raw tables
**Proposed response:** Verify and apply formatting requirement in camera-ready manuscript.
**Revised location:** Pending final manuscript page and paragraph check.
**Evidence/verification:** Pending release-gate confirmation.

### R3. Figures >=300 dpi
**Proposed response:** Verify and apply formatting requirement in camera-ready manuscript.
**Revised location:** Pending final manuscript page and paragraph check.
**Evidence/verification:** Pending release-gate confirmation.

### R4. Consolidated bracketed citations
**Proposed response:** Verify and apply formatting requirement in camera-ready manuscript.
**Revised location:** Pending final manuscript page and paragraph check.
**Evidence/verification:** Pending release-gate confirmation.

### R5. Reference existence, uniqueness and citation cross-audit
**Proposed response:** Verify and apply formatting requirement in camera-ready manuscript.
**Revised location:** Pending final manuscript page and paragraph check.
**Evidence/verification:** Pending release-gate confirmation.

### R6. ORCID iDs after names/emails
**Proposed response:** Verify and apply formatting requirement in camera-ready manuscript.
**Revised location:** Pending final manuscript page and paragraph check.
**Evidence/verification:** Pending release-gate confirmation.

### R7. Remove author job titles below title
**Proposed response:** Verify and apply formatting requirement in camera-ready manuscript.
**Revised location:** Pending final manuscript page and paragraph check.
**Evidence/verification:** Pending release-gate confirmation.

### R8. Verified biographies and photographs
**Proposed response:** Verify and apply formatting requirement in camera-ready manuscript.
**Revised location:** Pending final manuscript page and paragraph check.
**Evidence/verification:** Pending release-gate confirmation.

### R9. Exact IJWMT template/declarations
**Proposed response:** Verify and apply formatting requirement in camera-ready manuscript.
**Revised location:** Pending final manuscript page and paragraph check.
**Evidence/verification:** Pending release-gate confirmation.

### R10. Nine complete journal statements or N/A
**Proposed response:** Verify and apply formatting requirement in camera-ready manuscript.
**Revised location:** Pending final manuscript page and paragraph check.
**Evidence/verification:** Pending release-gate confirmation.

### R11. Red changes and detailed response
**Proposed response:** Verify and apply formatting requirement in camera-ready manuscript.
**Revised location:** Pending final manuscript page and paragraph check.
**Evidence/verification:** Pending release-gate confirmation.
