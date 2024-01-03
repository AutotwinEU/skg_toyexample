# Using Graph Databases to Create Toy Example for Auto Twin

## Installation
### PromG
The library can be installed in Pyhton using pip
`pip install promg==0.1.40`.

Make sure to install version 0.1.40. 

The source code for PromG can be found [PromG Core Github repository](https://github.com/PromG-dev/promg-core).

### Neo4j
The library assumes that Neo4j is installed.

Install [Neo4j](https://neo4j.com/download/):

- Use the [Neo4j Desktop](https://neo4j.com/download-center/#desktop)  (recommended), or
- [Neo4j Community Server](https://neo4j.com/download-center/#community)

## Get started

### Create a new graph database

- The scripts in this release assume password "12345678".
- The scripts assume the server to be available at the default URL `bolt://localhost:7687`
  - You can modify this also in the script.
- ensure to allocate enough memory to your database, advised: `dbms.memory.heap.max_size=5G`
- the script expects the `Neo4j APOC library` to be installed as a plugin, see https://neo4j.com/labs/apoc/


### Store the preprocessed data sets

The preprocessed datasets (S1-S7.csv) should be stored in the following directory `/data/ToyExampleV2/` or `/data/ToyExampleV3/` respectively. 

How to use
----------

For data import

1. start the Neo4j server
2. Set `local = True` and the version number (either 2 or 3) in `main.py`.
1. run `main.py`

## Data set & scripts
The data set should be added by the user.

#### Datasets
- The data set should be added by the user.
#### JSON files
- ToyExample.json - a description of which Entities (Pizza, Sensors, Station), Classes need to be created:
The main script uses this information to construct the EKG.
- ToyExample_DS.json - a description of the different data sets. It describes which labels the records should receive (e.g. :Event, :Location, :Activity) and what properties records have
