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
        query_str = '''match (s1:Sensor) match (s1)-[:ORIGIN] ->(:Connection) - [:DESTINATION]->(s2) 
                       return s1.sysId as input, collect(s2.sysId) as outputs'''
        return Query(query_str=query_str)

    # retrieves a lists with input sensors and corresponding output sensors, which are all full path
    @staticmethod
    def retrieve_sensor_connections_full_path():
        # language=sql
        query_str = ''' match (s1:Sensor) match (s1)-[:DF_SENSOR*]->(s2)
                where not exists ((:Sensor)-[:DF_SENSOR]->(s1)) and not exists ((s2)-[:DF_SENSOR]->(:Sensor))
                return s1.sysId as input, collect(s2.sysId) as outputs'''
        return Query(query_str=query_str)

    # retrieves for a sensor pair, all the execution times between them
    @staticmethod
    def execution_times_between_sensors(isensor, osensor):
        query_str = '''MATCH path=(ev:Event)- [:DF_CONTROL_FLOW_ITEM*]->(g:Event)
                MATCH (ev)-[:ACTS_ON]->(p:Pizza)
                WHERE NOT EXISTS((:Event)-[:DF_CONTROL_FLOW_ITEM]->(ev))
                AND NOT EXISTS((g)-[:DF_CONTROL_FLOW_ITEM]->(:Event))
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
        query_str = '''MATCH path=(ev:Event)- [:DF_CONTROL_FLOW_ITEM*]->(g:Event)
                MATCH (ev)-[:ACTS_ON]->(p:Pizza)
                WHERE NOT EXISTS((:Event)-[:DF_CONTROL_FLOW_ITEM]->(ev))
                AND NOT EXISTS((g)-[:DF_CONTROL_FLOW_ITEM]->(:Event))
                UNWIND nodes(path) as e
                WITH p,e
                match (e)-[:EXECUTED_BY]->(s)
                WHERE s.sysId="$sensor"
                WITH COLLECT(e.timestamp) as times
                return times'''
        return Query(query_str=query_str,
                     template_string_parameters={"sensor": sensor}
                     )

    # stores a performance artifact of a certain kind with a value in the database
    @staticmethod
    def store_in_db(kind, name, value):
        query_str = '''create(n1:$kind:Performance{name:"$name",val:"$value"})
                RETURN id(n1) as id'''
        return Query(query_str=query_str,
                     template_string_parameters={"kind": kind, "name":name, "value": value}
                     )

    # retrieves a performance artifact based on a name
    @staticmethod
    def retrieve_from_db(name):
        query_str = '''match(n:Performance{name:"$name"}) return n.val as value'''
        return Query(query_str=query_str,
                     template_string_parameters={"name": name}
                     )

    # retrieves a list of performance artifact names from the db
    @staticmethod
    def retrieve_performance_artifacts_from_db(kind):
        query_str = '''match(n: $kind:Performance) return n.name as names'''
        return Query(query_str=query_str,
                     template_string_parameters={"kind": kind}
                     )

    # connects two performance artifacts
    @staticmethod
    def connect_performance_artifacts(id1, id2):
        query_str = '''MATCH(n1) MATCH(n2)
                    WHERE ID(n1) = $id1 AND ID(n2) = $id2
                    CREATE(n1) - [: HAS_PERFORMANCE]->(n2)'''
        return Query(query_str=query_str,
                     template_string_parameters={"id1": id1, "id2": id2}
                     )

    @staticmethod
    def connect_performance_artifacts_by_name(name1, name2):
        query_str = '''MATCH(n1) MATCH(n2)
                    WHERE n1.name = "$name1" AND n2.name = "$name2"
                    CREATE(n1) - [: HAS_PERFORMANCE]->(n2)'''
        return Query(query_str=query_str,
                     template_string_parameters={"name1": name1, "name2": name2}
                     )

    # connects a performance artifact to its main artifact
    @staticmethod
    def connect_performance_artifact_to_its_main(id1, kind):
        query_str = '''MATCH (p1:Main$kind) 
                       MATCH (p2)
                       WHERE ID(p2) = $id1 
                       CREATE(p1) - [: HAS_PERFORMANCE]->(p2)'''
        return Query(query_str=query_str,
                     template_string_parameters={"id1": id1, "kind": kind}
                     )

    # connects a performance artifact to a sensor
    @staticmethod
    def connect_performance_artifact_to_sensor(id1, sensor):
        query_str = '''MATCH (p) MATCH (se:Sensor)
                       WHERE ID(p)=$id1 and se.sysId="$sensor"
                       create (p)-[:PERFORMED_BY]->(se)'''
        return Query(query_str=query_str,
                     template_string_parameters={"id1": id1, "sensor": sensor}
                     )

    # returns a list of all sensor and pizza combinations
    @staticmethod
    def all_sensor_pizza_combinations():
        query_str = '''MATCH path=(ev:Event)- [:DF_CONTROL_FLOW_ITEM*]->(g:Event)
                    MATCH (ev)-[:ACTS_ON]->(p:Pizza)
                    WHERE NOT EXISTS((:Event)-[:DF_CONTROL_FLOW_ITEM]->(ev))
                    AND NOT EXISTS((g)-[:DF_CONTROL_FLOW_ITEM]->(:Event))
                    UNWIND nodes(path) as e
                    MATCH (e)-[:ACTS_ON]->(n) 
                    WITH e, collect(n.sysId) as actsonids, p
                    match (e)-[:EXECUTED_BY]->(s)
                    return {activity:s.sysId,pizzaId:p.sysId} as trace'''
        return Query(query_str=query_str)

    # returns all the ecdfs belonging to an ecdfc
    @staticmethod
    def all_ecdfs_of_an_ecdfc(name):
        query_str = '''MATCH(n:Performance:Latency{name:"$name"})-[:HAS_PERFORMANCE]->(ecdf) RETURN ecdf.name as ecdf'''
        return Query(query_str=query_str,
                     template_string_parameters={"name": name}
                     )

    # returns all ecdfs and value of a database
    @staticmethod
    def return_all_ecdfs_and_values_of_a_db():
        query_str = '''match (p:Performance:LatencyECDF) 
                       match (parent:Latency)-[:HAS_PERFORMANCE]->(p)
                       return p.name, p.val, COLLECT(parent.name)[0] as parent'''
        return Query(query_str=query_str)

    # returns all ecdfcs and values of a database
    @staticmethod
    def return_all_ecdfcs_and_values_of_a_db():
        query_str = '''match (p:Performance:Latency) return p.name, p.val'''
        return Query(query_str=query_str)

    # returns all flows and values of a database
    @staticmethod
    def return_all_flows_and_values_of_a_db():
        query_str = '''match (p:Performance:Flow) return p.name, p.val'''
        return Query(query_str=query_str)

    # creates a LatencyECDF with name and value
    @staticmethod
    def create_latencyecdf_with_name_and_value_and_dbname(name, value, db_name):
        query_str = '''create (p:Performance:LatencyECDF{name:"$name",val:"$value",dbname:"$dbname"})'''
        return Query(query_str=query_str,
                     template_string_parameters={"name": name,"value": value, "dbname": db_name}
                    )

    @staticmethod
    def create_latency_with_name_and_value(name,value):
        query_str = '''create (p:Performance:Latency{name:"$name",val:"$value"})'''
        return Query(query_str=query_str,
                     template_string_parameters={"name": name,"value": value}
                    )

    @staticmethod
    def create_flow_with_name_and_value(name,value):
        query_str = '''create (p:Performance:Flow{name:"$name",val:"$value"})'''
        return Query(query_str=query_str,
                     template_string_parameters={"name": name,"value": value}
                    )

    # connects all the performance nodes to the corresponding parent
    @staticmethod
    def connect_main_performance_nodes_to_children():
        query_str = '''match (ml:MainLatency:Performance) match (l:Latency:Performance)
                create (ml)-[:HAS_PERFORMANCE]->(l)
                with count(*) as c_ml
                match (mq:MainQueue:Performance) match (q:Queue:Performance)
                create (mq)-[:HAS_PERFORMANCE]->(q)
                with count(*) as c_mq
                match (mf:MainFlow:Performance) match (f:Flow:Performance)
                create (mf)-[:HAS_PERFORMANCE]->(f)
                with count(*) as c_mf
                match (mu:MainUtilization:Performance) match (u:Utilization:Performance)
                create (mu)-[:HAS_PERFORMANCE]->(u)'''
        return Query(query_str)

    # provides a similarity and difference value between two ECDFs for conformance
    @staticmethod
    def diffence_and_similarity_between_ecdfs(ecdf_name1, ecdf_name2,difference,similarity,performance,kolmogorov):
        query_str = '''match(e1: Performance:LatencyECDF{name: "$ecdf_name1"})
                       match(e2: Performance:LatencyECDF{name: "$ecdf_name2"})
                       merge(e1) - [: CONFORMANCE {difference: "$difference", similarity: "$similarity", performance: "$performance", kolmogorov: "$kolmogorov"}]->(e2)'''
        return Query(query_str=query_str,
                     template_string_parameters={"ecdf_name1": ecdf_name1, "ecdf_name2": ecdf_name2,
                                "difference": difference, "similarity": similarity, "performance": performance, "kolmogorov": kolmogorov} )

    @staticmethod
    def similarity_difference_and_performance(ecdf_name1, ecdf_name2):
        query_str = '''match (e1:Performance:LatencyECDF{name:"$ecdf_name1"})
                       match (e2:Performance:LatencyECDF{name:"$ecdf_name2"})
                       match (e1)-[c:CONFORMANCE]->(e2)
                       return c.similarity as sim, c.difference as diff, c.performance as perf, c.kolmogorov as kolm'''
        return Query(query_str=query_str,
                     template_string_parameters={"ecdf_name1": ecdf_name1, "ecdf_name2": ecdf_name2} )

    @staticmethod
    def set_queue_properties(name,min,max,average):
        query_str = '''MATCH(p: Queue{name: "$name"})
                       SET p.max = $max
                       SET p.min = $min
                       SET p.average = $average
                       RETURN p'''
        return Query(query_str=query_str,
                     template_string_parameters={"name": name, "min": min, "max": max, "average": average} )

    @staticmethod
    def set_ecdf_properties(name,min,max,average,median):
        query_str = '''MATCH(p: LatencyECDF{name: "$name"})
                       SET p.max = $max
                       SET p.min = $min
                       SET p.average = $average
                       SET p.median = $median
                       RETURN p'''
        return Query(query_str=query_str,
                     template_string_parameters={"name": name, "min": min, "max": max, "average": average, "median": median} )

    @staticmethod
    def get_queue_properties(name):
        query_str = '''MATCH (p:Queue{name:"$name"}) 
                              RETURN p.max as max, p.min as min, p.average as average'''
        return Query(query_str=query_str,
                     template_string_parameters={"name": name } )

    @staticmethod
    def get_ecdf_properties(name):
        query_str = '''MATCH (p:LatencyECDF{name:"$name"}) 
                       RETURN p.max as max, p.min as min, p.average as average, p.median as median'''
        return Query(query_str=query_str,
                     template_string_parameters={"name": name } )

    @staticmethod
    def get_overall_performance_query():
        query_str = '''MATCH (p:Performance:LatencyECDF{name:"Execution time between S1 S15"}) RETURN p.average as average'''
        return Query(query_str=query_str)

    @staticmethod
    def get_similarity_of_designs(goal_design):
        query_str =  '''MATCH (p1:LatencyECDF)
                        MATCH (p2:LatencyECDF)
                        MATCH (p1)-[c:CONFORMANCE]->(p2)
                        WHERE p1.dbname<>p2.dbname
                        AND p2.dbname="$goal_design"
                        RETURN p1.dbname as p1db,avg(toFloat(c.kolmogorov)) as minsim
                        ORDER BY minsim DESC'''
        return Query(query_str=query_str,
                     template_string_parameters={"goal_design": goal_design})
