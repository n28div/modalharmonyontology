"""
Script used to add the SWRL rules to the ontology.
The input ontology needs to be in Manchester format. 
It needs to have a dummy Rule which will be removed, added with protege.

Rules are taken from https://online.berklee.edu/takenote/harmonic-considerations-modal-harmony/
which is extracted from Chapter 2 of Jazz Composition: Theory and Practice by Ted Pease 
and from https://en.wikipedia.org/wiki/Roman_numeral_analysis
and https://en.wikipedia.org/wiki/Mode_(music)
"""
import re
import rdflib
import argparse
import music21
from collections import deque

def m21_to_mto_label(note: str) -> str:
  """
  Convert an a music21 note to an mto note.
  mto notes use Flat instead of - and Sharp instead
  of #.

  Args:
      note (str): Note in music21 format
  Returns:
      str: Note in mto format.
  """
  note = note.replace("-", "Flat")
  note = note.replace("#", "Sharp")
  return note

MODES = {
  "Ionian": {
    "relation": ["PerfectUnison", "MajorSecond", "MajorThird", "PerfectFourth", "PerfectFifth", "MajorSixth", "MajorSeventh"],
    "root": "PerfectUnison"
  },
  "Dorian": {
    "relation": ["PerfectUnison", "MajorSecond", "MinorThird", "PerfectFourth", "PerfectFifth", "MajorSixth", "MinorSeventh"],
    "root": "MajorSecond"
  },
  "Phrygian": {
    "relation": ["PerfectUnison", "MinorSecond", "MinorThird", "PerfectFourth", "PerfectFifth", "MinorSixth", "MinorSeventh"],
    "root": "MajorThird"
  },
  "Lydian": {
    "relation": ["PerfectUnison", "MajorSecond", "MajorThird", "AugmentedFourth", "PerfectFifth", "MajorSixth", "MajorSeventh"],
    "root": "PerfectFourth"
  },
  "Mixolydian": {
    "relation": ["PerfectUnison", "MajorSecond", "MajorThird", "PerfectFourth", "PerfectFifth", "MajorSixth", "MinorSeventh"],
    "root": "PerfectFifth"
  },
  "Aeolian": {
    "relation": ["PerfectUnison", "MajorSecond", "MinorThird", "PerfectFourth", "PerfectFifth", "MinorSixth", "MinorSeventh"],
    "root": "MajorSixth"
  },
  "Locrian": {
    "relation": ["PerfectUnison", "MinorSecond", "MinorThird", "PerfectFourth", "DiminishedFifth", "MinorSixth", "MinorSeventh"],
    "root": "MajorSeventh"
  }
}

MODE_QUALITY = [
  "mto:MajorTriad(?<http://example.org/chord>)", 
  "mto:MinorTriad(?<http://example.org/chord>)", 
  "mto:MinorTriad(?<http://example.org/chord>)", 
  "mto:MajorTriad(?<http://example.org/chord>)", 
  "mto:MajorTriad(?<http://example.org/chord>)",
  "mto:MinorTriad(?<http://example.org/chord>)", 
  "mto:DiminishedTriad(?<http://example.org/chord>)"
]

DEGREES = [
  "Tonic", "Supertonic", "Mediant", "Subdominant", "Dominant", "Submediant", "Leadingtone"
]

args = argparse.ArgumentParser()
args.add_argument("-i", "--input", type=str, required=True)

if __name__ == "__main__":
  args = args.parse_args()

  with open(args.input) as f:
    ontology = f.read()

  # remove dummy SWRL rule
  ontology = re.sub(r"Rule:\s*\n\s+.*\n", "", ontology)

  # add the axiom for each mode
  # rules are in the form (example Tonic in Ionian)
  # IonianMode(?m) 
  # ^ mto:hasRootNote(?m, ?mr) 
  # ^ mto:hasPerfectUnisonInterval(?mr, ?cr) 
  # ^ mto:MajorTriad(?c)
  # ^ chord:root(?c, ?cr)
  # -> mto:hasTonic(?m, ?c)
  for mode_idx, (mode, mode_meta) in enumerate(MODES.items()):
    rule = f"{mode}Mode(?<http://example.org/mode>), "
    rule += "mto:hasRootNote(?<http://example.org/mode>, ?<http://example.org/mode_root>), "

    # retrieve the starting note of the mode
    # for instance C Ionian mode starts from the note C
    # but C Dorian starts from the note D
    starting_note_prop = f"mto:has{mode_meta['root']}Interval"
    rule += f"{starting_note_prop}(?<http://example.org/mode_root>, ?<http://example.org/tonic_root>), "

    # quality of chords is the right rotation
    # of the array MODE_QUALITY by mode_idx elements
    quality_array = deque(MODE_QUALITY)
    quality_array.rotate(-1 * mode_idx)
    quality_array = list(quality_array) if mode_idx > 0 else MODE_QUALITY

    for quality, relation, degree in zip(quality_array, mode_meta["relation"], DEGREES):
      # set the chord type for this deegree
      deegree_rule = rule + f"{quality}, "
      # retrieve the right degree note given the current tonic
      deegree_rule += f"mto:has{relation}Interval(?<http://example.org/tonic_root>, ?<http://example.org/chord_root>), "
      # set the chord to have the right root note
      deegree_rule += "chord:root(?<http://example.org/chord>, ?<http://example.org/chord_root>) "
      # add the rhs
      deegree_rule += f"-> mto:has{degree}(?<http://example.org/mode>, ?<http://example.org/chord>)"
      # add rule to the ontology
      ontology += "Rule:\n    " + deegree_rule + "\n"

  print(ontology)
