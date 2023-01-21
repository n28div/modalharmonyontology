# Use with Stardog - EL Reasoning - Approximate reasoning
import re
import rdflib
from rdflib import OWL, RDF, RDFS
from rdflib.extras.infixowl import Restriction
import argparse
import music21
from utils import m21_to_mto_label

args = argparse.ArgumentParser()
args.add_argument("--fho", type=str, required=True)

if __name__ == "__main__":
  args = args.parse_args()

  FHO = rdflib.Namespace("http://example.org/fho/")
  FHO_KB = rdflib.Namespace("http://example.org/fho/kb/")
  graph = rdflib.Graph().parse(args.fho)

  PARENT_PROPERTIES = [
    "hasTonicChord", "hasSupertonicChord",
    "hasMediantChord", "hasSubdominantChord",
    "hasDominantChord", "hasSubmediantChord",
    "hasLeadingtoneChord"
  ]
  
  for parent in PARENT_PROPERTIES:
    parent_fho = FHO[parent]

    chain = list(graph.triples((parent_fho, OWL.propertyChainAxiom, None)))
    if len(chain) > 0:
      chain = graph.collection(chain[0][-1])
      
      for subproperty, _, _ in graph.triples((None, RDFS.subPropertyOf, parent_fho)):
        d = graph.value(subject=subproperty, predicate=RDFS.domain)
        d_rolified = FHO[f"R_{str(d).split('/')[-1]}"]
        graph.add((d_rolified, RDF.type, OWL.ObjectProperty))
        # hasSelf restriction (not supported by rdflib)
        bnode = rdflib.BNode()
        graph.add((bnode, RDF.type, OWL.Restriction))
        graph.add((bnode, OWL.onProperty, d_rolified))
        graph.add((bnode, OWL.hasSelf, rdflib.Literal(True)))
        graph.add((d, OWL.equivalentClass, bnode))

        r = graph.value(subject=subproperty, predicate=RDFS.range)
        r_rolified = FHO[f"R_{str(r).split('/')[-1]}"]
        graph.add((r_rolified, RDF.type, OWL.ObjectProperty))
        # hasSelf restriction (not supported by rdflib)
        bnode = rdflib.BNode()
        graph.add((bnode, RDF.type, OWL.Restriction))
        graph.add((bnode, OWL.onProperty, r_rolified))
        graph.add((bnode, OWL.hasSelf, rdflib.Literal(True)))
        graph.add((r, OWL.equivalentClass, bnode))

        new_chain_IRI = rdflib.BNode()
        new_chain = rdflib.collection.Collection(
          graph, 
          new_chain_IRI, 
          [d_rolified, *chain, r_rolified])
        graph.add((subproperty, OWL.propertyChainAxiom, new_chain_IRI))
      
      graph.remove((parent_fho, OWL.propertyChainAxiom, None))
      
  print(graph.serialize())