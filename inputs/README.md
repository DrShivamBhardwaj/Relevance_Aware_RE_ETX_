# Experiment inputs

- `../validation/cooja/design.json`: revision-2 design, seeds, policies and stress cases. Its status records the plan at creation; completed execution is recorded in `../results/cooja_v2/status.json`.
- `../historical/config.py`: historical geometry, radio, energy and relevance settings.
- `../historical/simulator/sensing.py`: historical synthetic observations.
- `../validation/cooja/codec.c`: deterministic Cooja source blocks and source representation.
- Raw evidence archives contain each executed run’s generated configuration, offered trace and manifest.
- No external field dataset is required.

`software_versions.json` identifies the two evidence generations. Preserve their different codecs, context models and denominators.
