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
            Ecdf_visualize.plot_to_screen(ecdfc)

    def __add_queues_to_skg(self):
        ppqueue = PizzaPerformanceModuleEcdfs()
        for queueplot in ppqueue.return_queue_plots():
            queueplot.to_screen()

    def add_performance_to_skg(self):
        print("add_performance_to_skg")
        self.__delete_all_performance_nodes()
        self.__add_main_performance_nodes()
        self.__add_ecdfs_to_skg()
        self.__add_queues_to_skg()


