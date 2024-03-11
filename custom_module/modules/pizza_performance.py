from custom_module.modules.store_in_db import *
from custom_module.modules.pizza_performance_ecdfs import *
from custom_module.cypher_queries.performance_queries import PerformanceQueryLibrary as pfql
from promg import DatabaseConnection

class PizzaPerformanceModule:
    def __init__(self, config):
        self.connection = DatabaseConnection.set_up_connection(config=config)

    def __add_main_performance_nodes(self):
        self.connection.exec_query(pfql.create_main_performance_nodes)

    def __add_ecdfcs_to_skg(self):
        for ecdfc in PizzaPerformanceModuleEcdfs(self.connection).return_ecdfcs():
            id1 = Store_in_db(self.connection,"", ecdfc.return_title(), "Latency").store()
            for ecdf in ecdfc.return_ecdfs():
                id2 = Store_in_db(self.connection,ecdf, ecdf.legend(), "LatencyECDF").store()
                self.connection.exec_query(pfql.connect_performance_artifacts,
                                           **{"id1": id1[0]["id"], "id2": id2[0]["id"]})
                for sensor in ecdf.sensors():
                    self.connection.exec_query(pfql.connect_performance_artifact_to_sensor,
                                               **{"id1": id2[0]["id"], "sensor": sensor})

    def add_performance_to_skg(self):
        print("start add_performance_to_skg")
        self.__add_ecdfcs_to_skg()
        #self.connection.exec_query(pfql.connect_main_performance_nodes_to_children)
        print("finish add_performance_to_skg")

