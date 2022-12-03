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
args.add_argument("--mto", type=str, required=True)

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
  
  mto_graph = rdflib.Graph()
  mto_graph.parse(args.mto)

  NOTES = [
    "A", "AFlat", "ASharp", "B", "BFlat", "C",
    "CSharp", "D", "DFlat", "DSharp", "E", "EFlat",
    "F", "FSharp", "G", "GFlat", "GSharp"
  ]

  # create the major and minor scale of every note
  for note in NOTES:
    graph.add((FHO_KB[f"{note}_MajorScale"], RDF.type, MTO["MajorScale"]))
    graph.add((FHO_KB[f"{note}_MajorScale"], MTO["hasRootNote"], MTO_KB[note]))

    graph.add((FHO_KB[f"{note}_MinorScale"], RDF.type, MTO["MinorScale"]))
    graph.add((FHO_KB[f"{note}_MinorScale"], MTO["hasRootNote"], MTO_KB[note]))

  # add owl:sameAs between individuals
  # major scale
  for s, _, _ in graph.triples((None, RDF.type, FHO["IonianMode"])):
    root = str(graph.value(subject=s, predicate=MTO["hasRootNote"])).split("/")[-1]
    graph.add((s, OWL.sameAs, FHO_KB[f"{root}_MajorScale"]))
  
  # minor scale
  for s, _, _ in graph.triples((None, RDF.type, FHO["AeolianMode"])):
    root = graph.value(subject=s, predicate=MTO["hasRootNote"])
    # get the relative minor
    rel_minor = str(mto_graph.value(subject=root, predicate=MTO["hasMajorSixthInterval"])).split("/")[-1]
    graph.add((s, OWL.sameAs, FHO_KB[f"{rel_minor}_MinorScale"]))
  
  print(graph.serialize())