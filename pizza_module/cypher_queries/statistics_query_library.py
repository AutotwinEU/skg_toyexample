from promg import Query

# EV: Copied from v4

class StatisticsQueryLibrary:
    @staticmethod
    def get_record_layer_statistics():
        query_str = '''
            MATCH (r:Record)
            WITH r.log as log, count(r) as numberOfNodes, CASE 
            WHEN r.log CONTAINS "sim" THEN TRUE
            ELSE FALSE
            END AS is_simulated
            RETURN log, is_simulated, numberOfNodes ORDER BY log
        '''

        return Query(query_str=query_str)

    @staticmethod
    def get_node_count_query() -> Query:
        # language=SQL
        query_str = '''
                    // List all node types and counts
                    MATCH (n) 
                    WHERE not "Record" in labels(n)
                    WITH  labels(n) AS labels,  count(n) AS numberOfNodes, CASE
                    WHEN n.simulated THEN TRUE
                    ELSE FALSE
                    END AS is_simulated
                    RETURN labels, is_simulated, numberOfNodes ORDER BY labels[0]
                '''

        return Query(query_str=query_str)

    @staticmethod
    def get_edge_count_query() -> Query:
        # language=SQL
        query_str = '''
                    // List all rel types and counts
                    MATCH (from) - [r] -> (to)
                    WHERE type(r) <> "EXTRACTED_FROM"
                    // WHERE r.type is  NULL
                    WITH Type(r) as type, count(r) as numberOfRelations, CASE
                    WHEN from.simulated OR to.simulated THEN TRUE
                    ELSE FALSE
                    END AS is_simulated
                    RETURN type, is_simulated, numberOfRelations ORDER BY type
                '''

        return Query(query_str=query_str)
