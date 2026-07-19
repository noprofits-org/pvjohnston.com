# Operator-only provenance

Files in this directory document real identities, corpus roles, score sources,
candidate-return locations, extraction decisions, and manual corrections. They
are part of the reproducible repository but are never embedded in a model
prompt and never listed in the `cases` array of `../manifest.json`.

Complete `pilot-corpus.csv` before generating randomized model-facing case IDs.
The identity map should be revealed for scoring the identification probe only
after every scheduled model response has been collected.
