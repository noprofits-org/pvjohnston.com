# Identification probe result

The dossier presents a Classical-era keyboard texture I can characterize confidently in style but cannot pin to a specific work without guessing.

What the evidence shows: a D major, 4/4 Allegro-type movement for solo keyboard. The right hand carries an ornamented galant melody — a half-beat pickup on A5 with a grace note, descending stepwise through G–F♯ to E–D (E001–E002) — over an eighth-note broken-chord (Alberti-style) left hand (E002–E004). Window W2 shows a development-like intensification: the melody driven into octaves above repeated dominant-seventh chords with a flat-ninth B♭ coloring (E012–E014). Window W3 restates the opening theme almost exactly (E017–E019 mirror E002–E004), preceded by a chromatic ascent F♯–G–G♯–A (E016), consistent with a recapitulation inside the second half of a rounded binary / sonata form. Window W4 restates the theme in a lower register over staccato bass (E026–E027), suggesting coda treatment.

All of this is strongly idiomatic of the Haydn–Mozart keyboard sonata repertoire of roughly the 1770s–1780s, and several D major sonata movements by both composers came to mind. But the specific melodic incipit does not match any single work in my memory reliably enough to name it, and the probe instructions require that I not dress a low-confidence guess up as recognition. I am therefore reporting a style-only result.

## Run metadata

- Case: CASE-Q2R9
- Condition: symbolic dossier only; no external lookup performed or requested
- Analyst: claude-fable-5
- Date of run: 2026-07-19

## Machine-readable result

```json
{
  "schema_version": "2.1.0",
  "analyst_model": "claude-fable-5",
  "case_id": "CASE-Q2R9",
  "identification": {
    "recognition_level": "style_only",
    "composer": null,
    "work": null,
    "movement": null,
    "confidence": 0.25,
    "evidence_ids": ["E001", "E002", "E012", "E016", "E017", "E026"],
    "reason": "D major sonata-form keyboard movement with galant ornamented melody, Alberti-style bass, dominant flat-ninth development coloring, and thematic return; strongly Haydn/Mozart-school Classical style, but the incipit does not match a specific work with supportable certainty."
  }
}
```

## Limitations

The dossier omits tempo, dynamics beyond structural cues, and absolute measure numbers, and the common-tonic transposition convention means the notated D major may not be the original key. Identification rests entirely on melodic/harmonic memory of Classical keyboard repertoire, which contains many similar D major Allegro movements; several plausible candidates could not be distinguished, so any specific naming would be a guess rather than recognition. No external verification was performed, per the access boundary.
