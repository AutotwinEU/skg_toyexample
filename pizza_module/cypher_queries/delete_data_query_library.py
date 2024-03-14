from promg import Query


class DeleteDataQueryLibrary:
    @staticmethod
    def get_mark_delete_records_by_log_query(logs):
        log_str = ",".join([f'"{log}"' for log in logs])

        # language=sql
        query_str = '''
                CALL apoc.periodic.commit(
                'MATCH (r:Record)
                WHERE r.log in [$log_str] AND r.markForDeletion is Null
                WITH r limit $limit
                SET r.markForDeletion = True
                RETURN count(*)',
                {limit:$limit})
            '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "log_str": log_str
                     })

    @staticmethod
    def get_mark_nodes_constructed_by_records_to_be_deleted_query(node_constructor):
        # language=sql
        query_str = '''
                    CALL apoc.periodic.commit(
                    'MATCH ($node_pattern) - [:EXTRACTED_FROM] -> (r:Record)
                    WITH n, collect(distinct COALESCE(r.markForDeletion, false)) as records_deleted 
                    WHERE records_deleted = [true] // check whether all Record nodes marked for deletion
                    AND n.markForDeletion is Null // check to make sure we are not in an infinite loop
                    WITH n limit $limit
                    SET n.markForDeletion = True
                    RETURN count(*)',
                    {limit:$limit})
                '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "node_pattern": node_constructor.get_pattern(name='n', with_properties=False)
                     })

    @staticmethod
    def get_mark_node_relations_to_be_deleted_query(relation_constructor):
        # language=sql
        query_str = '''
                    CALL apoc.periodic.commit(
                    'MATCH (from) - [:FROM] -> ($relation_pattern) - [:TO] -> (to)
                    // this is a relation node, so if either from or to is marked for deletion, the relation node should 
                    // also be deleted
                    WHERE (from.markForDeletion OR to.markForDeletion)
                    AND n.markForDeletion is NULL // check to make sure we are not in an infinite loop
                    WITH n limit $limit
                    SET n.markForDeletion = True
                    RETURN count(*)',
                    {limit:$limit})
                '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "relation_pattern": relation_constructor.get_pattern(name='n', exclude_nodes=True,
                                                                              with_brackets=False,
                                                                              with_properties=False)
                     })

    @staticmethod
    def get_mark_connection_nodes_to_be_deleted_query():
        # language=sql
        query_str = '''
                        CALL apoc.periodic.commit(
                        'MATCH (from) - [:ORIGIN] -> (n:Connection) - [:DESTINATION] -> (to)
                        // this is a relation node, so if either from or to is marked for deletion, the relation node 
                        // should also be deleted
                        WHERE (from.markForDeletion OR to.markForDeletion)
                        AND n.markForDeletion is NULL // check to make sure we are not in an infinite loop
                        WITH n limit $limit
                        SET n.markForDeletion = True
                        RETURN count(*)',
                        {limit:$limit})
                    '''

        return Query(query_str=query_str)

    @staticmethod
    def get_mark_pizza_quality_attributes_query():
        # language=sql
        query_str = '''
                        CALL apoc.periodic.commit(
                        'MATCH (pq:PizzaQualityAttribute) <- [:HAS_PROPERTY] - (p:Pizza)
                        // pizza quality attribute only can exist if pizza exists
                        WHERE p.markForDeletion
                        AND pq.markForDeletion is NULL // check to make sure we are not in an infinite loop
                        WITH pq limit $limit
                        SET pq.markForDeletion = True
                        RETURN count(*)',
                        {limit:$limit})
                    '''

        return Query(query_str=query_str)

    @staticmethod
    def get_delete_marked_nodes_query() -> Query:
        # language=sql
        query_str = '''
                    CALL apoc.periodic.commit(
                    'MATCH (n {markForDeletion: True})
                    WITH n limit $limit
                    DETACH DELETE n
                    RETURN count(*)',
                    {limit:$limit})
                '''

        return Query(query_str=query_str)
