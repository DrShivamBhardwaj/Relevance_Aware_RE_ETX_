# IJWMT response notes

### E1 · Editable equations

The eight displayed equations use editable Word equations centred in full-width borderless three-column tables. Their labels run from (1) to (8) and are right-aligned. Inline formula objects remain editable.

Manuscript location. Equations (1)–(8) and the inline equations. All 43 Word equation objects were retained.

### E2 · Table format and numbering

Tables 1–22 are numbered in sequence, with repeating headers. Summary tables use horizontal rules. Tabulated measurement records retain full borders, and the complete seed-level outputs and hardware logs are supplied separately.

Manuscript location. Tables 1–22 and Data and code availability.

### E3 · Figure quality

All 11 figures are numbered in sequence. The minimum effective resolution at the size used in Word is about 420 dpi. We retained the original proportions and checked the rendered figures for legibility.

Manuscript location. Fig.1.–Fig. 11 and Word media audit.

### E4 · Grouped citations

Grouped citations use compact square brackets. We also ordered the bibliography by first citation and synchronised the in-text numbers with the reference entries.

Manuscript location. In-text citations and all 28 references.

### E5 · Bibliography verification

We checked the original 27 entries against publisher, standards or bibliographic records. We standardised the conference name in [2], checked the RFC 6550 authorship and editor credits [5], and recorded Holm’s DOI [26]. The ICT Express article [24] is listed as in press. We also checked the author copy and bibliographic record for the added dissemination study [28]. All 28 references have distinct DOIs and are cited in the text.

Manuscript location. All 28 references and their in-text citations.

### E6 · ORCID placement

Each author’s ORCID iD appears on its own line below their affiliation and email in the author-identified manuscript and the editorial title page.

Manuscript location. Author information following the title.

### E7 · Academic titles

The title block lists names, affiliations, email addresses and ORCID iDs. Academic roles appear in the Authors’ Profiles section where verified.

Manuscript location. Author information following the title, and Authors’ Profiles at the end.

### E8 · Author profiles

The three biographies appear beside the supplied portraits. Two portraits exceed 300 dpi at the displayed size. The portrait cropped from an event poster is about 86 dpi and is provisional. The corresponding author has approved his biography. A recent passport-style portrait of at least 300 dpi and the two coauthors’ biography approvals are still needed.

Manuscript location. Authors’ Profiles at the end of the manuscript.

### E9 · Journal format

We formatted the manuscript against the supplied IJWMT paper and preparation instructions. The revised files use A4, Times New Roman, single spacing, per-author details, the nine-field declaration block, appendices and an end-of-paper author profile section. The package includes the author-identified marked paper, an editorial title page and anonymous review copies.

Manuscript location. Anonymized Word files, separate title page, supplementary data and accompanying upload guide.

### E10 · Declarations

The title page records all nine declaration fields. The corresponding author confirmed the contribution roles: Conceptualization, Methodology, Software, Formal analysis, Visualization, and Writing – original draft. The coauthors are listed under Supervision. The declaration records no conflicts and no financial support. The editable disclosure specifies how ChatGPT and Grammarly were used. Final author approval and consent to submit remain pending.

Manuscript location. Separate title page and All the Declarations and Statements in the named manuscript.

### E11 · Red marks and detailed response

Red marks identify changes in the marked manuscript. Each response specifies the manuscript location so that the reviewer can find the revision.

Manuscript location. Red-marked manuscript and this response.

### M1 · Cost of neighbour context

We evaluated the overhead in two 100-node simulation studies. In the first study, the original centralised estimator was retained and each context broadcast was charged to its sender and all live neighbours. The baseline C1 mean LND and energy per delivered report were 1268.6 rounds and 1.147 mJ. At 1000 context bits per broadcast, C3 had 1297.6 rounds and 1.065 mJ per delivered report. At 2000 bits, it had 1039.9 rounds and 1.533 mJ. The reversal therefore occurs within the tested scenarios. The model assumes successful context reception, with zero additional MAC header and retry charge. A separate 20-run simulator study used receiver-cached observations and varied context size and assumed reception probability. Three-node Cooja and FIT IoT-LAB M3 pilots tested context transport. The modelled reversal is conditional on the broadcast assumptions, and the pilots establish transport feasibility at the tested scale.

Manuscript location. Sections 3.1–3.2 and 7, Appendix A Table 14, Appendix B Tables 16 and 18, and Appendix C Tables 19–20.

### M2 · Methodological contribution and sensitivity

We completed 90 matched-seed runs for a local sensitivity study covering the temporal and spatial weights, both payload thresholds and the routing energy weight. The baseline mean HND is 870.1 rounds, compared with 888.6 at temporal weight 0.80. The revised text identifies the retained settings and explains that changing the thresholds also changes the offered bit budget. We frame the methodological contribution as controlled attribution through C5 and C6. The sensitivity study supports local interpretation of the settings. Global optimality and performance relative to nonlinear designs remain outside the evaluated scope.

Manuscript location. Sections 1, 6.1 and 8, Fig. 9, and Appendix A Table 13.

### M3 · Receiver utility

We implemented and tested a payload-dependent receiver codec in 30 additional 300-round simulations. It allocates signed Q8.8 samples from a 160-sample history according to the available payload and reconstructs missing samples by interpolation. On 140,043 common reports, C3/C5/C6 mean RMSE was 0.104355/0.086526/0.102546 and event F1 was 0.904077/0.922417/0.906325. Higher C3 RMSE and lower C3 event F1 were significant against both controls (Holm p = 0.0078125 for each comparison). We report this result for the specified history codec and common delivery condition. The original 16-bit scalar results are retained.

Manuscript location. Sections 6.8 and 8, Appendix D Table 21, and the supplementary experiment archive.

### M4 · Unmodelled energy

We supplemented the radio ledger with 60 paired battery-state reruns using explicit additional energy scenarios. Mean LND for C1/C3 was 1268.6/2636.4 rounds without additional charges, 1042.9/1862.7 in the moderate scenario, and 725.9/1047.7 in the high scenario. The M3 workload measurements and context pilot report whole-board power. The physical measurements are limited to the observed workload phases. Estimating independent energy coefficients for operations and MAC states would require separately timed and calibrated measurements.

Manuscript location. Sections 3.2, 6.9 and 7, Appendix A Table 15, and Appendix B Table 18.

### M5 · Deep-topology timing

We recorded event onset and first delivery in 60 runs across three topology depths, using a simulated sampling clock and a serialised service queue. Figures 10–11 also report within-round service lag and selected route hops. At the primary 5 s period, the deep-profile first-arrival difference was +0.807 s for C3−C5 (95% CI [−5.010, 6.625], Holm p = 1.000). The deadline-miss difference was −19.389 percentage points (95% CI [−39.799, 1.021], Holm p = 0.78125). Undelivered episodes count as misses. Neither comparison establishes event staleness as the cause of the deep-topology lifetime result. The archive includes 2 s and 10 s sensitivity cases.

Manuscript location. Section 6.7, Figs. 10–11, Appendix B Table 17, Appendix D Table 22 and event_timestamps_simulated.csv.

### m1 · Payload mapping at the threshold

The review calculation omits the middle branch’s max operator. At v = 0.50, the correct ratio is max(0.75, 0.25 + 0.75 × 0.50) = 0.75, giving L = 3000 bits after byte alignment. We kept Equation (6) unchanged and inserted the full payload map at relevance values 0.0, 0.1, …, 1.0. Altering the mathematical rule to 2500 bits would contradict the actual implementation.

Manuscript location. Section 4.2; Appendix A Table 11; verified C/Python payload-rule parity.

### m2 · Statistical and semantic relevance

Section 2.2 distinguishes statistical novelty in sensor observations from semantic utility for a receiver or task. Table 12 compares the two approaches by inputs, outputs, decoder, evaluation metric and intended scope.

Manuscript location. Section 2.2; Appendix A Table 12.

### m3 · Equal-budget mechanism

We expanded the discussion of how fragmentation and forwarding workload affect the equal-budget comparison. Fig. 8 shows C3 and C5 mean HND and LND across the three profiles. Appendix B adds matched report timing and selected-hop comparisons. The results support a mixed lifetime interpretation across depth profiles.

Manuscript location. Sections 6.5 and 6.7, Tables 6 and 8, Fig. 8, and Appendix B Table 17.

### m4 · Introduction contribution

The Introduction now specifies the main contribution: a controlled comparison that separates the effect of sending fewer bits from the effect of assigning those bits according to relevance.

Manuscript location. Introduction, added contribution paragraph.

### m5 · Gaussian-event wording

The sentence now says that observations include a spatial Gaussian component when an event occurs. Amplitude, width, activation probability and duration are unchanged.

Manuscript location. Section 3.1; mathematical symbols preserved.

### m6 · Dijkstra wording

We now state the technical condition directly: non-negative link costs satisfy the edge-weight requirement of Dijkstra’s algorithm. The routing method and the once-per-round calculation are unchanged.

Manuscript location. Section 4.3; Equation (7) unchanged.

### m7 · C1 and C2 wording

The revised text says that C1 and C2 exhibit negligible differences across the metrics in Table 4. No equality claim or additional test was introduced.

Manuscript location. Section 6.2; Table 4 unchanged.

### m8 · Topology discussion wording

The discussion identifies which outcomes vary with initial hop depth and explains why the equal-budget lifetime results are mixed.

Manuscript location. Section 7.

### m9 · Conclusion readability

The Conclusion now uses separate sentences for the history-codec result, the timing result and the scope of the prototype evidence. It also identifies the further evidence needed for broader deployment claims.

Manuscript location. Section 8 and the revised final limitations.

### m10 · Revised title

The revised title identifies traffic reduction and relevance-directed allocation as the two effects tested and names the RE-ETX routing substrate.

Manuscript location. Revised title page.

### m11 · Abstract scope and exact effect sizes

The abstract reports reductions of 54.0% in mean delay and 54.2% in communication energy per delivered report. It states that the principal simulation uses centrally available observations and omits context-exchange, sensing and control energy. It also distinguishes the original scalar diagnostic from the separate history-codec results.

Manuscript location. Abstract.

### m12 · Comparison with Arnaiz et al.

The Introduction and Section 2.1 now compare the control variables and evaluation targets directly. Arnaiz et al. [11] adapt sensing and prediction under node-level energy constraints and assess monitoring accuracy. Our study adjusts the report length after an observation is generated and uses matched-bit and shuffled-length controls to isolate the allocation effect.

Manuscript location. Introduction and Section 2.1; Reference [11].

### m13 · Pseudocode and complexity

Algorithm 1 sets out the C3 execution sequence from observation generation and relevance scoring through route construction, forwarding and energy accounting. Section 4.4 explains the O(N²) dense graph representation, spatial median processing, shortest-path search and packet-forwarding workload separately.

Manuscript location. Section 4.4, Algorithm 1 and accompanying complexity analysis.

### m14 · Original simulator environment

Section 5.1 now reports the environment reconstructed for the original campaign: Apple M1 MacBook Air (MacBookAir10,1), 8 GB RAM, macOS Tahoe 26.6.2. The archived software snapshot lists Python 3.14.7, NumPy 2.4.6, pandas 3.0.5, SciPy 1.17.1 and Matplotlib 3.11.1. We linked the local launch command to the frozen runner and matched all 70 archived mode–seed pairs to the study summary. The Mac’s installation history establishes the OS version for that date. The November audit and the Linux Appendix D runs are described separately.

Manuscript location. Section 5.1, the archived software snapshot and M14 Original Simulator Provenance.

### m15 · Parameter limits in conclusion

The Conclusion identifies the weights and thresholds as design settings examined by a local sensitivity study. Broader validation would require independent seeds and additional sensing, link and deployment conditions.

Manuscript location. Section 8; Appendix A Table 13.

### m16 · Recent literature and exchange overhead

Section 2.2 compares two recent studies with our report-length controller: Yang et al. (Sensors, 2025) on task-oriented adaptation in WSNs and Kaya et al. (Sensors, 2026) on prediction-aided semantic coding of sensor streams. Section 7 now also cites Panta et al. [28] for the radio cost of periodic neighbour advertisements. That work gives context for the overhead discussion; our sensitivity experiments supply the study-specific estimates.

Manuscript location. Sections 2.2 and 7; References [21], [22] and [28].
