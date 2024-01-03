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

    # retrieves a lists with input sensors and corresponding output sensor(s)
    @staticmethod
    def retrieve_sensor_connections():
        # language=sql
        query_str = '''match (s1:Sensor) match (s1)-[:CONN]->(s2) 
                       return s1.sysId as input, collect(s2.sysId) as outputs'''
        return Query(query_str=query_str)

    # retrieves a lists with input sensors and corresponding output sensors, which are all full path
    @staticmethod
    def retrieve_sensor_connections_full_path():
        # language=sql
        query_str = ''' match (s1:Sensor) match (s1)-[:CONN*]->(s2)
                where not exists ((:Sensor)-[:CONN]->(s1)) and not exists ((s2)-[:CONN]->(:Sensor))
                return s1.sysId as input, collect(s2.sysId) as outputs'''
        return Query(query_str=query_str)

    # retrieves for a sensor pair, all the execution times between them
    @staticmethod
    def execution_times_between_sensors(isensor, osensor):
        query_str = '''MATCH path=(ev:Event)- [:DF_PIZZA|DF_PACK|DF_BOX|DF_PALLET*]->(g:Event)
                MATCH (ev)-[:ACTS_ON]->(p:Pizza)
                WHERE NOT EXISTS((:Event)-[:DF_PIZZA|DF_PACK|DF_BOX|DF_PALLET]->(ev))
                AND NOT EXISTS((g)-[:DF_PIZZA|DF_PACK|DF_BOX|DF_PALLET]->(:Event))
                UNWIND nodes(path) as e1
                UNWIND nodes(path) as e2
                WITH p,e1,e2
                match (e1)-[:EXECUTED_BY]->(s1)
                match (e2)-[:EXECUTED_BY]->(s2)
                WHERE s1.sysId="$isensor" and s2.sysId="$osensor" and s1.sysId is not null and s2.sysId is not null 
                WITH COLLECT (e2.timestamp-e1.timestamp) as times
                return times'''
        return Query(query_str=query_str,
                     template_string_parameters={"isensor": isensor,
                                                 "osensor": osensor}
                     )

    # retrieves for a sensor, all the execution times on which activity takes place
    @staticmethod
    def timestamps_for_a_sensor(sensor):
        query_str = '''MATCH path=(ev:Event)- [:DF_PIZZA|DF_PACK|DF_BOX|DF_PALLET*]->(g:Event)
                MATCH (ev)-[:ACTS_ON]->(p:Pizza)
                WHERE NOT EXISTS((:Event)-[:DF_PIZZA|DF_PACK|DF_BOX|DF_PALLET]->(ev))
                AND NOT EXISTS((g)-[:DF_PIZZA|DF_PACK|DF_BOX|DF_PALLET]->(:Event))
                UNWIND nodes(path) as e
                WITH p,e
                match (e)-[:EXECUTED_BY]->(s)
                WHERE s.sysId="$sensor"
                WITH COLLECT(e.timestamp) as times
                return times'''
        return Query(query_str=query_str,
                     template_string_parameters={"sensor": sensor}
                     )
