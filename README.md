# Using Graph Databases to Create Toy Example V3.6 for Auto Twin

## Installation
### PromG
The library can be installed in Pyhton using pip
`pip install promg==1.0.1`.

Ensure you have installed the correct version (version 1.0.1).

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


### Save the preprocessed data sets

All the preprocessed datasets can be found at [NextCloud Data](https://autotwin.cloud68.co/f/44738).
The complete folder `ToyExampleV3` should be put under `/data/`. 
For example your file structure for `S1.csv` should be e.g. `/data/ToyExampleV3/S1.csv`.

### Create config file

Create a `config.yaml` file and store in the root directory.
The file should be formatted as follows:
```yaml
# Database Credentials and Information
db_name: "<DATABASE NAME>" # e.g. "neo4j"
uri: "<URI OF DATABASE SERVER>" # e.g. bolt://localhost:7687"
user: "<USER>" # e.g. "neo4j"
password: "<PASSWORD>" # e.g. "12345678"
import_directory:  "<IMPORT DIRECTORY>" # see note 1

# Dataset information
dataset_name: "ToyExample"
semantic_header_path: "json_files/ToyExample.json"
dataset_description_path: "json_files/ToyExample_DS.json"
use_sample: false

# Import settings
verbose: false
batch_size: 10000
use_preprocessed_files: false
```

> **_NOTE:_**  You can determine the import directory as follows: 
> 1) Select the Neo4j Server in Neo4j Desktop > Click the three dots > Select Open Folder > Select Import
> 2) This opens the import directory, so now you can copy the directory.

### Schema

The schema can be found at [Nextcloud Schema v3.6](https://autotwin.cloud68.co/f/43488).

The schema is described in the following files:
- ToyExampleV3.json - a description of which Entities (Pizza, Sensors, Station, ...), need to be created:
The main script uses this information to construct the EKG.
- ToyExamplev3_DS.json - a description of the different data sets. It describes which labels the records should receive (e.g. :Event, :Location, :Activity) and what properties records have

### How to use

1. start the Neo4j server
2. Set `local = True` and the version number to 3 in `main.py` (line 29).
1. run `main.py`

## Getting Stuck??
If you're getting stuck (or you have questions), feel free to reach out to me at a.j.e.swevels@tue.nl.
