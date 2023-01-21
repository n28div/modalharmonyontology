import re
import rdflib
import argparse

args = argparse.ArgumentParser()
args.add_argument("-i", "--input", type=str, nargs="+")
args.add_argument("-f", "--format", type=str, required=False, default="xml")

if __name__ == "__main__":
  args = args.parse_args()

  graph = rdflib.Graph()
  for o in args.input:
    graph.parse(o)
  
  print(graph.serialize(format=args.format))