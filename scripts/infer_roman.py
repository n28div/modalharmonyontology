from SPARQLWrapper import SPARQLWrapper, JSON
import argparse

args = argparse.ArgumentParser()
args.add_argument("-c", "--chord", type=str, required=True)
args.add_argument("-k", "--key", type=str, required=True)
args.add_argument("-s", "--scale", type=str, required=False, default="Ionian")

if __name__ == "__main__":
  args = args.parse_args()
  
  scale = f"mto:{args.scale}Scale" if args.scale in ["Major", "Minor"] else f"fho:{args.scale}Mode"
  
  sparql = SPARQLWrapper("http://localhost:5820/fho/query/reasoning")
  sparql.setCredentials("admin", "admin")

  DEGREE_QUERY_TEMPLATE = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX mto: <http://purl.org/ontology/mto/>
    PREFIX chord: <http://purl.org/ontology/chord/>
    PREFIX fho: <http://example.org/fho/>
    PREFIX ex: <http://example.org/>
    PREFIX mto-kb: <http://purl.org/ontology/mto/kb/>
    PREFIX fho-kb: <ttp://example.org/fho/kb/>

    SELECT DISTINCT ?degreeIRI
    WHERE {
        [] a %s ;
          mto:hasRootNote mto-kb:%s ;
          ?prop <http://example.org/fho/kb/%s> .
                     
        FILTER (?prop != mto:hasDiatonicDegree) .

        BIND(REPLACE(STRAFTER(STR(?prop), STR(mto:)), "has", "") AS ?degree) .
        BIND(URI(CONCAT(STR(mto:), ?degree)) as ?degreeIRI) .
    }
    """
  
  query = DEGREE_QUERY_TEMPLATE % (scale, args.key.replace("#", "Sharp").replace("b", "Flat"), args.chord)
  sparql.setQuery(query)
  sparql.setReturnFormat(JSON)
  ret = sparql.queryAndConvert()
  degrees = map(lambda bind: bind["degreeIRI"]["value"].split("/")[-1], ret["results"]["bindings"])

  DEGREE_LABEL_QUERY_TEMPLATE = """
  PREFIX mto: <http://purl.org/ontology/mto/>
  PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
  SELECT ?degree
  WHERE { mto:%s skos:altLabel ?degree }
  """
  
  for degree in degrees:
    query = DEGREE_LABEL_QUERY_TEMPLATE % degree
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    ret = sparql.queryAndConvert()
    degree = ret["results"]["bindings"][0]["degree"]["value"]
    print(f"{degree}")