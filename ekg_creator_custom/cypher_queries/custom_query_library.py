from dataclasses import dataclass
from typing import Dict, Optional

from string import Template

from ekg_creator.database_managers.db_connection import Query


class CustomCypherQueryLibrary:

    @staticmethod
    def get_create_source_station_aggregation_query(entity_type):
        # language=sql
        query_str = '''
            MATCH (c_start:Class {classType: "sensor"})
            WHERE NOT EXISTS ((:Class) - [:$df_c_type] -> (c_start))
            WITH c_start, "SourceStation"+c_start.cID as id
            MERGE (s:Entity:Resource:Station {entityType: "Station", type: "Source", sensors: [c_start.cID],
                                             ID: id, uID:"Station_"+id})
            MERGE (c_start) - [:OCCURS_AT] -> (s)
        '''

        return Query(query_str=query_str,
                     template_string_parameters={"df_c_type": f"DF_C_{entity_type.upper()}"})

    @staticmethod
    def get_create_sink_station_aggregation_query(entity_type):
        # language=sql
        query_str = '''
                MATCH (c_end:Class {classType: "sensor"})
                WHERE NOT EXISTS ((c_end) - [:$df_c_type] -> (:Class))
                WITH c_end, "SinkStation"+c_end.cID as id
                MERGE (s:Entity:Resource:Station {entityType: "Station", type: "Sink", sensors: [c_end.cID],
                                             ID: id, uID:"Station_"+id})
                MERGE (c_end) - [:OCCURS_AT] -> (s)
            '''

        return Query(query_str=query_str,
                     template_string_parameters={"df_c_type": f"DF_C_{entity_type.upper()}"})

    @staticmethod
    def get_create_processing_stations_aggregation_query(entity_type):
        # language=sql
        query_str = '''
                    MATCH p=(c_start:Class {classType: "sensor"}) - [:$df_c_type*] -> (c_end:Class {classType: 
                    "sensor"})
                    WHERE NOT EXISTS ((c_end) - [:$df_c_type] -> (:Class {classType: "sensor"})) AND NOT EXISTS ((
                    :Class {classType: "sensor"}) - [
                    :$df_c_type] -> (c_start))
                    WITH nodes(p) as classList
                    UNWIND range(1,size(classList)-3,2) AS i
                    WITH classList[i] as first, classList[i+1] as second
                    WITH first, second, "ProcessingStation"+first.cID+second.cID as id
                    MERGE (s:Entity:Resource:Station {entityType: "Station", type: "Processing", 
                                             sensors: [first.cID, second.cID],
                                              ID: id, uID:"Station_"+id})
                    MERGE (first) - [:OCCURS_AT] -> (s) <- [:OCCURS_AT] - (second)
                '''

        return Query(query_str=query_str,
                     template_string_parameters={"df_c_type": f"DF_C_{entity_type.upper()}"})

    @staticmethod
    def get_observe_events_to_station_aggregation_query():
        # language=sql
        query_str = '''
            MATCH (e:Event) - [:OBSERVED] -> (c:Class {classType: "sensor"}) - [:OCCURS_AT] -> (s:Station)
            MERGE (e) - [:CORR] -> (s)
        '''

        return Query(query_str=query_str)

    @staticmethod
    def get_connect_stations_queries(entity_type):
        # language=sql
        query_str = '''
            MATCH (s1:Station) <- [:OCCURS_AT] - (c1:Class) - [:$df_c_type] -> (c2:Class) - [:OCCURS_AT] -> (s2:Station)
            WHERE s1 <> s2
            MERGE (s1) - [:CONN {movedEntity: "$entity_type"}] -> (s2)
        '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "df_c_type": f"DF_C_{entity_type.upper()}",
                         "entity_type": entity_type
                     })

    @staticmethod
    def get_create_station_entities_and_correlate_to_events_query():
        # language=sql
        query_str = '''
            MATCH (e) - [:OCCURRED_AT] ->  (l:Location) <- [:LOCATED_AT] - (s:Station)
            MERGE (e) - [:CORR] -> (s)
        '''

        return Query(query_str=query_str)

    @staticmethod
    def get_create_non_processing_station_entities_and_correlate_to_events_query():
        # language=sql
        query_str = '''
                MATCH (e) - [:AT] -> (cs:Location)
                WHERE cs.type <> "Processing"
                WITH e, cs, cs.ID AS id
                MERGE (s:Entity:Station {entityType: "Station", type: cs.type, 
                                        sensor: cs.sensors[0], 
                                        ID: id, uID:"Station_"+id})
                MERGE (s) - [:LOCATED_AT] -> (cs)
                MERGE (e) - [:CORR] -> (s)
            '''

        return Query(query_str=query_str)

    @staticmethod
    def get_read_log_query():
        # language=sql
        query_str = '''
            MATCH (e:Event)-[:CORR]->(c:Entity:Station)
            RETURN e.timestamp AS time, c.ID AS station, c.type AS station_type, e.pizzaId AS part,
            CASE WHEN c.type = "Source" THEN "EXIT"
                 WHEN c.type = "Sink" THEN "ENTER"
                 WHEN e.sensor = c.sensors[0] THEN "ENTER" ELSE "EXIT"
                 END AS activity
            ORDER BY time, ID(e)
        '''

        return Query(query_str=query_str)

    @staticmethod
    def get_write_attributes_to_stations(station, buffer_capacity, machine_capacity, processing_time):
        # language=sql
        query_str = '''
            MATCH (c:Entity:Station {ID: "$station"})
                   SET c.buffer_capacity = $buffer_capacity,
                       c.machine_capacity = $machine_capacity,
                       c.processing_time_mean = $mean,
                       c.processing_time_std = $std
        '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "station": station,
                         "buffer_capacity": buffer_capacity,
                         "machine_capacity": machine_capacity,
                         "mean": processing_time['mean'],
                         "std": processing_time['std']
                     })

    @staticmethod
    def get_write_attributes_to_connections(connection, routing_probability, transfer_time):
        # language=sql
        query_str = '''
                           MATCH (:Entity:Station {ID: "$connection_from"})
                                 -[conn:CONN {movedEntity: "Pizza"}]->
                                 (:Entity:Station {ID: "$connection_to"})
                           SET conn.routing_probability = $routing_probability,
                               conn.transfer_time_mean = $mean,
                               conn.transfer_time_std = $std
                    '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "connection_from": connection[0],
                         "connection_to": connection[1],
                         "routing_probability": routing_probability,
                         "mean": transfer_time['mean'],
                         "std": transfer_time['std']
                     })
