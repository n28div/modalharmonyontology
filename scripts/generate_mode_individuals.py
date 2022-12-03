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

args = argparse.ArgumentParser()
args.add_argument("-i", "--input", type=str, required=True)

if __name__ == "__main__":
  args = args.parse_args()

  MTO = rdflib.Namespace("http://purl.org/ontology/mto/")
  MTO_KB = rdflib.Namespace("http://purl.org/ontology/mto/kb/")
  FHO = rdflib.Namespace("http://example.org/fho/")
  FHO_KB = rdflib.Namespace("http://example.org/fho/kb/")
  OWL = rdflib.OWL
  RDF = rdflib.RDF
  RDFS = rdflib.RDFS

  graph = rdflib.Graph()
  graph.parse(args.input)

  # create the individuals
  DEEGREES = [
    "Tonic", "Supertonic", "Mediant", "Subdominant",
    "Dominant", "Submediant", "Leadingtone"
  ]

  NOTES = [
    "A", "AFlat", "ASharp", "B", "BFlat", "C",
    "CSharp", "D", "DFlat", "DSharp", "E", "EFlat",
    "F", "FSharp", "G", "GFlat", "GSharp"
  ]

  for s, _, _ in graph.triples((None, RDFS.subClassOf, FHO["Mode"])):
    name = str(s).split("/")[-1]
    mode = name.replace("Mode", "")
    
    for note in NOTES:
      graph.add((FHO_KB[f"{note}_{mode}"], RDF.type, FHO[name]))
      graph.add((FHO_KB[f"{note}_{mode}"], MTO["hasRootNote"], MTO_KB[note]))

    
  print(graph.serialize())