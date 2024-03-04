from typing import Optional, List

from promg import Performance
from promg.data_managers.semantic_header import NodeConstructor, RelationConstructor

from custom_module.cypher_queries.delete_data_query_library import DeleteDataQueryLibrary as ddql


class DeleteModule:
    def __init__(self, db_connection, semantic_header):
        self.connection = db_connection
        self.semantic_header = semantic_header

    @Performance.track("logs")
    def delete_records(self, logs):
        self.mark_delete_nodes_record_layer(logs)
        self.mark_delete_nodes_semantic_layer()
        self.delete_marked_nodes()

    def mark_delete_nodes_record_layer(self, logs):
        self.connection.exec_query(ddql.get_mark_delete_records_by_log_query,
                                   **{
                                       "logs": logs
                                   })

    def mark_delete_nodes_semantic_layer(self, node_types: Optional[List[str]] = None):
        for node_constructor in self.semantic_header.get_node_by_record_constructors(node_types):
            self.delete_node_by_record(node_constructor)
        for relation_constructor in self.semantic_header.get_node_relation_constructors():
            self.mark_delete_node_relation(relation_constructor)
        self.mark_delete_connection_nodes()
        self.mark_pizza_quality_attributes()

    def delete_node_by_record(self, node_constructor: NodeConstructor):
        self.connection.exec_query(ddql.get_mark_nodes_constructed_by_records_to_be_deleted_query,
                                   **{
                                       "node_constructor": node_constructor
                                   })

    def mark_delete_node_relation(self, relation_constructor: RelationConstructor):
        self.connection.exec_query(ddql.get_mark_node_relations_to_be_deleted_query,
                                   **{
                                       "relation_constructor": relation_constructor
                                   })

    def mark_delete_connection_nodes(self):
        self.connection.exec_query(ddql.get_mark_connection_nodes_to_be_deleted_query)

    def mark_pizza_quality_attributes(self):
        self.connection.exec_query(ddql.get_mark_pizza_quality_attributes_query)

    def delete_marked_nodes(self):
        self.connection.exec_query(ddql.get_delete_marked_nodes_query)
