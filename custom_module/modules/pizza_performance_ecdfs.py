from promg import DatabaseConnection
from custom_module.cypher_queries.performance_queries import PerformanceQueryLibrary as pfql
from custom_module.modules.ecdf_library import *
from custom_module.modules.plot import *

class PizzaPerformanceModuleEcdfs:
    def __init__(self):
        self.connection = DatabaseConnection()

    def ecdfc_latency_between_sensors(self, isensor, osensor):
        exec_times = self.connection.exec_query(pfql.execution_times_between_sensors,
                                                **{
                                                    "isensor": isensor,
                                                    "osensor": osensor
                                                })
        ecdf = Ecdf(exec_times[0]["times"], "Execution time between " + isensor + " " + osensor, [isensor] + [osensor])
        return Ecdf_collection([ecdf], isensor + " " + osensor)

    def create_ecdf_collections_for_latencies(self):
        ecdfcs = []
        sensor_connections = self.connection.exec_query(pfql.retrieve_sensor_connections)
        sensor_connections_full_path = self.connection.exec_query(pfql.retrieve_sensor_connections_full_path)
        for sensors in sensor_connections + sensor_connections_full_path:
            for osensor in sensors["outputs"]:
                ecdfcs.append(self.ecdfc_latency_between_sensors(sensors["input"], osensor))
        return ecdfcs

    # returns one queue plot for an isensor and corresponding osensor(s)
    def retrieve_plot_with_queue_size_at_timestamp(self, iosensors):
        timestampsi = self.connection.exec_query(pfql.timestamps_for_a_sensor, **{"sensor": iosensors["input"]})[0]["times"]
        timestampso = []
        for osensor in iosensors["outputs"]:
            timestampso += self.connection.exec_query(pfql.timestamps_for_a_sensor, **{"sensor": osensor})[0]["times"]

        queue_size=0
        xs=[]
        ys=[]
        for timestamp in sorted(list(set(timestampsi + timestampso))):
            queue_size += timestampsi.count(timestamp)
            queue_size -= timestampso.count(timestamp)
            xs.append(timestamp)
            ys.append(queue_size)
        return Plot(xs, ys, "Queue size (y-axis) between " + iosensors["input"] + " and sensors that follow at a time (x-axis).",
                    [iosensors["input"]] + iosensors["outputs"])

    # returns the queue plots for all the isensors and corresponding osensors
    def retrieve_all_plots_and_sensors(self):
        return [self.retrieve_plot_with_queue_size_at_timestamp(iosensors)
                for iosensors in self.connection.exec_query(pfql.retrieve_sensor_connections)]

    # returns one Ecdfc plot for an isensor and corresponding osensor(s)
    # the timestamps are neglected, only the change of the queue size is considered
    def retrieve_ecdf_of_queue_sizes(self, iosensors):
        timestampsi = self.connection.exec_query(pfql.timestamps_for_a_sensor, **{"sensor": iosensors["input"]})[0]["times"]
        timestampso = []
        for osensor in iosensors["outputs"]:
            timestampso += self.connection.exec_query(pfql.timestamps_for_a_sensor, **{"sensor": osensor})[0]["times"]

        queues = []
        queue = 0
        for timestamp in sorted(list(set(timestampsi + timestampso))):
            queue += timestampsi.count(timestamp)
            queue -= timestampso.count(timestamp)
            queues.append(queue)
        return Ecdf_collection([Ecdf(queues, "Ecdf of the queue size of " + iosensors["input"],
                                     [iosensors["input"]] + iosensors["outputs"])],
                                     "Ecdfc of the queue size of " + iosensors["input"])

    def create_ecdf_collections_for_queues(self):
        return [self.retrieve_ecdf_of_queue_sizes(iosensors)
                for iosensors in self.connection.exec_query(pfql.retrieve_sensor_connections)]

    def return_ecdfcs(self):
        return self.create_ecdf_collections_for_latencies() + self.create_ecdf_collections_for_queues()

    def return_queue_plots(self):
        return self.retrieve_all_plots_and_sensors()
