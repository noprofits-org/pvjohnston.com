# Identification probe result

The dossier shows a two-voice binary-form movement in D major, 6/8 meter: an unaccompanied descending scalar incipit (D5–D4–C♯4–B3–A3–G3–F♯3, E001–E002), a rising tonic arpeggio spanning two octaves (E002–E003), a stepwise-descending sequence of tied appoggiaturas over chromatic applied-dominant bass motion (E004–E006, with E♯ and D♯ inflections), a single trill cadence figure (E013), and a literal restatement of the opening at the marked return point 63 quarter notes into a 147-quarter-note second reprise (E015). All of this is idiomatic of a Baroque gigue (or gigue-like finale) from a solo sonata or keyboard suite, in the Italianate mold of Corelli, Handel, or their contemporaries. I considered specific candidates (e.g., a Corelli Op. 5 giga, Handel suite movements, Bach suite gigues), but none matches with enough certainty from memory of the incipit alone — the well-known D-major gigues I can verify (e.g., Bach Partita No. 4, which is in 9/16) are ruled out, and I cannot confirm any other single work. I therefore report a stylistic resemblance only.

## Run metadata

- Analyst model: Claude (claude-fable-5)
- Case: CASE-6U43
- Condition: symbolic dossier only; no external lookup performed or available
- Date of run: 2026-07-19

## Machine-readable result

```json
{
  "schema_version": "2.1.0",
  "analyst_model": "claude-fable-5",
  "case_id": "CASE-6U43",
  "identification": {
    "recognition_level": "style_only",
    "composer": null,
    "work": null,
    "movement": null,
    "confidence": 0.15,
    "evidence_ids": ["E001", "E002", "E003", "E004", "E005", "E006", "E013", "E015"],
    "reason": "Two-voice D-major 6/8 binary movement with scalar incipit, two-octave arpeggio, chromatic appoggiatura sequence, and mid-reprise thematic return: idiomatic late-Baroque gigue (Italian sonata or suite style), but no specific work confirmed from the incipit."
  }
}
```

## Limitations

Identification relies solely on symbolic features in the provided windows; no audio, title, instrumentation, or external reference was available or consulted. The gigue idiom is highly conventional, so many works share this incipit shape and harmonic sequencing, inflating false-recognition risk. My recall of specific Baroque incipits is imperfect, and I could not verify any candidate work's opening against the dossier, so a true positive may have been missed. Confidence reflects style-level certainty only, not any specific attribution.
