from promg import DatabaseConnection
from custom_module.cypher_queries.performance_queries import PerformanceQueryLibrary as pfql
from custom_module.modules.ecdf_library import *


class PizzaPerformanceModuleEcdfs:
    def __init__(self):
        self.connection = DatabaseConnection()

    def ecdfc_between_sensors(self, isensor, osensor):
        exec_times = self.connection.exec_query(pfql.execution_times_between_sensors,
                                                **{
                                                    "isensor": isensor,
                                                    "osensor": osensor
                                                })
        ecdf = Ecdf(exec_times[0]["times"], "Execution time between " + isensor + " " + osensor, [isensor] + [osensor])
        return Ecdf_collection([ecdf], isensor + " " + osensor)

    def create_ecdf_collections(self):
        ecdfcs = []
        sensor_connections = self.connection.exec_query(pfql.retrieve_sensor_connections)
        sensor_connections_full_path = self.connection.exec_query(pfql.retrieve_sensor_connections_full_path)
        for sensors in sensor_connections + sensor_connections_full_path:
            for osensor in sensors["outputs"]:
                ecdfcs.append(self.ecdfc_between_sensors(sensors["input"], osensor))
        return ecdfcs

    def return_ecdfcs(self):
        return self.create_ecdf_collections()
