from promg import DatabaseConnection
from custom_module.cypher_queries.performance_queries import PerformanceQueryLibrary as pfql
from custom_module.modules.pizza_performance_ecdfs import *
from custom_module.modules.ecdf_library import *
from custom_module.modules.store_in_db import *
from custom_module.modules.pizza_performance_flows import *
from custom_module.modules.pizza_performance_create_website import *

class PizzaPerformanceModule:
    def __init__(self, working_dir):
        self.connection = DatabaseConnection()
        self.__working_dir = working_dir

    def __delete_all_performance_nodes(self):
        self.connection.exec_query(pfql.delete_all_performance_nodes)

    def __add_main_performance_nodes(self):
        self.connection.exec_query(pfql.create_main_performance_nodes)

    def __add_ecdfcs_to_skg(self):
        for ecdfc in PizzaPerformanceModuleEcdfs().return_ecdfcs():
            id1 = Store_in_db("", ecdfc.return_title(), "Latency").store()
            self.connection.exec_query(pfql.connect_performance_artifact_to_its_main, **{"kind": "Latency", "id1": id1[0]["id"]})
            for ecdf in ecdfc.return_ecdfs():
                id2 = Store_in_db(ecdf, ecdf.legend(), "LatencyECDF").store()
                self.connection.exec_query(pfql.connect_performance_artifacts, **{"id1": id1[0]["id"], "id2": id2[0]["id"]})
                for sensor in ecdf.sensors():
                    self.connection.exec_query(pfql.connect_performance_artifact_to_sensor, **{"id1": id2[0]["id"], "sensor":sensor})

    def __add_queues_to_skg(self):
        for queueplot in PizzaPerformanceModuleEcdfs().return_queue_plots():
            id1 = Store_in_db(queueplot, queueplot.return_title(), "Queue").store()
            self.connection.exec_query(pfql.connect_performance_artifact_to_its_main,
                                       **{"kind": "Queue", "id1": id1[0]["id"]})
            for sensor in queueplot.return_sensors():
                self.connection.exec_query(pfql.connect_performance_artifact_to_sensor, **{"id1": id1[0]["id"], "sensor": sensor})

    def __add_flows_to_skg(self):
        counter=0
        for flow in PizzaPerformanceModuleFlows(self.__working_dir).return_flows():
            id1 = Store_in_db(flow, flow.return_title(), "Flow").store()
            self.connection.exec_query(pfql.connect_performance_artifact_to_its_main,
                                       **{"kind": "Flow", "id1": id1[0]["id"]})
            counter+=1
            for sensor in flow.return_sensors():
                self.connection.exec_query(pfql.connect_performance_artifact_to_sensor, **{"id1": id1[0]["id"], "sensor": sensor})

    def __add_utils_to_skg(self):
        return

    def __retrieve_ecdfcs_from_skg(self):
        ecdfcs=[]
        for ecdfcname in Store_in_db.retrieve_names("Latency"):
            ecdfs=[Store_in_db.retrieve(ecdf["ecdf"])
                   for ecdf in self.connection.exec_query(pfql.all_ecdfs_of_an_ecdfc, **{"name": ecdfcname["names"]})]
            ecdfcs.append(Ecdf_collection(ecdfs, ecdfcname["names"]))
        return ecdfcs

    def __retrieve_queues_from_skg(self):
        return [Store_in_db.retrieve(name["names"]) for name in Store_in_db.retrieve_names("Queue")]

    def __retrieve_flows_from_skg(self):
        return [Store_in_db.retrieve(name["names"]) for name in Store_in_db.retrieve_names("Flow")]

    def __retrieve_utils_from_skg(self):
        return []

    def add_performance_to_skg(self):
        print("add_performance_to_skg")
        self.__delete_all_performance_nodes()
        self.__add_main_performance_nodes()
        self.__add_ecdfcs_to_skg()
        self.__add_queues_to_skg()
        self.__add_flows_to_skg()
        self.__add_utils_to_skg()

    def retrieve_performance_from_skg(self):
        print("retrieve_performance_from_skg")
        ecdfcs=self.__retrieve_ecdfcs_from_skg()
        queues=self.__retrieve_queues_from_skg()
        flows=self.__retrieve_flows_from_skg()
        utils=self.__retrieve_utils_from_skg()
        Performance_website(self.__working_dir, ecdfcs, queues, flows, utils).create()
