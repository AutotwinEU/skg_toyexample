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

    def create_ecdf_collections_for_queues(self):
        return []

    # returns one queue plot for an isensor and corresponding osensor(s)
    def retrieve_plot_with_queue_size_at_timestamp(self, iosensors):
        timestampsi = self.connection.exec_query(pfql.timestamps_for_a_sensor, **{"sensor": iosensors["input"]})[0]["times"]
        timestampso = []
        for osensor in iosensors["outputs"]:
            timestampso += self.connection.exec_query(pfql.timestamps_for_a_sensor, **{"sensor": osensor})[0]["times"]

        queue_size = 0
        xs = [0]
        ys = [0]
        for timestamp in sorted(timestampsi + timestampso):
            queue_size += timestampsi.count(timestamp)
            queue_size -= timestampso.count(timestamp)
            xs.append(timestamp)
            ys.append(queue_size)
        return Plot(xs, ys, "Queue size (y-axis) between " + iosensors["input"] + " and sensors that follow at a time (x-axis).",
                    [iosensors["input"]] + iosensors["outputs"])

    # returns the queue plots for all the isensors and corresponding osensors
    def retrieve_all_plots_and_sensors(self):
        plots = []
        for iosensors in self.connection.exec_query(pfql.retrieve_sensor_connections):
            plot = self.retrieve_plot_with_queue_size_at_timestamp(iosensors)
            if plot.all_positive_values():
                plots.append(plot)
        return plots

    def return_ecdfcs(self):
        return self.create_ecdf_collections_for_latencies() + self.create_ecdf_collections_for_queues()

    def return_plots(self):
        return self.retrieve_all_plots_and_sensors()
