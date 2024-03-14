from flask import Flask, current_app

# tag::import[]
from neo4j import GraphDatabase
from promg import DatabaseConnection, Configuration, Performance

# end::import[]

"""
Initiate the configuration file in PromG
"""


# tag::initConfiguration[]
def init_promg_configuration(semantic_header_path, dataset_description_path, import_directory, db_name, uri, user,
                             password, verbose, batch_size, use_sample, use_preprocessed_files):
    config = Configuration(
        semantic_header_path=semantic_header_path,
        dataset_description_path=dataset_description_path,
        import_directory=import_directory,
        db_name=db_name,
        uri=uri,
        user=user,
        password=password,
        verbose=verbose,
        batch_size=batch_size,
        use_sample=use_sample,
        use_preprocessed_files=use_preprocessed_files)

    return config


# end::initConfiguration[]

# tag::getConfiguration[]
def get_promg_configuration():
    return current_app.promg_config


# end::getConfiguration[]

# tag::initPerformance[]
def init_performance(performance_path):
    current_app.performance = Performance(performance_path, write_console=False)


# end::initPerformance[]

# tag::getPerformance[]
def get_performance():
    return current_app.performance


# end::getPerformance[]

"""
Initiate the connection to a Neo4j Driver
"""


# tag::initDatabaseConnection[]
def init_db_connection(uri, db_name, user, password):
    current_app.connection = DatabaseConnection(uri=uri, db_name=db_name, user=user, password=password)

    return current_app.connection


# end::initDatabaseConnection[]


"""
Get the instance of the Neo4j Driver created in the `initDriver` function
"""


# tag::getDatabaseConnection[]
def get_db_connection():
    return current_app.connection


# end::getDriver[]

"""
If the driver has been instantiated, close it and all remaining open sessions
"""


# tag::closeConnection[]
def close_connection():
    if current_app.connection is not None:
        current_app.connection.close_connection()
        current_app.connection = None

        return current_app.connection


# end::closeConnection[]

"""
Get the instance of the Neo4j Driver created in the `initDriver` function
"""


# tag::getDriver[]
def get_driver():
    return current_app.connection.driver

# end::getDriver[]
