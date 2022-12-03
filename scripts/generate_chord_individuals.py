"""
Script used to add the mode individuals to the ontology.
This is done simply by creating all the individuals of each mode.
"""
import re
import rdflib
import argparse
import music21

def m21_to_mto_label(note: str) -> str:
  """
  Convert a music21 note to an mto note.
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

def mto_to_harte_label(note: str) -> str:
  """
  Convert an mto note to a Harte note.
  mto notes use Flat instead of b and Sharp instead
  of #.

  Args:
      note (str): Note in mto format
  Returns:
      str: Note in Harte format.
  """
  note = note.replace("Flat", "b")
  note = note.replace("Sharp", "#")
  return note


if __name__ == "__main__":

  CHORD = rdflib.Namespace("http://purl.org/ontology/chord/")
  MTO = rdflib.Namespace("http://purl.org/ontology/mto/")
  MTO_KB = rdflib.Namespace("http://purl.org/ontology/mto/kb/")
  FHO = rdflib.Namespace("http://example.org/fho/")
  FHO_KB = rdflib.Namespace("http://example.org/fho/kb/")
  OWL = rdflib.OWL
  RDF = rdflib.RDF
  RDFS = rdflib.RDFS

  graph = rdflib.Graph()

  # create the individuals
  SHORTHAND_DEGREE = {
    "maj": ["MajorThirdInterval", "PerfectFifthInterval"],
    "min": ["MinorThirdInterval", "PerfectFifthInterval"],
    "7": ["MajorThirdInterval", "PerfectFifthInterval", "MajorSeventhInterval"],
    "maj7": ["MajorThirdInterval", "PerfectFifthInterval", "MinorSeventhInterval"],
    "min7": ["MinorThirdInterval", "PerfectFifthInterval", "MinorSeventhInterval"],
    "dim": ["MinorThirdInterval", "DiminishedFifthInterval"],
  }

  NOTES = [
    "A", "AFlat", "ASharp", "B", "BFlat", "C",
    "CSharp", "D", "DFlat", "DSharp", "E", "EFlat",
    "F", "FSharp", "G", "GFlat", "GSharp"
  ]

  for note in NOTES:
    for shorthand, intervals in SHORTHAND_DEGREE.items():
      harte_chord = f"{mto_to_harte_label(note)}:{shorthand}"

      # add chord to graph
      graph.add((FHO_KB[harte_chord], RDF.type, CHORD["Chord"]))
      graph.add((FHO_KB[harte_chord], CHORD["root"], MTO_KB[note]))
      
      for interval in intervals:
        graph.add((FHO_KB[harte_chord], CHORD["interval"], MTO[interval]))

  print(graph.serialize())