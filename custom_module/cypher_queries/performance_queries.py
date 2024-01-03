from promg import Query


class PerformanceQueryLibrary:
    # creates all the high-level performance nodes
    @staticmethod
    def create_main_performance_nodes():
        # language=sql
        query_str = '''
            CREATE(n1:MainPerformance:Performance),(n2:MainLatency:Performance),(n3:MainUtilization:Performance),
            (n4:MainQueue:Performance),(n5:MainFlow:Performance)
            CREATE(n1)-[:HAS_PERFORMANCE]->(n2),(n1)-[:HAS_PERFORMANCE]->(n3),(n1)-[:HAS_PERFORMANCE]->
            (n4),(n1)-[:HAS_PERFORMANCE]->(n5)'''
        return Query(query_str=query_str)

    # removes all the performance nodes. used before adding performance to SKG.
    @staticmethod
    def delete_all_performance_nodes():
        # language=sql
        query_str = '''MATCH(c:Performance) detach delete c'''
        return Query(query_str=query_str)