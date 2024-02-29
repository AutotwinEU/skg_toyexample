import pandas as pd

from promg import DatabaseConnection
from promg import Performance
from custom_module.cypher_queries.custom_query_library import CustomCypherQueryLibrary as ccql


class PizzaLineModule:
    def __init__(self, database_connection):
        self.connection = database_connection

    @Performance.track('entity_type')
    def create_station_aggregation(self, entity_type):
        self.connection.exec_query(ccql.get_create_source_station_aggregation_query,
                                   **{"entity_type": entity_type})

        self.connection.exec_query(ccql.get_create_sink_station_aggregation_query,
                                   **{"entity_type": entity_type})
        self.connection.exec_query(ccql.get_create_processing_stations_aggregation_query,
                                   **{"entity_type": entity_type})

    @Performance.track('station_id')
    def infer_part_of_relation(self, station_id):
        # depending on station, we first need to prepare the batching policy
        if station_id in ["PackStation", "BoxStation"]:
            self._determine_start_and_terminor_nodes(station_id=station_id)
            self._determine_part_of_property(station_id=station_id)
            self._determine_number_in_run(station_id=station_id)
            self._create_part_of_relation_fifo_batch(station_id=station_id)
            self._delete_temp_properties(station_id=station_id)
        elif station_id in ["PalletStation"]:
            self._create_part_of_relation_fifo(station_id=station_id)

    def _determine_start_and_terminor_nodes(self, station_id):
        self.connection.exec_query(ccql.get_set_pp_changed_property_query,
                                   **{
                                       "station_id": station_id
                                   }
                                   )
        self.connection.exec_query(ccql.get_determine_pp_changed_query,
                                   **{
                                       "station_id": station_id
                                   }
                                   )

        self.connection.exec_query(ccql.get_set_start_and_terminator_label_based_on_temp_prop_query)
        self.connection.exec_query(ccql.get_set_terminator_label_based_on_end_query,
                                   **{
                                       "station_id": station_id
                                   })

    def _determine_part_of_property(self, station_id):
        self.connection.exec_query(ccql.get_determine_entity_part_of_query,
                                   **{
                                       "station_id": station_id
                                   }
                                   )

    def _determine_number_in_run(self, station_id):
        self.connection.exec_query(ccql.get_determine_number_in_run_query)
        self.connection.exec_query(ccql.get_determine_number_in_run_range_of_exit_stations_query,
                                   **{
                                       "station_id": station_id
                                   }
                                   )

    def _create_part_of_relation_fifo_batch(self, station_id):
        self.connection.exec_query(ccql.get_create_part_of_relation,
                                   **{
                                       "station_id": station_id
                                   })

    def _create_part_of_relation_fifo(self, station_id):
        self.connection.exec_query(ccql.get_create_part_of_fifo_query,
                                   **{
                                       "station_id": station_id
                                   })

    def _delete_temp_properties(self, station_id):
        self.connection.exec_query(ccql.get_delete_temp_properties_query,
                                   **{
                                       "station_id": station_id
                                   })

    @Performance.track()
    def connect_wip_sensor_to_assembly_line(self):
        self.connection.exec_query(ccql.get_connect_wip_sensor_to_assembly_line_query)

    @Performance.track()
    def complete_quality(self):
        self.connection.exec_query(ccql.get_complete_quality_query)
        self.connection.exec_query(ccql.get_create_quality_for_pizzas_query)
        self.connection.exec_query(ccql.get_create_qualifier_rel_to_pizza_quality_query)

    @Performance.track()
    def connect_operators_to_station(self):
        mappings = [
            {
                "operator": 'opBox_onBreak', "station": "BoxStation"
            },
            {
                "operator": 'opPack_onBreak', "station": "PackStation"
            }
        ]
        for mapping in mappings:
            self.connection.exec_query(ccql.get_connect_operators_to_station_query,
                                       **{
                                           "operator": mapping["operator"],
                                           "station": mapping["station"]
                                       })

    @Performance.track()
    def connect_activities_to_location(self):
        self.connection.exec_query(ccql.get_connect_activities_to_location_query)

    @Performance.track()
    def observe_events_to_station_aggregation_query(self):
        self.connection.exec_query(ccql.get_observe_events_to_station_aggregation_query)

    @Performance.track()
    def create_station_entities_and_correlate_to_events(self):
        self.connection.exec_query(ccql.get_create_station_entities_and_correlate_to_events_query)

    @Performance.track()
    def connect_stations_and_sensors(self):
        self.connection.exec_query(ccql.get_connect_stations_queries)
        self.connection.exec_query(ccql.get_connect_sensors_queries)

    @Performance.track()
    def update_sensor_attributes(self):
        self.connection.exec_query(ccql.get_update_sensors_queries)

    @Performance.track()
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

    @Performance.track()
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
