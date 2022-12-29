"""
Script used to add the mode individuals to the ontology.
This is done simply by creating all the individuals of each mode.
"""
import re
import rdflib
from rdflib import OWL, RDF, RDFS
import argparse
import music21
from utils import m21_to_mto_label

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
args.add_argument("--mto", type=str, required=True)
args.add_argument("--fho", type=str, required=True)

if __name__ == "__main__":
  args = args.parse_args()

  MTO = rdflib.Namespace("http://purl.org/ontology/mto/")
  MTO_KB = rdflib.Namespace("http://purl.org/ontology/mto/kb/")
  mto_graph = rdflib.Graph().parse(args.mto)
  notes = list(mto_graph.triples((None, RDF.type, MTO["Note"])))

  FHO = rdflib.Namespace("http://example.org/fho/")
  FHO_KB = rdflib.Namespace("http://example.org/fho/kb/")
  fho_graph = rdflib.Graph().parse(args.fho)
  
  # create the major and minor scale of every note
  for note, _, _ in notes:
    if "Double" not in str(note):
      note_name = mto_graph.value(subject=note, predicate=RDFS.label)
        
      major_scale_name = f"{m21_to_mto_label(note_name)}_MajorScale" 
      fho_graph.add((FHO_KB[major_scale_name], RDF.type, MTO["MajorScale"]))
      fho_graph.add((FHO_KB[major_scale_name], MTO["hasRootNote"], note))
      fho_graph.add((FHO_KB[major_scale_name], RDFS.label, rdflib.Literal(f"{note_name} Major Scale")))
      fho_graph.add((FHO_KB[major_scale_name], RDFS.comment, 
                    rdflib.Literal(f"Major scale with tonic note {note_name}")))

      minor_scale_name = f"{m21_to_mto_label(note_name)}_MinorScale" 
      fho_graph.add((FHO_KB[minor_scale_name], RDF.type, MTO["MinorScale"]))
      fho_graph.add((FHO_KB[minor_scale_name], MTO["hasRootNote"], note))
      fho_graph.add((FHO_KB[minor_scale_name], RDFS.label, rdflib.Literal(f"{note_name} Minor Scale")))
      fho_graph.add((FHO_KB[minor_scale_name], RDFS.comment, 
                    rdflib.Literal(f"Minor scale with tonic note {note_name}")))

  # add owl:sameAs between individuals
  # major scale
  for s, _, _ in fho_graph.triples((None, RDF.type, FHO["IonianModeScale"])):
    root = str(fho_graph.value(subject=s, predicate=MTO["hasRootNote"])).split("/")[-1]
    fho_graph.add((s, OWL.sameAs, FHO_KB[f"{root}_MajorScale"]))
  
  # minor scale
  for s, _, _ in fho_graph.triples((None, RDF.type, FHO["AeolianModeScale"])):
    root = fho_graph.value(subject=s, predicate=MTO["hasRootNote"])
    # get the relative minor
    rel_minor = str(mto_graph.value(subject=root, predicate=MTO["hasMajorSixthInterval"])).split("/")[-1]
    fho_graph.add((s, OWL.sameAs, FHO_KB[f"{rel_minor}_MinorScale"]))
  
  print(fho_graph.serialize())