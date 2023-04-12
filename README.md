# Using Graph Databases to Create Toy Example for Auto Twin

## Description

This repository collects queries for modeling and importing incomplete event data as Event Knowledge Graphs using the Labeled
Property Graph data model of graph databases.
All scripts and queries are licensed under LGPL v3.0, see LICENSE.
Copyright information is provided within each Project.

## Requirements

### Neo4j
Install the neo4j-python-driver

`pip install neo4j`
OR
`conda install -c conda-forge neo4j-python-driver`

Install [Neo4j](https://neo4j.com/download/):

- Use the [Neo4j Desktop](https://neo4j.com/download-center/#desktop)  (recommended), or
- [Neo4j Community Server](https://neo4j.com/download-center/#community)

### EKG Construction
The EKG construction is specified in `ekg-creator` and is a submodule, for documentation see [ekg_creator](https://github.com/Ava-S/ekg_creator).

So do not forget to run `git submodule init` and `git submodule update`.

### Other packages
- `numpy`
- `pandas`
- `tabulate`
- `tqdm`

## Get started

### Create a new graph database

- The scripts in this release assume password "12345678".
- The scripts assume the server to be available at the default URL `bolt://localhost:7687`
  - You can modify this also in the script.
- ensure to allocate enough memory to your database, advised: `dbms.memory.heap.max_size=5G`
- the script expects the `Neo4j APOC library` to be installed as a plugin, see https://neo4j.com/labs/apoc/

### Store the preprocessed data sets

The preprocessed datasets (S1-S7.csv) should be stored in the following directory /data/ToyExample/

How to use
----------

For data import

1. start the Neo4j server
1. run `main.py`

Output: 
Event logs for the pizza, sensors and stations in data\ToyExample\event_logs.

## Data set & scripts
The data set should be added by the user.

#### Datasets
- The data set should be added by the user.
#### JSON files
- ToyExample.json - a description of which Entities (Pizza, Sensors, Station), Classes need to be created:
The main script uses this information to construct the EKG.
- ToyExample_DS.json - a description of the different data sets. It describes which labels the records should receive (e.g. :Event, :Location, :Activity) and what properties records have

### Main script
There is one script that creates the Event/System knowledge graph: **ekg_creator/main.py**

Then there are several other scripts in the submodule [ekg_creator](https://github.com/Ava-S/ekg_creator). that support this main script. The read me can be found in the sub module.

