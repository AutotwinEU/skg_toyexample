import pandas as pd

from promg import DatabaseConnection
from promg import Performance
from ekg_creator_custom.cypher_queries.custom_query_library import CustomCypherQueryLibrary as ccql


class CustomModule:
    def __init__(self, db_connection: DatabaseConnection, perf: Performance):
        self.connection = db_connection
        self.perf = perf

    def _write_message_to_performance(self, message: str):
        if self.perf is not None:
            self.perf.finished_step(activity=message)

    def do_custom_query(self, query_name, **kwargs):
        func = getattr(self, query_name)
        return func(**kwargs)

    def create_station_aggregation(self, entity_type):
        self.connection.exec_query(ccql.get_create_source_station_aggregation_query,
                                   **{"entity_type": entity_type})

        self.connection.exec_query(ccql.get_create_sink_station_aggregation_query,
                                   **{"entity_type": entity_type})
        self.connection.exec_query(ccql.get_create_processing_stations_aggregation_query,
                                   **{"entity_type": entity_type})

    def complete_corr(self):
        completion_dict = [
            {"entity_type": 'Pizza', "from_activity": "Pass Sensor S4", "to_activity": "Pass Sensor S5"},
            {"entity_type": 'Pack', "from_activity": "Pass Sensor S8", "to_activity": "Pass Sensor S9"},
            {"entity_type": 'Box', "from_activity": "Pass Sensor S10", "to_activity": "Pass Sensor S13"}
        ]
        for dict in completion_dict:
            self.connection.exec_query(ccql.get_complete_corr_query,
                                       **{
                                           "entity_type": dict["entity_type"],
                                           "from_activity": dict["from_activity"],
                                           "to_activity": dict["to_activity"]
                                       })

        self.connection.exec_query(ccql.get_reset_used_prop_query)

    def connect_activities_to_location(self):
        self.connection.exec_query(ccql.get_connect_activities_to_location_query)

    def observe_events_to_station_aggregation_query(self):
        self.connection.exec_query(ccql.get_observe_events_to_station_aggregation_query)

    def create_station_entities_and_correlate_to_events(self):
        self.connection.exec_query(ccql.get_create_station_entities_and_correlate_to_events_query)

    def connect_stations_and_sensors(self):
        self.connection.exec_query(ccql.get_connect_stations_queries)
        self.connection.exec_query(ccql.get_connect_sensors_queries)

    def update_sensor_attributes(self):
        self.connection.exec_query(ccql.get_update_sensors_queries)

    def read_log(self):
        data = self.connection.exec_query(ccql.get_read_log_query)
        i = 0
        while i < len(data):
            if data[i]['station_type'] == 'Source':
                for j in range(i - 1, -1, -1):
                    if data[j]['station'] == data[i]['station']:
                        data.insert(j + 1, data[i].copy())
                        data[j + 1]['time'] = data[j]['time']
                        data[j + 1]['activity'] = 'ENTER'
                        # new entry is added before i, hence i moves with 1
                        i += 1
                        break
            elif data[i]['station_type'] == 'Sink':
                data.insert(i + 1, data[i].copy())
                data[i + 1]['activity'] = 'EXIT'
                # new entry does not have to be checked, hence increase i already with 1
                i += 1
            i += 1
        log = pd.DataFrame.from_records(data)
        log = log.loc[:, ['time', 'station', 'part', 'activity']]
        return log

    def write_attributes(self, graph):
        for station, attributes in graph.nodes.items():
            buffer_capacity = attributes['buffer_capacity']
            machine_capacity = attributes['machine_capacity']
            processing_time = attributes['processing_time']
            self.connection.exec_query(ccql.get_write_attributes_to_stations,
                                       **{
                                           "station": station,
                                           "buffer_capacity": buffer_capacity,
                                           "machine_capacity": machine_capacity,
                                           "processing_time": processing_time
                                       })

        for connection, attributes in graph.edges.items():
            routing_probability = attributes['routing_probability']
            transfer_time = attributes['transfer_time']
            self.connection.exec_query(ccql.get_write_attributes_to_connections,
                                       **{
                                           "connection": connection,
                                           "routing_probability": routing_probability,
                                           "transfer_time": transfer_time
                                       })
