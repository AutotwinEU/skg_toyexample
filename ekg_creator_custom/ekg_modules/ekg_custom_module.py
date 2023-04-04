from ekg_creator.database_managers.db_connection import DatabaseConnection
from ekg_creator.utilities.performance_handling import Performance
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
        func(**kwargs)

    def create_station_aggregation(self, entity_type):
        self.connection.exec_query(ccql.get_create_source_station_aggregation_query,
                                   **{"entity_type": entity_type})

        self.connection.exec_query(ccql.get_create_sink_station_aggregation_query,
                                   **{"entity_type": entity_type})
        self.connection.exec_query(ccql.get_create_processing_stations_aggregation_query,
                                   **{"entity_type": entity_type})

    def observe_events_to_station_aggregation_query(self):
        self.connection.exec_query(ccql.get_observe_events_to_station_aggregation_query)

    def create_station_entities_and_correlate_to_events(self):
        self.connection.exec_query(ccql.get_create_non_processing_station_entities_and_correlate_to_events_query)
        self.connection.exec_query(ccql.get_create_non_processing_station_entities_and_correlate_to_events_query)
