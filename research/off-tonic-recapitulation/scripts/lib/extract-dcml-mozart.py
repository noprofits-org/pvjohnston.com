#!/usr/bin/env python3
"""Extract one schema-v3 Mozart dossier from the pinned DCML v2.3 sources.

This helper deliberately uses only Python's standard library.  It emits a
model-facing dossier plus a separate operator-only audit object.  The Node
wrapper performs the final schema/semantic validation and output hashing.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from fractions import Fraction
from pathlib import Path


PINNED_COMMIT = "5337257a5318711e6302cfe85c3f1a6ade3c6271"

WORKS = {
    "K333-1": {
        "tonic": "Bb",
        "mode": "major",
        "files": {
            "MS3/K333-1.mscx": "2822921745818df3d3194215b33ea0a46c72756a6468426ed22f575a056839f2",
            "notes/K333-1.notes.tsv": "40f4ce51a41000025bc71c7f1fccdf34c90cfed53216a6ff755df4224d3c2458",
            "measures/K333-1.measures.tsv": "7fa973ac443a449fa3f4cd18ada093a6b7c8ed1a66bc4244542a0957dab2497f",
        },
    },
    "K545-1": {
        "tonic": "C",
        "mode": "major",
        "files": {
            "MS3/K545-1.mscx": "1d54af691e2b24be8f977b048d7417ff2abc79b69bdd484de82a85f4dcf33654",
            "notes/K545-1.notes.tsv": "6e67611704cf0ecb83d10ee574f2095180b30a0b121ff8ed983d30e51cde0551",
            "measures/K545-1.measures.tsv": "ba453205a0c39871ce01f1f4d84df4e9c7ae3d686a29f783a02702c5143643f4",
        },
    },
    "K570-1": {
        "tonic": "Bb",
        "mode": "major",
        "files": {
            "MS3/K570-1.mscx": "326fecaedf12ebe933bb14b13aef62bd33127cf5df9f7946bb4d4af9bd0443a8",
            "notes/K570-1.notes.tsv": "0b8501f172b6498d202ffba50cd8ee55e25581f2a115c0c4d57cb632c5a76f1f",
            "measures/K570-1.measures.tsv": "5e5b5a551cdf0de8e7eaff03c00cc05e41ef66dd58e16df76f78d1c3f51c88ce",
        },
    },
}

CONFIG_KEYS = {
    "case_id",
    "work",
    "candidate_mc",
    "candidate_onset_qn",
    "second_part_mc",
    "second_part_onset_qn",
}

STEPS = ("C", "D", "E", "F", "G", "A", "B")
STEP_INDEX = {step: index for index, step in enumerate(STEPS)}
NATURAL_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
MAJOR_FIFTHS_TO_TONIC = {
    -7: "Cb", -6: "Gb", -5: "Db", -4: "Ab", -3: "Eb", -2: "Bb", -1: "F",
    0: "C", 1: "G", 2: "D", 3: "A", 4: "E", 5: "B", 6: "F#", 7: "C#",
}
MAJOR_TONIC_TO_FIFTHS = {value: key for key, value in MAJOR_FIFTHS_TO_TONIC.items()}

DURATION_TYPES = {
    "long": Fraction(4, 1),
    "breve": Fraction(2, 1),
    "whole": Fraction(1, 1),
    "half": Fraction(1, 2),
    "quarter": Fraction(1, 4),
    "eighth": Fraction(1, 8),
    "16th": Fraction(1, 16),
    "32nd": Fraction(1, 32),
    "64th": Fraction(1, 64),
    "128th": Fraction(1, 128),
}

ARTICULATION_MAP = {
    "articAccentAbove": "accent",
    "articAccentBelow": "accent",
    "articMarcatoAbove": "marcato",
    "articMarcatoBelow": "marcato",
    "articStaccatissimoAbove": "staccatissimo",
    "articStaccatissimoBelow": "staccatissimo",
    "articStaccatoAbove": "staccato",
    "articStaccatoBelow": "staccato",
    "articTenutoAbove": "tenuto",
    "articTenutoBelow": "tenuto",
    "fermataAbove": "fermata",
    "fermataBelow": "fermata",
}

ORNAMENT_MAP = {
    "ornamentMordent": "mordent",
    "ornamentPrallMordent": "inverted_mordent",
    "ornamentTrill": "trill",
    "ornamentTurn": "turn",
    "ornamentTurnInverted": "inverted_turn",
}

DYNAMICS = {
    "pppp", "ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", "ffff",
    "fp", "sf", "sfp", "sfz", "sffz", "rfz",
}

TIE_MAP = {"": "none", "1": "start", "0": "continue", "-1": "stop"}


class ExtractionError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise ExtractionError(message)


def fraction_from_json(value: object, label: str) -> Fraction:
    if not isinstance(value, dict) or set(value) != {"numerator", "denominator"}:
        fail(f"{label} must contain exactly numerator and denominator")
    numerator = value["numerator"]
    denominator = value["denominator"]
    if isinstance(numerator, bool) or not isinstance(numerator, int) or numerator < 0:
        fail(f"{label}.numerator must be a nonnegative integer")
    if isinstance(denominator, bool) or not isinstance(denominator, int) or denominator < 1:
        fail(f"{label}.denominator must be a positive integer")
    result = Fraction(numerator, denominator)
    if result.numerator != numerator or result.denominator != denominator:
        fail(f"{label} must be reduced")
    return result


def rational(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def parse_fraction(value: str, label: str) -> Fraction:
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as error:
        fail(f"invalid exact duration at {label}: {value!r} ({error})")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_config(config: object) -> dict:
    if not isinstance(config, dict) or set(config) != CONFIG_KEYS:
        fail(f"config must contain exactly: {', '.join(sorted(CONFIG_KEYS))}")
    if not isinstance(config["case_id"], str) or not re.fullmatch(r"CASE-[A-Z0-9]{4}", config["case_id"]):
        fail("case_id must match CASE-[A-Z0-9]{4}")
    if config["work"] not in WORKS:
        fail(f"work must be one of: {', '.join(sorted(WORKS))}")
    for key in ("candidate_mc", "second_part_mc"):
        if isinstance(config[key], bool) or not isinstance(config[key], int) or config[key] < 1:
            fail(f"{key} must be a positive integer measure count")
    fraction_from_json(config["candidate_onset_qn"], "candidate_onset_qn")
    fraction_from_json(config["second_part_onset_qn"], "second_part_onset_qn")
    return config


def verify_source(source_root: Path, work: str) -> list[dict[str, str]]:
    if not source_root.is_dir():
        fail(f"DCML source root does not exist: {source_root}")
    try:
        commit = subprocess.run(
            ["git", "-C", str(source_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as error:
        fail(f"could not resolve DCML source commit: {error}")
    if commit != PINNED_COMMIT:
        fail(f"DCML source commit is {commit}, expected pinned {PINNED_COMMIT}")

    verified = []
    for relative, expected in WORKS[work]["files"].items():
        path = source_root / relative
        if not path.is_file():
            fail(f"missing pinned DCML source file: {relative}")
        actual = sha256(path)
        if actual != expected:
            fail(f"source hash mismatch for {relative}: {actual} != {expected}")
        verified.append({"path": relative, "sha256": actual})
    return verified


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source, delimiter="\t"))


def parse_meter(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"([1-9][0-9]*)/([1-9][0-9]*)", value)
    if not match:
        fail(f"unsupported time signature: {value!r}")
    beats, beat_type = int(match.group(1)), int(match.group(2))
    return beats, beat_type


def parse_pitch_name(value: str) -> tuple[str, int, int]:
    match = re.fullmatch(r"([A-G])(bb|##|b|#)?(-?[0-9]+)", value)
    if not match:
        fail(f"unsupported DCML pitch spelling: {value!r}")
    accidental = match.group(2) or ""
    alter = {"bb": -2, "b": -1, "": 0, "#": 1, "##": 2}[accidental]
    return match.group(1), alter, int(match.group(3))


def pitch_class(spelling: str) -> int:
    match = re.fullmatch(r"([A-G])(bb|##|b|#)?", spelling)
    if not match:
        fail(f"unsupported tonic spelling: {spelling!r}")
    alter = {"bb": -2, "b": -1, None: 0, "#": 1, "##": 2}[match.group(2)]
    return (NATURAL_PC[match.group(1)] + alter) % 12


def spelling_parts(spelling: str) -> tuple[str, int]:
    match = re.fullmatch(r"([A-G])(bb|##|b|#)?", spelling)
    if not match:
        fail(f"unsupported pitch spelling: {spelling!r}")
    return match.group(1), {"bb": -2, "b": -1, None: 0, "#": 1, "##": 2}[match.group(2)]


def transposition_for_tonic(tonic: str) -> tuple[int, int]:
    source_step, _ = spelling_parts(tonic)
    chromatic = (-pitch_class(tonic)) % 12
    if chromatic > 6:
        chromatic -= 12
    # The modulo result is +6 for a tritone, satisfying the protocol's tie rule.
    target_index = STEP_INDEX["C"]
    source_index = STEP_INDEX[source_step]
    possible = []
    for diatonic in range(-7, 8):
        if (source_index + diatonic) % 7 == target_index:
            possible.append(diatonic)
    matching_direction = [
        interval for interval in possible
        if interval == 0 or chromatic == 0 or (interval > 0) == (chromatic > 0)
    ]
    if not matching_direction:
        fail(f"could not choose a diatonic transposition for tonic {tonic}")
    diatonic = min(matching_direction, key=lambda interval: (abs(interval), interval))
    return chromatic, diatonic


def transpose_pitch(name: str, midi: int, chromatic: int, diatonic: int) -> dict[str, int | str]:
    step, source_alter, octave = parse_pitch_name(name)
    source_midi = 12 * (octave + 1) + NATURAL_PC[step] + source_alter
    if source_midi != midi:
        fail(f"DCML pitch name/MIDI disagreement: {name} != {midi}")

    absolute_diatonic = octave * 7 + STEP_INDEX[step] + diatonic
    target_octave, target_index = divmod(absolute_diatonic, 7)
    target_step = STEPS[target_index]
    target_midi = midi + chromatic
    target_natural = 12 * (target_octave + 1) + NATURAL_PC[target_step]
    target_alter = target_midi - target_natural
    if not -4 <= target_alter <= 4:
        fail(f"transposed accidental outside schema range for {name}")
    return {"step": target_step, "alter": target_alter, "octave": target_octave}


def transpose_key_signature(fifths: int, chromatic: int, diatonic: int) -> int:
    if fifths not in MAJOR_FIFTHS_TO_TONIC:
        fail(f"source key signature outside supported range: {fifths}")
    source = MAJOR_FIFTHS_TO_TONIC[fifths]
    step, alter = spelling_parts(source)
    source_midi = 60 + NATURAL_PC[step] + alter
    source_octave = 4
    if NATURAL_PC[step] + alter >= 12:
        source_octave += 1
    absolute_diatonic = source_octave * 7 + STEP_INDEX[step] + diatonic
    target_octave, target_index = divmod(absolute_diatonic, 7)
    target_step = STEPS[target_index]
    target_midi = source_midi + chromatic
    target_natural = 12 * (target_octave + 1) + NATURAL_PC[target_step]
    target_alter = target_midi - target_natural
    suffix = {0: "", 1: "#", -1: "b"}.get(target_alter)
    if suffix is None:
        fail(f"transposed key signature is not representable: {source}")
    target = f"{target_step}{suffix}"
    if target not in MAJOR_TONIC_TO_FIFTHS:
        fail(f"transposed key signature lies outside -7..7 fifths: {target}")
    return MAJOR_TONIC_TO_FIFTHS[target]


def element_duration(element: ET.Element, measure_duration_whole: Fraction) -> Fraction:
    duration_type = element.findtext("durationType")
    if duration_type == "measure":
        explicit = element.findtext("duration")
        return parse_fraction(explicit, "measure rest duration") if explicit else measure_duration_whole
    if duration_type not in DURATION_TYPES:
        fail(f"unsupported MuseScore durationType {duration_type!r}")
    base = DURATION_TYPES[duration_type]
    total = base
    addition = base
    dots = int(element.findtext("dots") or "0")
    for _ in range(dots):
        addition /= 2
        total += addition
    return total


def grace_type(chord: ET.Element) -> tuple[bool, str, str]:
    tags = [
        child.tag for child in chord
        if child.tag == "acciaccatura" or child.tag == "appoggiatura" or child.tag.startswith("grace")
    ]
    if len(tags) > 1:
        fail(f"chord has multiple grace-type tags: {tags}")
    if not tags:
        return False, "none", ""
    tag = tags[0]
    if tag == "acciaccatura":
        return True, "acciaccatura", tag
    if tag == "appoggiatura":
        return True, "appoggiatura", tag
    # MuseScore's generic duration-specific grace tags do not assert either
    # named class, so preserve them conservatively as unspecified.
    return True, "unspecified", tag


def marks_from_articulations(elements: list[ET.Element], label: str) -> tuple[list[str], list[str]]:
    articulations: set[str] = set()
    ornaments: set[str] = set()
    for element in elements:
        subtype = element.findtext("subtype")
        if subtype in ARTICULATION_MAP:
            articulations.add(ARTICULATION_MAP[subtype])
        elif subtype in ORNAMENT_MAP:
            ornaments.add(ORNAMENT_MAP[subtype])
        else:
            fail(f"unsupported articulation/ornament {subtype!r} at {label}")
    return sorted(articulations), sorted(ornaments)


def spanner_endpoint(
    mc: int,
    onset: Fraction,
    location: ET.Element,
    measure_rows: list[dict[str, str]],
) -> tuple[int, Fraction]:
    measure_delta = int(location.findtext("measures") or "0")
    if measure_delta < 0:
        fail(f"forward spanner at MC {mc} has a negative measure displacement")
    target_mc = mc + measure_delta
    if target_mc < 1 or target_mc > len(measure_rows):
        fail(f"spanner at MC {mc} ends outside the movement")
    target_onset = onset + parse_fraction(location.findtext("fractions") or "0", f"MC {mc} spanner")
    target_duration = parse_fraction(
        measure_rows[target_mc - 1]["duration_qb"], f"MC {target_mc} duration_qb"
    ) / 4
    while target_onset > target_duration and target_mc < len(measure_rows):
        target_onset -= target_duration
        target_mc += 1
        target_duration = parse_fraction(
            measure_rows[target_mc - 1]["duration_qb"], f"MC {target_mc} duration_qb"
        ) / 4
    if target_onset < 0 or target_onset > target_duration:
        fail(f"spanner at MC {mc} has an endpoint outside MC {target_mc}")
    return target_mc, target_onset


def parse_xml(source: Path, measure_rows: list[dict[str, str]]) -> dict:
    try:
        score = ET.parse(source).getroot().find("Score")
    except ET.ParseError as error:
        fail(f"invalid MuseScore XML: {error}")
    if score is None:
        fail("MuseScore file has no Score element")

    staff_elements = score.findall("Staff")
    if not staff_elements:
        fail("MuseScore file contains no notation staves")
    if any(len(staff.findall("Measure")) != len(measure_rows) for staff in staff_elements):
        fail("MuseScore staff/measure table count disagreement")

    voice_layers: set[tuple[int, int]] = set()
    chord_records: dict[tuple[int, int, int, Fraction], list[dict]] = defaultdict(list)
    rests: dict[int, list[dict]] = defaultdict(list)
    directions: dict[int, list[dict]] = defaultdict(list)
    unsupported: dict[int, list[str]] = defaultdict(list)
    barlines = {
        mc: {"start_repeat": False, "end_repeat": False, "subtypes": set()}
        for mc in range(1, len(measure_rows) + 1)
    }

    for staff_position, staff in enumerate(staff_elements, start=1):
        staff_id = int(staff.get("id") or staff_position)
        for mc, measure in enumerate(staff.findall("Measure"), start=1):
            measure_qn = parse_fraction(measure_rows[mc - 1]["duration_qb"], f"measure {mc} duration_qb")
            measure_whole = measure_qn / 4
            if measure.find("startRepeat") is not None:
                barlines[mc]["start_repeat"] = True
            if measure.find("endRepeat") is not None:
                barlines[mc]["end_repeat"] = True

            for voice_number, voice in enumerate(measure.findall("voice"), start=1):
                cursor = Fraction(0)
                if voice.find("Chord") is not None or voice.find("Rest") is not None:
                    voice_layers.add((staff_id, voice_number))
                for child in voice:
                    if child.tag == "location":
                        cursor += parse_fraction(child.findtext("fractions") or "0", f"MC {mc} location")
                        continue
                    if child.tag in {"Harmony", "Tempo", "Clef", "Beam"}:
                        continue
                    if child.tag in {"KeySig", "TimeSig"}:
                        if cursor != 0:
                            unsupported[mc].append(f"mid-measure {child.tag}")
                        continue
                    if child.tag == "Fermata":
                        unsupported[mc].append("voice-level fermata cannot be attached losslessly")
                        continue
                    if child.tag == "BarLine":
                        subtype = child.findtext("subtype")
                        if subtype:
                            barlines[mc]["subtypes"].add(subtype)
                        continue
                    if child.tag == "Dynamic":
                        value = child.findtext("subtype")
                        if value not in DYNAMICS:
                            unsupported[mc].append(f"unsupported dynamic {value!r}")
                        else:
                            directions[mc].append({
                                "source_onset_whole": cursor,
                                "direction_type": "dynamic",
                                "value": value,
                                "staff": staff_id,
                                "voice": voice_number,
                            })
                        continue
                    if child.tag == "Spanner":
                        kind = child.get("type")
                        if kind == "HairPin" and child.find("HairPin") is not None:
                            subtype = child.findtext("HairPin/subtype") or "0"
                            family = {"0": "crescendo", "1": "diminuendo", "2": "crescendo", "3": "diminuendo"}.get(subtype)
                            location = child.find("next/location")
                            if family is None or location is None:
                                unsupported[mc].append("unsupported hairpin encoding")
                            else:
                                end_mc, end = spanner_endpoint(mc, cursor, location, measure_rows)
                                directions[mc].extend([
                                    {
                                        "source_onset_whole": cursor,
                                        "direction_type": "hairpin",
                                        "value": f"{family}_start",
                                        "staff": staff_id,
                                        "voice": voice_number,
                                    },
                                ])
                                for continuation_mc in range(mc + 1, end_mc):
                                    directions[continuation_mc].append({
                                        "source_onset_whole": Fraction(0),
                                        "direction_type": "hairpin",
                                        "value": f"{family}_continue",
                                        "staff": staff_id,
                                        "voice": voice_number,
                                    })
                                directions[end_mc].append({
                                    "source_onset_whole": end,
                                    "direction_type": "hairpin",
                                    "value": f"{family}_stop",
                                    "staff": staff_id,
                                    "voice": voice_number,
                                })
                        elif kind == "HairPin" and child.find("prev") is not None:
                            # The paired endpoint is emitted from the starting spanner.
                            pass
                        elif kind == "Trill":
                            location = child.find("next/location")
                            if location is None:
                                unsupported[mc].append("unpaired trill spanner is not representable in schema 3")
                            else:
                                end_mc, _ = spanner_endpoint(mc, cursor, location, measure_rows)
                                for affected_mc in range(mc, end_mc + 1):
                                    unsupported[affected_mc].append(
                                        "trill spanner duration is not representable in schema 3"
                                    )
                        else:
                            unsupported[mc].append(f"unsupported voice-level spanner {kind!r}")
                        continue
                    if child.tag not in {"Chord", "Rest"}:
                        unsupported[mc].append(f"unsupported voice element {child.tag!r}")
                        continue

                    duration = element_duration(child, measure_whole)
                    is_grace = False
                    normalized_grace = "none"
                    source_grace = ""
                    if child.tag == "Chord":
                        is_grace, normalized_grace, source_grace = grace_type(child)
                        try:
                            articulations, ornaments = marks_from_articulations(
                                child.findall("Articulation"), f"MC {mc} staff {staff_id} voice {voice_number}"
                            )
                        except ExtractionError as error:
                            unsupported[mc].append(str(error))
                            articulations, ornaments = [], []
                        pitches = []
                        for note in child.findall("Note"):
                            if note.find("Symbol") is not None:
                                unsupported[mc].append("note Symbol is not representable in schema 3")
                            pitch = note.findtext("pitch")
                            tpc = note.findtext("tpc")
                            if pitch is None or tpc is None:
                                fail(f"MC {mc} note lacks pitch or tonal pitch class")
                            for spanner in note.findall("Spanner"):
                                if spanner.get("type") != "Tie":
                                    unsupported[mc].append(f"unsupported note spanner {spanner.get('type')!r}")
                            pitches.append((int(pitch), int(tpc) - 14))
                        if not pitches:
                            fail(f"MC {mc} contains an empty chord")
                        for spanner in child.findall("Spanner"):
                            if spanner.get("type") == "Trill":
                                unsupported[mc].append("trill spanner duration is not representable in schema 3")
                            elif spanner.get("type") != "Slur":
                                unsupported[mc].append(f"unsupported chord spanner {spanner.get('type')!r}")
                        if child.find("Arpeggio") is not None:
                            ornaments = sorted(set(ornaments) | {"arpeggiate"})
                        chord_records[(mc, staff_id, voice_number, cursor)].append({
                            "pitches": sorted(pitches),
                            "duration_whole": duration,
                            "is_grace": is_grace,
                            "grace": normalized_grace,
                            "source_grace": source_grace,
                            "articulations": articulations,
                            "ornaments": ornaments,
                        })
                    else:
                        try:
                            articulations, ornaments = marks_from_articulations(
                                child.findall("Articulation"), f"MC {mc} rest"
                            )
                        except ExtractionError as error:
                            unsupported[mc].append(str(error))
                            articulations, ornaments = [], []
                        if ornaments:
                            unsupported[mc].append("rest ornament is not representable in schema 3")
                        rests[mc].append({
                            "staff": staff_id,
                            "voice": voice_number,
                            "source_onset_whole": cursor,
                            "duration_whole": duration,
                            "articulations": articulations,
                        })

                    if cursor < 0 or (not is_grace and cursor + duration > measure_whole):
                        fail(f"MC {mc} staff {staff_id} voice {voice_number} event lies outside its measure")
                    if not is_grace:
                        cursor += duration

    voice_map = {
        layer: f"V{index:02d}"
        for index, layer in enumerate(sorted(voice_layers), start=1)
    }
    if len(voice_map) > 99:
        fail("source contains more than 99 voice layers")
    return {
        "voice_map": voice_map,
        "chords": chord_records,
        "rests": rests,
        "directions": directions,
        "unsupported": unsupported,
        "barlines": barlines,
    }


def parse_notes(rows: list[dict[str, str]]) -> tuple[dict, dict]:
    required = {
        "mc", "mc_onset", "staff", "voice", "duration", "gracenote",
        "nominal_duration", "tied", "tpc", "midi", "name", "chord_id",
    }
    if not rows or not required.issubset(rows[0]):
        fail("DCML notes table lacks required columns")

    grouped_rows: dict[tuple[int, int, int, str], list[dict[str, str]]] = defaultdict(list)
    by_measure: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        mc = int(row["mc"])
        staff = int(row["staff"])
        voice = int(row["voice"])
        parse_pitch_name(row["name"])
        midi = int(row["midi"])
        step, alter, octave = parse_pitch_name(row["name"])
        if 12 * (octave + 1) + NATURAL_PC[step] + alter != midi:
            fail(f"DCML name/MIDI mismatch at MC {mc}: {row['name']} / {midi}")
        if row["tied"] not in TIE_MAP:
            fail(f"unsupported DCML tie state at MC {mc}: {row['tied']!r}")
        grouped_rows[(mc, staff, voice, row["chord_id"])].append(row)
        by_measure[mc].append(row)

    grouped_by_key: dict[tuple[int, int, int, Fraction], list[dict]] = defaultdict(list)
    for (mc, staff, voice, chord_id), group in grouped_rows.items():
        first = group[0]
        onset = parse_fraction(first["mc_onset"], f"MC {mc} note onset")
        is_grace = bool(first["gracenote"])
        duration = parse_fraction(
            first["nominal_duration"] if is_grace else first["duration"],
            f"MC {mc} note duration",
        )
        for row in group[1:]:
            if (
                row["mc_onset"] != first["mc_onset"]
                or bool(row["gracenote"]) != is_grace
                or (row["nominal_duration"] if is_grace else row["duration"])
                != (first["nominal_duration"] if is_grace else first["duration"])
            ):
                fail(f"inconsistent note rows within chord {chord_id}")
        grouped_by_key[(mc, staff, voice, onset)].append({
            "chord_id": int(chord_id),
            "rows": group,
            "pitches": sorted((int(row["midi"]), int(row["tpc"])) for row in group),
            "duration_whole": duration,
            "is_grace": is_grace,
        })
    for groups in grouped_by_key.values():
        groups.sort(key=lambda group: group["chord_id"])
    return grouped_by_key, by_measure


def reconcile_chords(tsv_chords: dict, xml_chords: dict) -> None:
    keys = set(tsv_chords) | set(xml_chords)
    for key in sorted(keys):
        tsv_groups = tsv_chords.get(key, [])
        xml_groups = xml_chords.get(key, [])
        if len(tsv_groups) != len(xml_groups):
            fail(f"MuseScore/notes-table chord-count mismatch at {key}")
        for position, (tsv_group, xml_group) in enumerate(zip(tsv_groups, xml_groups), start=1):
            for field in ("pitches", "duration_whole", "is_grace"):
                if tsv_group[field] != xml_group[field]:
                    fail(f"MuseScore/notes-table {field} mismatch at {key}, chord {position}")
            tsv_grace = tsv_group["rows"][0]["gracenote"]
            if bool(tsv_grace) != bool(xml_group["source_grace"]):
                fail(f"MuseScore/notes-table grace mismatch at {key}, chord {position}")
            tsv_group["grace"] = xml_group["grace"]
            tsv_group["articulations"] = xml_group["articulations"]
            tsv_group["ornaments"] = xml_group["ornaments"]


def measure_metadata(rows: list[dict[str, str]]) -> list[dict]:
    required = {"mc", "quarterbeats", "duration_qb", "keysig", "timesig"}
    if not rows or not required.issubset(rows[0]):
        fail("DCML measures table lacks required columns")
    result = []
    for expected_mc, row in enumerate(rows, start=1):
        mc = int(row["mc"])
        if mc != expected_mc:
            fail(f"measures table is not contiguous at MC {expected_mc}")
        beats, beat_type = parse_meter(row["timesig"])
        result.append({
            "mc": mc,
            "absolute_start_qn": parse_fraction(row["quarterbeats"], f"MC {mc} quarterbeats"),
            "duration_qn": parse_fraction(row["duration_qb"], f"MC {mc} duration_qb"),
            "meter": {"beats": beats, "beat_type": beat_type},
            "complete_duration_qn": Fraction(beats * 4, beat_type),
            "keysig": int(row["keysig"]),
        })
    return result


def fixed_windows(measures: list[dict], candidate_mc: int) -> list[tuple[str, str, list[tuple[int, int]]]]:
    if candidate_mc - 6 < 1 or candidate_mc + 11 > len(measures):
        fail("candidate does not have the required six-measure context on both sides")

    opening = []
    cursor = 1
    if measures[0]["duration_qn"] < measures[0]["complete_duration_qn"]:
        opening.append((-1, 1))
        cursor = 2
    elif measures[0]["duration_qn"] != measures[0]["complete_duration_qn"]:
        fail("first measure is longer than its active meter")
    for index in range(8):
        mc = cursor + index
        if measures[mc - 1]["duration_qn"] != measures[mc - 1]["complete_duration_qn"]:
            fail(f"opening MC {mc} is not a complete measure")
        opening.append((index, mc))

    contexts = []
    for start in (candidate_mc - 6, candidate_mc, candidate_mc + 6):
        selected = []
        for index, mc in enumerate(range(start, start + 6)):
            if measures[mc - 1]["duration_qn"] != measures[mc - 1]["complete_duration_qn"]:
                fail(f"context MC {mc} is not a complete measure")
            selected.append((index, mc))
        contexts.append(selected)

    all_mcs = [mc for _, mc in opening]
    for selected in contexts:
        all_mcs.extend(mc for _, mc in selected)
    if len(all_mcs) != len(set(all_mcs)):
        fail("fixed windows overlap")
    return [
        ("W1", "opening", opening),
        ("W2", "pre_candidate", contexts[0]),
        ("W3", "candidate", contexts[1]),
        ("W4", "continuation", contexts[2]),
    ]


def event_sort_key(event: dict) -> tuple:
    onset = event["_onset"]
    voice = event["voice_id"]
    event_rank = 0 if event["event_type"] == "note" else 1
    if event["event_type"] == "note":
        pitch = event["pitch"]
        pitch_key = (pitch["octave"], STEP_INDEX[pitch["step"]], pitch["alter"])
    else:
        pitch_key = (-999, -999, -999)
    remaining = (
        event["_duration"],
        tuple(event["articulations"]),
        event.get("tie", ""),
        event.get("grace", ""),
        tuple(event.get("ornaments", [])),
    )
    return onset, voice, event_rank, pitch_key, remaining


def direction_sort_key(direction: dict) -> tuple:
    return (
        direction["_onset"],
        direction["direction_type"],
        direction["value"],
        direction["voice_id"] or "",
    )


def normalize_barline(mc: int, count: int, structure: dict) -> tuple[str, str]:
    left = "none" if mc == 1 else "regular"
    right = "final" if mc == count else "regular"
    if structure["start_repeat"]:
        left = "repeat_start"
    subtypes = structure["subtypes"]
    if structure["end_repeat"] or "end-repeat" in subtypes:
        right = "repeat_end"
    elif "double" in subtypes:
        right = "double"
    elif "dashed" in subtypes:
        right = "dashed"
    elif subtypes - {"normal", "double", "dashed"}:
        fail(f"unsupported barline subtype(s) at MC {mc}: {sorted(subtypes)}")
    return left, right


def build(source_root: Path, config: dict) -> dict:
    work = config["work"]
    pins = verify_source(source_root, work)
    settings = WORKS[work]
    note_rows = read_tsv(source_root / f"notes/{work}.notes.tsv")
    raw_measure_rows = read_tsv(source_root / f"measures/{work}.measures.tsv")
    measures = measure_metadata(raw_measure_rows)
    xml = parse_xml(source_root / f"MS3/{work}.mscx", raw_measure_rows)
    tsv_chords, notes_by_measure = parse_notes(note_rows)
    reconcile_chords(tsv_chords, xml["chords"])
    for (mc, staff, voice, onset), groups in tsv_chords.items():
        grace_groups = [group for group in groups if group["is_grace"]]
        if len(grace_groups) > 1:
            xml["unsupported"][mc].append(
                "multiple ordered grace chords share one onset/voice, but schema 3 has no grace-sequence field"
            )
        non_grace_durations = [group["duration_whole"] for group in groups if not group["is_grace"]]
        if len(non_grace_durations) != len(set(non_grace_durations)):
            xml["unsupported"][mc].append(
                "distinct simultaneous chords are not recoverable from schema-3 note events"
            )

    candidate_mc = config["candidate_mc"]
    second_part_mc = config["second_part_mc"]
    if candidate_mc > len(measures) or second_part_mc > len(measures):
        fail("configured source measure lies beyond the movement")
    candidate_onset = fraction_from_json(config["candidate_onset_qn"], "candidate_onset_qn")
    second_part_onset = fraction_from_json(config["second_part_onset_qn"], "second_part_onset_qn")
    if candidate_onset >= measures[candidate_mc - 1]["duration_qn"]:
        fail("candidate onset lies outside its measure")
    if second_part_onset >= measures[second_part_mc - 1]["duration_qn"]:
        fail("second-part onset lies outside its measure")

    windows = fixed_windows(measures, candidate_mc)
    selected_mcs = {mc for _, _, selected in windows for _, mc in selected}
    for mc in sorted(selected_mcs):
        if xml["unsupported"].get(mc):
            details = "; ".join(sorted(set(xml["unsupported"][mc])))
            fail(f"selected MC {mc} contains notation schema 3 cannot preserve losslessly: {details}")

    candidate_has_note = any(
        parse_fraction(row["mc_onset"], f"MC {candidate_mc} candidate check") * 4 == candidate_onset
        for row in notes_by_measure[candidate_mc]
    )
    if not candidate_has_note:
        fail("candidate onset does not coincide with a notated note")

    chromatic, diatonic = transposition_for_tonic(settings["tonic"])
    initial_fifths = measures[0]["keysig"]
    expected_initial = MAJOR_TONIC_TO_FIFTHS[settings["tonic"]]
    if initial_fifths != expected_initial:
        fail(f"initial key signature {initial_fifths} disagrees with preset tonic {settings['tonic']}")

    absolute_candidate = measures[candidate_mc - 1]["absolute_start_qn"] + candidate_onset
    absolute_second_part = measures[second_part_mc - 1]["absolute_start_qn"] + second_part_onset
    movement_end = max(measure["absolute_start_qn"] + measure["duration_qn"] for measure in measures)
    if absolute_candidate < absolute_second_part:
        fail("candidate precedes configured second-part boundary")
    if absolute_second_part >= movement_end:
        fail("second-part boundary is not before movement end")
    elapsed = absolute_candidate - absolute_second_part
    total = movement_end - absolute_second_part

    evidence_counter = 1
    event_counter = 1
    direction_counter = 1
    normalized_windows = []
    selected_event_count = 0
    selected_rest_count = 0
    selected_direction_count = 0
    source_measure_map = []

    for window_id, role, selected in windows:
        normalized_measures = []
        for relative_index, mc in selected:
            metadata = measures[mc - 1]
            events = []
            # Notes are emitted chord by chord so chord-level notation can be
            # copied to every constituent note without losing its application.
            chord_keys = sorted(
                (key for key in tsv_chords if key[0] == mc),
                key=lambda key: (key[3], key[1], key[2]),
            )
            for key in chord_keys:
                _, staff, voice, source_onset = key
                voice_id = xml["voice_map"].get((staff, voice))
                if voice_id is None:
                    fail(f"note refers to unmapped source voice at MC {mc}")
                for group in tsv_chords[key]:
                    onset_qn = source_onset * 4
                    duration_qn = group["duration_whole"] * 4
                    for row in group["rows"]:
                        event = {
                            "event_type": "note",
                            "onset_qn": rational(onset_qn),
                            "duration_qn": rational(duration_qn),
                            "voice_id": voice_id,
                            "pitch": transpose_pitch(
                                row["name"], int(row["midi"]), chromatic, diatonic
                            ),
                            "tie": TIE_MAP[row["tied"]],
                            "grace": group["grace"],
                            "articulations": list(group["articulations"]),
                            "ornaments": list(group["ornaments"]),
                            "_onset": onset_qn,
                            "_duration": duration_qn,
                        }
                        events.append(event)

            for rest in xml["rests"].get(mc, []):
                voice_id = xml["voice_map"].get((rest["staff"], rest["voice"]))
                if voice_id is None:
                    fail(f"rest refers to unmapped source voice at MC {mc}")
                onset_qn = rest["source_onset_whole"] * 4
                duration_qn = rest["duration_whole"] * 4
                events.append({
                    "event_type": "rest",
                    "onset_qn": rational(onset_qn),
                    "duration_qn": rational(duration_qn),
                    "voice_id": voice_id,
                    "articulations": list(rest["articulations"]),
                    "_onset": onset_qn,
                    "_duration": duration_qn,
                })
                selected_rest_count += 1

            events.sort(key=event_sort_key)
            for event in events:
                event["event_id"] = f"EV{event_counter:04d}"
                event_counter += 1
                del event["_onset"]
                del event["_duration"]
            selected_event_count += len(events)

            directions = []
            for source_direction in xml["directions"].get(mc, []):
                onset_qn = source_direction["source_onset_whole"] * 4
                if onset_qn < 0 or onset_qn > metadata["duration_qn"]:
                    fail(f"direction at MC {mc} lies outside its measure")
                directions.append({
                    "direction_type": source_direction["direction_type"],
                    "onset_qn": rational(onset_qn),
                    "voice_id": xml["voice_map"].get(
                        (source_direction["staff"], source_direction["voice"])
                    ),
                    "value": source_direction["value"],
                    "_onset": onset_qn,
                })
                if directions[-1]["voice_id"] is None:
                    fail(f"direction refers to unmapped source voice at MC {mc}")
            directions.sort(key=direction_sort_key)
            for direction in directions:
                direction["direction_id"] = f"DR{direction_counter:04d}"
                direction_counter += 1
                del direction["_onset"]
            selected_direction_count += len(directions)

            left_barline, right_barline = normalize_barline(mc, len(measures), xml["barlines"][mc])
            normalized_measures.append({
                "measure_index": relative_index,
                "evidence_id": f"E{evidence_counter:03d}",
                "notated_duration_qn": rational(metadata["duration_qn"]),
                "meter": metadata["meter"],
                "key_signature": {
                    "fifths": transpose_key_signature(metadata["keysig"], chromatic, diatonic)
                },
                "left_barline": left_barline,
                "right_barline": right_barline,
                "volta": "none",
                "events": events,
                "directions": directions,
            })
            source_measure_map.append({
                "window_id": window_id,
                "measure_index": relative_index,
                "source_mc": mc,
            })
            evidence_counter += 1
        normalized_windows.append({
            "window_id": window_id,
            "role": role,
            "measures": normalized_measures,
        })

    dossier = {
        "schema_version": "3.0.0",
        "case_id": config["case_id"],
        "condition": "symbolic",
        "encoding": {
            "common_tonic": "C",
            "home_mode": settings["mode"],
            "duration_unit": "quarter_note",
            "measure_numbers": "window_relative",
            "pitch_system": "scientific_pitch_diatonic_spelling",
            "coverage": {
                "notes": "complete",
                "rests": "complete",
                "voices": "complete",
                "meter": "complete",
                "key_signatures": "complete",
                "dynamics": "complete",
                "articulations": "complete",
                "ornaments": "complete",
                "repeats_and_barlines": "complete",
            },
        },
        "candidate_return": {
            "window_id": "W3",
            "measure_index": 0,
            "onset_qn": rational(candidate_onset),
            "second_part_elapsed_qn": rational(elapsed),
            "second_part_total_qn": rational(total),
        },
        "windows": normalized_windows,
    }

    audit = {
        "schema_version": "1.0.0",
        "status": "generated_unverified",
        "case_id": config["case_id"],
        "source": {
            "source_id": "SRC-DCML-MOZART-V2.3",
            "work": work,
            "commit": PINNED_COMMIT,
            "files": pins,
        },
        "configuration": config,
        "normalization": {
            "source_tonic": settings["tonic"],
            "home_mode": settings["mode"],
            "chromatic_semitones": chromatic,
            "diatonic_steps": diatonic,
            "voice_map": [
                {"source_staff": staff, "source_voice": voice, "voice_id": voice_id}
                for (staff, voice), voice_id in sorted(xml["voice_map"].items())
            ],
        },
        "source_measure_map": source_measure_map,
        "exact_durations_qn": {
            "second_part_elapsed": rational(elapsed),
            "second_part_total": rational(total),
        },
        "checks": {
            "all_source_chords_reconciled_with_notes_table": True,
            "selected_schema_unsupported_constructs": 0,
            "selected_event_count": selected_event_count,
            "selected_rest_count": selected_rest_count,
            "selected_direction_count": selected_direction_count,
        },
        "limitations": [
            "generated dossier still requires source-score visual verification and reverse-render review",
            "schema 3 omits slurs, clefs, beaming, tempo, and display-only accidental status by design",
            "chord-level articulations and ornaments are copied to every constituent note event",
        ],
    }
    return {"dossier": dossier, "audit": audit}


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: extract-dcml-mozart.py SOURCE_ROOT", file=sys.stderr)
        return 2
    try:
        config = verify_config(json.load(sys.stdin))
        package = build(Path(sys.argv[1]).resolve(), config)
        json.dump(package, sys.stdout, ensure_ascii=True, separators=(",", ":"), sort_keys=False)
        sys.stdout.write("\n")
        return 0
    except (ExtractionError, OSError, ValueError, KeyError) as error:
        print(f"extraction failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
