from typing import List, Dict, Optional
from pizza_module.cypher_queries.statistics_query_library import StatisticsQueryLibrary as sql

# EV: Copied from v4.

class StatisticsMethod:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def get_log_statistics(self) -> List[Dict[str, any]]:
        """
        Get the count of nodes per label and the count of relationships per type

        Returns:
            A list containing dictionaries with the label/relationship and its count
        """

        def make_empty_list_if_none(_list: Optional[List[Dict[str, str]]]):
            if _list is not None:
                return _list
            else:
                return []

        record_count = self.db_connection.exec_query(sql.get_record_layer_statistics)

        result = make_empty_list_if_none(record_count)

        return result

    def get_statistics(self) -> List[Dict[str, any]]:
        """
        Get the count of nodes per label and the count of relationships per type

        Returns:
            A list containing dictionaries with the label/relationship and its count
        """

        def make_empty_list_if_none(_list: Optional[List[Dict[str, str]]]):
            if _list is not None:
                return _list
            else:
                return []

        record_count = self.db_connection.exec_query(sql.get_record_layer_statistics)
        node_count = self.db_connection.exec_query(sql.get_node_count_query)
        edge_count = self.db_connection.exec_query(sql.get_edge_count_query)

        result = \
            make_empty_list_if_none(record_count) + \
            make_empty_list_if_none(node_count) + \
            make_empty_list_if_none(edge_count)

        return result
