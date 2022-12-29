"""
Script used to add the mode individuals to the ontology.
This is done simply by creating all the individuals of each mode.
"""
import rdflib
from rdflib import RDF, OWL, RDFS
import argparse
import music21
from itertools import product
from utils import m21_to_mto_label, m21_to_leadsheet_label

args = argparse.ArgumentParser()
args.add_argument("--mto", type=str, required=True)
args.add_argument("-i", "--input", type=str, required=False, default=None)

if __name__ == "__main__":
  args = args.parse_args()

  MTO = rdflib.Namespace("http://purl.org/ontology/mto/")
  MTO_KB = rdflib.Namespace("http://purl.org/ontology/mto/kb/")
  mto_graph = rdflib.Graph().parse(args.mto)
  notes = list(mto_graph.triples((None, RDF.type, MTO["Note"])))

  FHO = rdflib.Namespace("http://example.org/fho/")
  FHO_KB = rdflib.Namespace("http://example.org/fho/kb/")

  graph = rdflib.Graph()
  if args.input is not None:
    graph.parse(args.input)

  # create the individuals
  DEEGREES = ["Tonic", "Supertonic", "Mediant", "Subdominant", "Dominant", "Submediant", "Leadingtone"]
  SCALES = [
    "IonianMode", "DorianMode", "PhrygianMode", "LydianMode", "MixolydianMode", "AeolianMode", "LocrianMode",
  ]

  m21_scale = music21.scale.ConcreteScale()
  for scale in SCALES:
    m21_scale.abstract = music21.scale.AbstractDiatonicScale(scale.replace("Mode", ""))
  
    for note_mto, _, _ in notes:
      if "Double" not in str(note_mto):
        note_name = mto_graph.value(subject=note_mto, predicate=RDFS.label)
        scale_name = f"{note_mto.split('/')[-1]}_{scale}Scale"

        # create the individual
        graph.add((FHO_KB[scale_name], RDF.type, FHO[f"{scale}Scale"]))
        graph.add((FHO_KB[scale_name], MTO["hasRootNote"], note_mto))
        
        scale_label = scale.replace("Mode", "")
        graph.add((FHO_KB[scale_name], RDFS.label, rdflib.Literal(f"{note_name} {scale_label} Mode")))
        graph.add((FHO_KB[scale_name], RDFS.comment, 
                  rdflib.Literal(f"{scale_label} modal scale with tonic note {note_name}")))
        
        m21_scale.tonic = music21.pitch.Pitch(note_name.replace("b", "-"))

        for scale_note, scale_note_degree in zip(m21_scale.getPitches(), DEEGREES):
          scale_note_name = m21_to_mto_label(m21_to_leadsheet_label(scale_note.name))
          graph.add((FHO_KB[scale_name], FHO[f"has{scale_note_degree}Note"], MTO_KB[scale_note_name]))
    
  print(graph.serialize())