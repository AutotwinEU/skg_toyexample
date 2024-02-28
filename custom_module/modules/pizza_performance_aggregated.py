from promg import DatabaseConnection
from promg.database_managers import authentication

from custom_module.cypher_queries.db_management_queries import DBManagementQueries as dbmq
from custom_module.cypher_queries.performance_queries import PerformanceQueryLibrary as pfql
from custom_module.modules.pizza_performance_add_metrics import add_metrics
from custom_module.modules.pizza_performance_flows import PizzaPerformanceModuleFlows
from custom_module.modules.store_in_db import Store_in_db

from custom_module.modules.pizza_performance import PizzaPerformanceModule
import time

def create_db(db_name):
    credentials = authentication.connections_map[authentication.Connections.LOCAL]
    db_connection = DatabaseConnection.set_up_connection(credentials=credentials, verbose=False)
    db_connection.exec_query(dbmq.create_db, **{"dbname": db_name})

def copy_ecdfcs_from_one_database_to_aggregated(db_connection):
    db_connection.change_db(db_connection.exec_query(dbmq.return_db_list)[0]["name"])
    ecdfc_values = db_connection.exec_query(pfql.return_all_ecdfcs_and_values_of_a_db)
    db_connection.change_db("aggregated")
    for ecdfc_value in ecdfc_values:
        db_connection.exec_query(pfql.create_latency_with_name_and_value, **{"name": ecdfc_value["p.name"], "value": ecdfc_value["p.val"]})

def copy_flows_from_one_database_to_aggregated(db_connection,working_dir):
    db_connection.change_db(db_connection.exec_query(dbmq.return_db_list)[0]["name"])
    for flow in PizzaPerformanceModuleFlows(working_dir).return_flows():
        db_connection.change_db("aggregated")
        Store_in_db(flow, flow.return_title(), "Flow").store()

def copy_ecdfs_from_one_database_to_aggregated(db_connection,db_name):
    db_connection.change_db(db_name["name"])
    ecdf_values = db_connection.exec_query(pfql.return_all_ecdfs_and_values_of_a_db)
    db_connection.change_db("aggregated")
    for ecdf_value in ecdf_values:
        name = ecdf_value["p.name"] + " (" + db_name["name"] + ")"
        db_connection.exec_query(pfql.create_latencyecdf_with_name_and_value_and_dbname,
                                 **{"name": name, "value": ecdf_value["p.val"], "db_name": db_name["name"]})
        db_connection.exec_query(pfql.connect_performance_artifacts_by_name,
                                 **{"name1": ecdf_value["parent"], "name2": name})

def add_aggregated_performance(working_dir):
    print("Starting aggregated performance...")
    credentials = authentication.connections_map[authentication.Connections.LOCAL]
    db_connection = DatabaseConnection.set_up_connection(credentials=credentials, verbose=False)
    create_db("aggregated")
    time.sleep(2)
    db_connection.change_db("aggregated")
    db_connection.exec_query(pfql.create_main_performance_nodes)

    copy_ecdfcs_from_one_database_to_aggregated(db_connection)
    db_names=db_connection.exec_query(dbmq.return_db_list)
    for db_name in db_names:
        copy_ecdfs_from_one_database_to_aggregated(db_connection, db_name)
    db_connection.change_db("aggregated")
    copy_flows_from_one_database_to_aggregated(db_connection,working_dir)
    db_connection.exec_query(pfql.connect_main_performance_nodes_to_children)
    print("Finishing aggregated performance...")

    add_metrics("aggregated")

    print("Starting aggregated performance website creation...")
    db_connection.change_db("aggregated")
    PizzaPerformanceModule(working_dir).retrieve_performance_from_skg_aggregated(db_names)
    print("Finishing aggregated performance website creation...")

# working_dir="D:/perf_analysis/aggregated"
# add_aggregated_performance(working_dir)
