from string import Template

from promg import Query
from promg.data_managers.semantic_header import ConstructedNodes
class DFDiscoveryQueryLibrary:

    @staticmethod
    def get_create_df_compound_events_query(entity_type: str, cor_type: str, event_label: str, df_label: str,
                                            include_sys_id: bool) -> Query:
        # find the specific entities and events with a certain label correlated to that entity
        # order all events by time, order_nr and id grouped by a node n
        # collect the sorted nodes as a list
        # unwind the list from 0 to the one-to-last node
        # find neighbouring nodes and add an edge between

        # language=sql
        include_sys_id_string = "SET df.entityId = n.sysId" if include_sys_id else ""
        cor_relation = f"[:{cor_type}]" if cor_type is not None else ""

        # language=sql
        query_str = '''
                     CALL apoc.periodic.iterate(
                     'MATCH (n:$entity_type) <-$cor_relation - (e:$event_label)
                     CALL {
                        WITH e
                        MATCH (e) - [:CONSISTS_OF] -> (single_event:Event)
                        RETURN id(single_event) as min_id ORDER BY id(single_event)
                        LIMIT 1
                    }
                    WITH n , e as nodes ORDER BY e.timestamp, min_id
                    WITH n , collect (nodes) as nodeList
                    UNWIND range(0,size(nodeList)-2) AS i
                    WITH n , nodeList[i] as first, nodeList[i+1] as second
                    RETURN n, first, second',
                    'MERGE (first) -[df:$df_label {entityType: "$entity_type"}]->(second)
                    SET df.type = "DF"
                    $include_sys_id_string',
                    {batchSize: $batch_size})
                    '''

        query_str = Template(query_str).safe_substitute(include_sys_id_string=include_sys_id_string,
                                                        cor_relation=cor_relation)

        return Query(query_str=query_str,
                     template_string_parameters={
                         "corr_type_string": cor_type,
                         "event_label": event_label,
                         "df_label": df_label,
                         "entity_type": entity_type
                     })

    @staticmethod
    def get_create_df_atomic_events_query(entity_type: str, event_label: str, df_label: str,
                                          include_sys_id: bool, cor_type: str) -> Query:
        # find the specific entities and events with a certain label correlated to that entity
        # order all events by time, order_nr and id grouped by a node n
        # collect the sorted nodes as a list
        # unwind the list from 0 to the one-to-last node
        # find neighbouring nodes and add an edge between

        # language=sql
        include_sys_id_string = "SET df.entityId = n.sysId" if include_sys_id else ""
        cor_relation = f"[:{cor_type}]" if cor_type is not None else ""

        # language=sql
        query_str = '''
                 CALL apoc.periodic.iterate(
                    'MATCH (n:$entity_type) <- $cor_relation - (e:$event_label)
                    WITH n , e as nodes ORDER BY e.timestamp, ID(e)
                    WITH n , collect (nodes) as nodeList
                    UNWIND range(0,size(nodeList)-2) AS i
                    WITH n , nodeList[i] as first, nodeList[i+1] as second
                    RETURN n, first, second',
                    'MERGE (first) -[df:$df_label {entityType: "$entity_type"}]->(second)
                     SET df.type = "DF"
                    $include_sys_id_string',
                    {batchSize: $batch_size})
                '''

        query_str = Template(query_str).safe_substitute(include_sys_id_string=include_sys_id_string,
                                                        cor_relation=cor_relation)

        return Query(query_str=query_str,
                     template_string_parameters={
                         "entity_type": entity_type,
                         "corr_type_string": cor_type,
                         "event_label": event_label,
                         "df_label": df_label
                     })

    @staticmethod
    def get_merge_duplicate_df_entity_query(node_type: str, df_label: str) -> Query:
        # language=sql
        query_str = '''
                            MATCH (n1:Event)-[r:$df_label {entityType: '$entity_type'}]->(n2:Event)
                            WITH n1, n2, collect(r) AS rels
                            WHERE size(rels) > 1
                            // only include this and the next line if you want to remove the existing relationships
                            UNWIND rels AS r 
                            DELETE r
                            MERGE (n1)
                                -[:$df_label {entityType: '$entity_type', count:size(rels), type: 'DF'}]->
                                  (n2)
                        '''
        return Query(query_str=query_str,
                     template_string_parameters={
                         "entity_type": node_type,
                         "df_label": df_label
                     })

    @staticmethod
    def delete_parallel_directly_follows_derived(old_node: ConstructedNodes, df_label_old: str,
                                                 new_node: ConstructedNodes, df_label_new: str):
        # language=sql
        query_str = '''
                MATCH (e1:Event) -[df:$df_label_old {entityType: "$old_entity_type"}]-> (e2:Event)
                WHERE (e1:Event) -[:$df_label_new {entityType: "$new_entity_type"}]-> (e2:Event)
                DELETE df'''
        return Query(query_str=query_str,
                     template_string_parameters={
                         "old_entity_type": old_node.node_type,
                         "new_entity_type": new_node.node_type,
                         "df_label_old": df_label_old,
                         "df_label_new": df_label_new
                     },
                     parameters={})

    @staticmethod
    def get_delete_df_query(df_label: str, entity_type: str = None):
        entity_type = f"{{entityType: '{entity_type}'}}" if entity_type is not None else ""

        query_str = '''
            MATCH (e:Event) - [df:$df_label $entity_type] -> (f:Event)
            DELETE df
        '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "df_label": df_label,
                         "entity_type": entity_type
                     })
