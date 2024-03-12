from custom_module.modules.pizza_performance_add_metrics import add_metrics
from custom_module.modules.pizza_performance_create_website import Performance_website
from custom_module.modules.store_in_db import *
from custom_module.modules.pizza_performance_ecdfs import *
from custom_module.cypher_queries.performance_queries import PerformanceQueryLibrary as pfql
from promg import DatabaseConnection

class PizzaPerformanceModule:
    def __init__(self, config):
        self.connection = DatabaseConnection.set_up_connection(config=config)

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

    def __retrieve_ecdfcs_from_skg(self):
        ecdfcs = []
        for ecdfcname in Store_in_db.retrieve_names(self.connection,"Latency"):
            ecdfs = [Store_in_db.retrieve(self.connection,ecdf["ecdf"])
                     for ecdf in self.connection.exec_query(pfql.all_ecdfs_of_an_ecdfc, **{"name": ecdfcname["names"]})]
            ecdfcs.append(Ecdf_collection(ecdfs, ecdfcname["names"]))
        return ecdfcs

    def add_performance_to_skg(self):
        print("start add_performance_to_skg")
        self.__add_ecdfcs_to_skg()
        add_metrics(self.connection)
        print("finish add_performance_to_skg")

    def retrieve_performance_from_skg(self,working_dir):
        print("start retrieve_performance_from_skg")
        ecdfcs = self.__retrieve_ecdfcs_from_skg()
        Performance_website(self.connection,working_dir, ecdfcs, [], [], []).create()
        print("finish retrieve_performance_from_skg")

