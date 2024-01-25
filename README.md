# Create a System Knowledge Graph for Toy Example V3.6 for Auto Twin

---------------------

## Installation
### Neo4j
The code assumes that Neo4j is installed.

Install [Neo4j](https://neo4j.com/download/):

- Use the [Neo4j Desktop](https://neo4j.com/download-center/#desktop)  (recommended), or
- [Neo4j Community Server](https://neo4j.com/download-center/#community)

### PromG
PromG should be installed as a Python package using pip
`pip install promg==1.0.4`.

The source code for PromG can be found [PromG Core Github repository](https://github.com/PromG-dev/promg-core).

---------------------

## Getting Started

1. Create database or connect to a database
   <details> 
      <summary> Click here for step-by-step instructions  </summary>

    1. Select `+Add` (Top right corner)
    2. Choose Local DBMS or Remote Connection
    3. Follow the prompted steps (the default password we assume is 12345678)

</details>

2. Configure the database settings (only do this step when you created a local database)
   1. Install APOC: `Neo4j APOC Core library` (see https://neo4j.com/labs/apoc/)
      <details>
         <summary>Click here for step-by-step instructions</summary>
      
      1. Select the database in Neo4j desktop 
      2. On the right, click on the `plugins` tab > Open the `APOC` section > Click the `install` button
      3. Wait until a green check mark shows up next to `APOC` - that means it's good to go!
      
    </details>

   2. Install APOC: `Neo4j APOC Extended library`
      <details>
        <summary>Click here for step-by-step instructions</summary>
   
      1. Download the [appropriate release](https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases) (same version numbers as your Neo4j version)
          1. Look for the release that matches the version number of your Neo4j Database.
          2. Download the file `apoc-[your neo4j version]-extended.jar`
       2. Locate the `plugins` folder of your database:  
          Select the Neo4j Server in Neo4j Desktop > Click the three dots > Select `Open Folder` > Select `Plugins`
       4. Put `apoc-[your neo4j version]-extended.jar` into the `plugins` folder of your database
       5. Restart the server (database)
      
      </details>

   3. Configure extra settings using the configuration file `$NEO4J_HOME/conf/apoc.conf`
      <details>
        <summary>Click here for step-by-step instructions</summary>
      
      1. Locate the `conf` folder of your database  
         Select the Neo4j Server in Neo4j Desktop > Click the three dots > Select `Open Folder` > Select `Conf`
      2. Create the file `apoc.conf`
      3. Add the following line to `apoc.conf`: `apoc.import.file.enabled=true`.
   
      </details>
   4. Ensure to allocate enough memory to your database, advised: `dbms.memory.heap.max_size=10G`
      <details>
        <summary>Click here for step-by-step instructions</summary>
      
      1. Select the Neo4j Server in Neo4j Desktop > Click the three dots > Select `Settings`
      2. Locate `dbms.memory.heap.max_size=512m`
      3. Change `512m` to `10G`
        
      </details>

    
3. Save the preprocessed data sets
   <details>
        <summary>Click here for step-by-step instructions</summary>
    All the preprocessed datasets can be found at [NextCloud Data](https://autotwin.cloud68.co/f/44738).
    The complete folder `ToyExampleV3` should be put under `/data/`. 
    For example your file structure for `S1.csv` should be e.g. `/data/ToyExampleV3/S1.csv`.
   </details>


4. Create and store the configuration file `config.yaml` in the root directory (see [Create config file](#config))
    <details>
    <summary> Click here for example `config.yaml` file </summary>
   Create a `config.yaml` file and store in the root directory.
   The file should be formatted as follows:

   ```yaml
   # Database Credentials and Information
   db_name: "neo4j"
   uri: "<URI OF DATABASE SERVER>" # e.g. bolt://localhost:7687" (see note 1)
   user: "neo4j"
   password: "<PASSWORD>" # e.g. "12345678" (see note 2)
   import_directory:  "<IMPORT DIRECTORY>" # (see note 3)

   # Dataset information
   dataset_name: "ToyExample"
   semantic_header_path: "json_files/ToyExample.json"
   dataset_description_path: "json_files/ToyExample_DS.json"
   use_sample: false # set to true or false depending on whether you want to use a sample

   # Import settings
   verbose: false
   batch_size: 10000
   use_preprocessed_files: false
   ```

   > **_NOTES:_**  You can determine the import directory as follows: 
   > 1) Set the URI in `config.yaml` to the URI of your server. Default value is `bolt://localhost:7687`.
   > 2) Set the password in `config.yaml` to the password of your server. Default value is `12345678`. 
   > 3) Set the import directory in `config.yaml` to the import directory of your Neo4j server. You can determine the import directory as follows:
   >    1) Select the Neo4j Server in Neo4j Desktop > Click the three dots > Select `Open Folder` > Select `Import`
   >    2) This opens the import directory, so now you can copy the directory.
  </details>

5. Connect to the Neo4j server
   <details>
     <summary>Click here for step-by-step instructions</summary>
   
      1. Select the database in Neo4j desktop 
      2. Click the `Connect` button
      3. Wait until a textbox `• active` is shown - that means it's good to go!
   </details>


6. Install PromG in Python. 
   
   PromG should be installed as a Python package using pip `pip install promg==1.0.4`.


6. run main.py

---------------------
## Database Schema

The schema can be found at [Nextcloud Schema v3.6](https://autotwin.cloud68.co/f/43488).

The schema is described in the following files:
- ToyExampleV3.json - a description of which Entities (Pizza, Sensors, Station, ...), need to be created:
The main script uses this information to construct the EKG.
- ToyExamplev3_DS.json - a description of the different data sets. It describes which labels the records should receive (e.g. :Event, :Location, :Activity) and what properties records have

---------------------

## Getting Stuck??
If you're getting stuck (or you have questions), feel free to reach out to me at a.j.e.swevels@tue.nl.
