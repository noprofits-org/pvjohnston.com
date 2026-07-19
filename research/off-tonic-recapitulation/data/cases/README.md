# Model-facing pilot dossiers

This directory contains exactly six JSON dossiers conforming to
`../schema/case.schema.json`, including the pre-freeze replacement
`CASE-D09B`. Dataset 1.0.0, its operator manifests, prompt hashes, and 108-call
schedule were frozen at 2026-07-19T17:54:14Z. The collection lock was created
and verified at 2026-07-19T17:56:35.630Z; real-case collection is authorized
only from the pre-outcome Git commit containing it. File presence alone is not
evidence that those gates were met.

Each invocation receives exactly one dossier. Filenames and case IDs are
arbitrary, operator-assigned opaque labels; they are not claimed to have been
randomly generated. They must not encode composer, work, date, key
relationship, focal/control status, or expected classification.

Allowed evidence is limited to mechanically transposed symbolic score content:
notes, durations, voices, signatures, dynamics, articulations, texture, and
relative location. Do not include Roman numerals, cadence labels, formal labels,
absolute measure numbers, source prose, or bibliographic provenance.

The identity map belongs under `../provenance/` and is never listed in the
model-facing manifest. The manifest's ordered `cases` array records each opaque
case ID, relative dossier path, and SHA-256 hash; the runner accepts no
caller-supplied file path.
