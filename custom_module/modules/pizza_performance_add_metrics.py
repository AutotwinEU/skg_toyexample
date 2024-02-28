from promg import DatabaseConnection
from promg.database_managers import authentication

from custom_module.modules.ecdf_library import *
from custom_module.modules.store_in_db import Store_in_db
from custom_module.cypher_queries.performance_queries import PerformanceQueryLibrary as pfql



def add_conformance_between_ecdfs(dbconnection, ecdf1_name, ecdf2_name, ecdf1_counter, ecdf2_counter, ecdfs):
    difference = Ecdf_compute.difference(ecdfs[ecdf1_counter], ecdfs[ecdf2_counter])
    similarity = Ecdf_compute.similarity_using_diff(difference, ecdfs[ecdf1_counter], ecdfs[ecdf2_counter])
    performance = Ecdf_compute.performance_ratio(ecdfs[ecdf1_counter], ecdfs[ecdf2_counter], 0.5)
    kolmogorov = Ecdf_compute.kolmogorov(ecdfs[ecdf1_counter], ecdfs[ecdf2_counter])
    dbconnection.exec_query(pfql.diffence_and_similarity_between_ecdfs,
            **{"ecdf_name1": ecdf1_name, "ecdf_name2": ecdf2_name,
               "difference": difference, "similarity": similarity, "performance": performance, "kolmogorov": kolmogorov})

def add_conformance_to_a_ecdfc(dbconnection,ecdfc_name):
    ecdfs_data=dbconnection.exec_query(pfql.all_ecdfs_of_an_ecdfc, **{"name": ecdfc_name["names"]})
    ecdfs = [Store_in_db.retrieve(ecdf_name["ecdf"]) for ecdf_name in ecdfs_data]
    for ecdf1_counter in range(len(ecdfs)):
        for ecdf2_counter in range(len(ecdfs)):
            ecdf1_name=ecdfs_data[ecdf1_counter]["ecdf"]
            ecdf2_name=ecdfs_data[ecdf2_counter]["ecdf"]
            add_conformance_between_ecdfs(dbconnection, ecdf1_name, ecdf2_name, ecdf1_counter, ecdf2_counter, ecdfs)

def add_aggregated_data_to_an_ecdf(dbconnection,ecdf_name):
    ecdf = Store_in_db.retrieve(ecdf_name["names"])
    min = ecdf.min_value()
    max = ecdf.max_value()
    average = ecdf.avg_value()
    median = ecdf.median_value()
    dbconnection.exec_query(pfql.set_ecdf_properties,
                            **{"name": ecdf_name["names"], "min": min, "max": max, "average": average, "median": median})

def add_aggregated_data_to_queues(dbconnection,queue_name):
    queue=Store_in_db.retrieve(queue_name["names"])
    min = queue.get_min()
    max = queue.get_max()
    average = queue.get_average()
    dbconnection.exec_query(pfql.set_queue_properties, **{"name":queue_name["names"],"min":min,"max":max,"average":average})

def add_metrics(db_name):
    print("Starting adding metrics...")
    credentials = authentication.connections_map[authentication.Connections.LOCAL]
    dbconnection=DatabaseConnection.set_up_connection(credentials=credentials, verbose=False)
    if db_name is not None:
        dbconnection.change_db(db_name)

    # add difference, similarity and performance between ecdfs
    for ecdfc_name in Store_in_db.retrieve_names("Latency"):
        add_conformance_to_a_ecdfc(dbconnection,ecdfc_name)

    for ecdf_name in Store_in_db.retrieve_names("LatencyECDF"):
        add_aggregated_data_to_an_ecdf(dbconnection,ecdf_name)

    # add min, max and average queue sizes to each queue
    queue_names=Store_in_db.retrieve_names("Queue")
    if queue_names is not None:
        for queue_name in queue_names:
            add_aggregated_data_to_queues(dbconnection,queue_name)

    print("Finishing adding metrics...")

# add_conformance()