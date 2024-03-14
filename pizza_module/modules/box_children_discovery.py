from promg import Performance
from pizza_module.cypher_queries.determine_box_children_query_library import BoxCypherQueryLibrary as bcql


class BoxChildrenModule:
    def __init__(self, db_connection, is_simulated=False):
        self.connection = db_connection
        self.is_simulated = is_simulated

    @Performance.track()
    def create_box_children(self):
        self._create_box_event_labels()
        self._create_box_children()
        self._delete_box_event_labels()

    def _create_box_event_labels(self):
        self.connection.exec_query(bcql.get_set_box_event_labels_based_on_activity_query,
                                   **{"is_simulated": self.is_simulated})
        self.connection.exec_query(bcql.get_set_box_event_labels_based_on_first_event_query,
                                   **{"is_simulated": self.is_simulated}
                                   )
        self.connection.exec_query(bcql.get_set_box_event_labels_based_on_last_event_query,
                                   **{"is_simulated": self.is_simulated}
                                   )

    def _create_box_children(self):
        self.connection.exec_query(bcql.get_create_box_children_query,
                                   **{"is_simulated": self.is_simulated})
        self.connection.exec_query(bcql.get_create_box_single_children_query,
                                   **{"is_simulated": self.is_simulated})

    def _delete_box_event_labels(self):
        self.connection.exec_query(bcql.get_delete_box_event_labels_query)

    @Performance.track()
    def create_df_box_children(self):
        self.connection.exec_query(bcql.get_create_df_path_boxes_query,
                                   **{"is_simulated": self.is_simulated})

    @Performance.track()
    def create_run_id_children(self):
        self.connection.exec_query(bcql.get_create_run_id_children_query,
                                   **{"is_simulated": self.is_simulated})

    @Performance.track()
    def create_extracted_from_record_query(self):
        self.connection.exec_query(bcql.get_create_extracted_from_record_query,
                                   **{"is_simulated": self.is_simulated})
