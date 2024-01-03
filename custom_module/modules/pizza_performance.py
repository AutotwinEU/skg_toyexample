from promg import DatabaseConnection
from custom_module.cypher_queries.performance_queries import PerformanceQueryLibrary as pfql


class PizzaPerformanceModule:
    def __init__(self):
        self.connection = DatabaseConnection()

    def __delete_all_performance_nodes(self):
        self.connection.exec_query(pfql.delete_all_performance_nodes)

    def __add_main_performance_nodes(self):
        self.connection.exec_query(pfql.create_main_performance_nodes)

    def add_performance_to_skg(self):
        print("add_performance_to_skg")
        self.__delete_all_performance_nodes()
        self.__add_main_performance_nodes()


