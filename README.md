# Running the docker file

Run

```
docker pull stardog/stardog:latest
docker run -it -v $PWD/.docker/stardog:/var/opt/stardog -p 5820:5820 stardog/stardog
```

* Open https://stardog.studio/
* Click on `Connect to Stardog` and add a new connection (default credetianls is `admin:admin`)
* Click on the DB icon -> Create database -> Name the db `fho` (**important**)
* Load the ontologies from `ontology/final.ttl` and `ontology/mto.ttl`
* Load chord data from `data/chord_individuals.ttl` (around 9k triples should be in the DB)
* Turn off the DB (top switch) -> Select properties tab and enable **SameAs** and **Punning** -> Click on save (top-right) -> Turn on DB again

# Roman inference
The file `scripts/infer_roman.py` performs roman numeral inference.

An example is

```python scripts/infer_roman.py --chord C:maj --key C --scale Major```

`scale` can be `Major`, `Minor` or one of the seven modes.