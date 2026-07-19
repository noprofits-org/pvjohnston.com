# Model-facing pilot dossiers

This directory will contain exactly six JSON dossiers conforming to
`../schema/case.schema.json`. It is intentionally empty while corpus selection
and extraction rules are under development.

Each invocation receives exactly one dossier. Filenames and case IDs are
randomized and must not encode composer, work, date, key relationship,
focal/control status, or expected classification.

Allowed evidence is limited to mechanically transposed symbolic score content:
notes, durations, voices, signatures, dynamics, articulations, texture, and
relative location. Do not include Roman numerals, cadence labels, formal labels,
absolute measure numbers, source prose, or bibliographic provenance.

The identity map belongs under `../provenance/` and is never listed in the
model-facing manifest. The manifest's ordered `cases` array records each opaque
case ID, relative dossier path, and SHA-256 hash; the runner accepts no
caller-supplied file path.
