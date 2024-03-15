from promg import DatabaseConnection
from promg.database_managers import authentication

from pizza_module.modules.ecdf_library import *
from pizza_module.modules.store_in_db import Store_in_db
from pizza_module.cypher_queries.performance_queries import PerformanceQueryLibrary as pfql



def add_conformance_between_ecdfs(dbconnection, ecdf1_name, ecdf2_name, ecdf1_counter, ecdf2_counter, ecdfs):
    difference = Ecdf_compute.difference(ecdfs[ecdf1_counter], ecdfs[ecdf2_counter])
    similarity = Ecdf_compute.similarity_using_diff(difference, ecdfs[ecdf1_counter], ecdfs[ecdf2_counter])
    performance = Ecdf_compute.performance_ratio(ecdfs[ecdf1_counter], ecdfs[ecdf2_counter], 0.5)
    kolmogorov = Ecdf_compute.kolmogorov(ecdfs[ecdf1_counter], ecdfs[ecdf2_counter])
    dbconnection.exec_query(pfql.diffence_and_similarity_between_ecdfs,
            **{"ecdf_name1": ecdf1_name, "ecdf_name2": ecdf2_name,
               "difference": difference, "similarity": similarity, "performance": performance, "kolmogorov": kolmogorov})

def add_conformance_to_a_ecdfc(dbconnection,ecdfc_name):
    ecdfs_data=dbconnection.exec_query(pfql.all_ecdfs_of_an_ecdfc_all, **{"name": ecdfc_name["names"]})
    ecdfs = [Store_in_db.retrieve(dbconnection,ecdf_name["ecdf"]) for ecdf_name in ecdfs_data]
    for ecdf1_counter in range(len(ecdfs)):
        for ecdf2_counter in range(len(ecdfs)):
            ecdf1_name=ecdfs_data[ecdf1_counter]["ecdf"]
            ecdf2_name=ecdfs_data[ecdf2_counter]["ecdf"]
            add_conformance_between_ecdfs(dbconnection, ecdf1_name, ecdf2_name, ecdf1_counter, ecdf2_counter, ecdfs)

def add_aggregated_data_to_an_ecdf(dbconnection,ecdf_name,gt_sim):
    ecdf = Store_in_db.retrieve(dbconnection,ecdf_name["names"],gt_sim)
    min = ecdf.min_value()
    max = ecdf.max_value()
    average = ecdf.avg_value()
    median = ecdf.median_value()
    dbconnection.exec_query(pfql.set_ecdf_properties,
            **{"name": ecdf_name["names"], "min": min, "max": max, "average": average, "median": median, "gt_sim": gt_sim})

def add_aggregated_data_to_queues(dbconnection,queue_name,gt_sim):
    queue=Store_in_db.retrieve(dbconnection,queue_name["names"],gt_sim)
    min = queue.get_min()
    max = queue.get_max()
    average = queue.get_average()
    dbconnection.exec_query(pfql.set_queue_properties,
            **{"name":queue_name["names"],"min":min,"max":max,"average":average,"gt_sim": gt_sim})

def add_metrics(dbconnection,gt_sim):
    print("Starting adding metrics...")

    for ecdf_name in Store_in_db.retrieve_names(dbconnection,"LatencyECDF"):
        add_aggregated_data_to_an_ecdf(dbconnection,ecdf_name,gt_sim)

    print("Finishing adding metrics...")

# add_conformance()