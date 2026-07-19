#!/usr/bin/env python3

import argparse
from fractions import Fraction
import json
import xml.etree.ElementTree as ET


parser = argparse.ArgumentParser()
parser.add_argument("xml")
parser.add_argument("--measures", help="1-based sequence indexes, e.g. 1-8,38-55")
parser.add_argument("--json", action="store_true")
args = parser.parse_args()


def fraction_text(value):
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def selected(index):
    if not args.measures:
        return True
    for item in args.measures.split(","):
        bounds = [int(value) for value in item.split("-")]
        if len(bounds) == 1 and index == bounds[0]:
            return True
        if len(bounds) == 2 and bounds[0] <= index <= bounds[1]:
            return True
    return False


root = ET.parse(args.xml).getroot()
part = root.find("part")
divisions = 1
records = []

for sequence_index, measure in enumerate(part.findall("measure"), 1):
    attributes = measure.find("attributes")
    if attributes is not None and attributes.findtext("divisions"):
        divisions = int(attributes.findtext("divisions"))
    cursor = Fraction(0)
    previous_onset = None
    events = []
    for child in measure:
        if child.tag == "backup":
            cursor -= Fraction(int(child.findtext("duration")), divisions)
            continue
        if child.tag == "forward":
            cursor += Fraction(int(child.findtext("duration")), divisions)
            continue
        if child.tag != "note" or child.get("print-object") == "no":
            continue
        duration = Fraction(int(child.findtext("duration") or "0"), divisions)
        is_chord = child.find("chord") is not None
        onset = previous_onset if is_chord else cursor
        if not is_chord and child.find("grace") is None:
            cursor += duration
        if not is_chord:
            previous_onset = onset
        staff = child.findtext("staff") or "1"
        voice = f"V0{staff}"
        options = {}
        articulations = []
        for element, value in [
            ("accent", "accent"),
            ("staccato", "staccato"),
            ("staccatissimo", "staccatissimo"),
            ("tenuto", "tenuto"),
            ("strong-accent", "marcato"),
        ]:
            if child.find(f"notations/articulations/{element}") is not None:
                articulations.append(value)
        if child.find("notations/fermata") is not None:
            articulations.append("fermata")
        if articulations:
            options["articulations"] = sorted(set(articulations))
        ornaments = []
        for element, value in [
            ("trill-mark", "trill"),
            ("mordent", "mordent"),
            ("inverted-mordent", "inverted_mordent"),
            ("turn", "turn"),
            ("inverted-turn", "inverted_turn"),
        ]:
            if child.find(f"notations/ornaments/{element}") is not None:
                ornaments.append(value)
        if child.find("notations/arpeggiate") is not None:
            ornaments.append("arpeggiate")
        if ornaments:
            options["ornaments"] = sorted(set(ornaments))
        ties = sorted({element.get("type") for element in child.findall("tie")})
        if ties == ["start"]:
            options["tie"] = "start"
        elif ties == ["stop"]:
            options["tie"] = "stop"
        elif ties == ["start", "stop"]:
            options["tie"] = "continue"
        grace = child.find("grace")
        if grace is not None:
            options["grace"] = "acciaccatura" if grace.get("slash") == "yes" else "unspecified"
        if child.find("rest") is not None:
            event = ["r", fraction_text(onset), fraction_text(duration), voice]
            if options:
                event.append(options)
        else:
            pitch = child.find("pitch")
            step = pitch.findtext("step")
            alter = int(pitch.findtext("alter") or "0")
            suffix = {-2: "bb", -1: "b", 0: "", 1: "#", 2: "##"}[alter]
            name = f"{step}{suffix}{pitch.findtext('octave')}"
            event = ["n", fraction_text(onset), fraction_text(duration), voice, [name]]
            if options:
                event.append(options)
        events.append(event)
    if selected(sequence_index):
        records.append({
            "sequence": sequence_index,
            "xml_number": measure.get("number"),
            "new_system": measure.find("print") is not None,
            "events": events,
        })

if args.json:
    print(json.dumps(records, indent=2))
else:
    for record in records:
        marker = " SYSTEM" if record["new_system"] else ""
        print(f"SEQ {record['sequence']} XML {record['xml_number']}{marker}")
        for event in record["events"]:
            print("  " + json.dumps(event, separators=(",", ":")))
