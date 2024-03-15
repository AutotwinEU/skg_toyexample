from pizza_module.modules.pizza_performance_add_metrics import add_metrics, add_conformance_to_a_ecdfc
from pizza_module.modules.pizza_performance_create_website import Performance_website
from pizza_module.modules.store_in_db import *
from pizza_module.modules.pizza_performance_ecdfs import *
from pizza_module.cypher_queries.performance_queries import PerformanceQueryLibrary as pfql
from promg import DatabaseConnection

class PizzaPerformanceModule:
    def __init__(self, config, first_time):
        self.connection = DatabaseConnection.set_up_connection(config=config)
        self.first_time = first_time

    def __add_ecdfcs_to_skg(self,gt_sim):
        for ecdfc in PizzaPerformanceModuleEcdfs(self.connection).return_ecdfcs(gt_sim):
            id1 = Store_in_db(self.connection,"", ecdfc.return_title(), "Latency",gt_sim).store()
            for ecdf in ecdfc.return_ecdfs():
                id2 = Store_in_db(self.connection,ecdf, ecdf.legend(), "LatencyECDF",gt_sim).store()
                self.connection.exec_query(pfql.connect_performance_artifacts,
                                           **{"id1": id1[0]["id"], "id2": id2[0]["id"]})

    def __retrieve_ecdfcs_from_skg(self, gt_sim):
        ecdfcs = []
        for ecdfcname in Store_in_db.retrieve_names(self.connection,"Latency"):
            ecdfs = [Store_in_db.retrieve(self.connection,ecdf["ecdf"],gt_sim)
                     for ecdf in self.connection.exec_query(pfql.all_ecdfs_of_an_ecdfc,
                                                    **{"name": ecdfcname["names"], "gt_sim": gt_sim})]
            ecdfcs.append(Ecdf_collection(ecdfs, ecdfcname["names"]))
        return ecdfcs

    def add_performance_to_skg(self,gt_sim):
        print("start add_performance_to_skg")
        self.__add_ecdfcs_to_skg(gt_sim)
        add_metrics(self.connection,gt_sim)
        print("finish add_performance_to_skg")

    def retrieve_performance_from_skg(self,working_dir,gt_sim):
        print("start retrieve_performance_from_skg")
        ecdfcs = self.__retrieve_ecdfcs_from_skg(gt_sim)
        Performance_website(self.connection,working_dir, ecdfcs, [], [], [], self.first_time).create()
        print("finish retrieve_performance_from_skg")

    def post_processing(self):
        self.connection.exec_query(pfql.connect_latencies_to_ecdf_latencies)
        self.connection.exec_query(pfql.add_suffix_to_ecdf_latencies)

        # add difference, similarity and performance between ecdfs
        for ecdfc_name in Store_in_db.retrieve_names(self.connection, "Latency"):
            add_conformance_to_a_ecdfc(self.connection, ecdfc_name)

    def remove_performance_artifacts(self):
        self.connection.exec_query(pfql.delete_all_performance_nodes)
