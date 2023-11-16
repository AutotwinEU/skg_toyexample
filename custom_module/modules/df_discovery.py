from typing import Optional, List

import pandas as pd

from promg import DatabaseConnection
from promg import Performance
from promg.data_managers.semantic_header import ConstructedNodes

from custom_module.cypher_queries.df_discovery_query_library import DFDiscoveryQueryLibrary as dfql


class DFDiscoveryModule:
    def __init__(self):
        self.connection = DatabaseConnection()

    @Performance.track("entity_type")
    def create_df_edges_for_entity(self, entity_type: str, df_label: str, include_sys_id: bool = False,
                                   cor_type: str = None, event_label: str = None, version_number: str = None):
        if event_label is None:
            event_label = "Event"

        if "CompoundEvent" in event_label:
            self.connection.exec_query(dfql.get_create_df_compound_events_query,
                                       **{
                                           "entity_type": entity_type,
                                           "cor_type": cor_type,
                                           "event_label": event_label,
                                           "df_label": df_label,
                                           "include_sys_id": include_sys_id,
                                           "version_number": version_number
                                       })
        else:
            self.connection.exec_query(dfql.get_create_df_atomic_events_query,
                                       **{
                                           "entity_type": entity_type,
                                           "cor_type": cor_type,
                                           "event_label": event_label,
                                           "df_label": df_label,
                                           "include_sys_id": include_sys_id,
                                           "version_number": version_number
                                       })

    @Performance.track("node")
    def merge_duplicate_df_for_node(self, node_type: str, df_label: str, version_number: str = None):
        self.connection.exec_query(dfql.get_merge_duplicate_df_entity_query, **{
            "node_type": node_type,
            "df_label": df_label,
            "version_number": version_number
        })

    @Performance.track()
    def delete_df_edges(self, df_label: str, entity_type: str, version_number: str):
        self.connection.exec_query(dfql.get_delete_df_query,
                                   **{
                                       "df_label": df_label,
                                       "entity_type": entity_type,
                                       "version_number": version_number
                                   })

    # def delete_parallel_dfs_derived(self):
    #     node: ConstructedNodes
    #     original_entity: ConstructedNodes
    #     relation: Relationship
    #     node_constructor: NodeConstructor
    #     for _type, node_constructor in self.semantic_header.get_nodes_constructed_by_relations(
    #             only_include_delete_parallel_df=True).items():
    #         self._delete_parallel_dfs_derived_for_node(node=node_constructor, type=_type)
    #
    # @Performance.track("type")
    # def _delete_parallel_dfs_derived_for_node(self, node: NodeConstructor, type: str):
    #     from_node = node.relation.from_node
    #     to_node = node.relation.to_node
    #     for node in [from_node, to_node]:
    #         self.connection.exec_query(sh_ql.delete_parallel_directly_follows_derived,
    #                                    **{
    #                                        "type": type,
    #                                        "node": node
    #                                    })
