from promg import DatabaseConnection
from custom_module.cypher_queries.performance_queries import PerformanceQueryLibrary as pfql
from custom_module.modules.pizza_performance_ecdfs import *
from custom_module.modules.ecdf_library import *
from custom_module.modules.store_in_db import *


class PizzaPerformanceModule:
    def __init__(self):
        self.connection = DatabaseConnection()

    def __delete_all_performance_nodes(self):
        self.connection.exec_query(pfql.delete_all_performance_nodes)

    def __add_main_performance_nodes(self):
        self.connection.exec_query(pfql.create_main_performance_nodes)

    def __add_ecdfs_to_skg(self):
        ppecdfs = PizzaPerformanceModuleEcdfs()
        for ecdfc in ppecdfs.return_ecdfcs():
            ecdfcstore = Store_in_db("", ecdfc.return_title(), "Latency")
            id1 = ecdfcstore.store()
            self.connection.exec_query(pfql.connect_performance_artifact_to_its_main, **{"kind": "Latency", "id1": id1[0]["id"]})
            for ecdf in ecdfc.return_ecdfs():
                ecdfstore = Store_in_db(ecdf, ecdf.legend(), "LatencyECDF")
                id2 = ecdfstore.store()
                self.connection.exec_query(pfql.connect_performance_artifacts, **{"id1": id1[0]["id"], "id2": id2[0]["id"]})
                self.connection.exec_query(pfql.connect_performance_artifact_to_its_main, **{"kind": "Latency", "id1": id2[0]["id"]})

    def __add_queues_to_skg(self):
        ppqueue = PizzaPerformanceModuleEcdfs()
        #for queueplot in ppqueue.return_queue_plots():


    def add_performance_to_skg(self):
        print("add_performance_to_skg")
        self.__delete_all_performance_nodes()
        self.__add_main_performance_nodes()
        self.__add_ecdfs_to_skg()
        self.__add_queues_to_skg()


