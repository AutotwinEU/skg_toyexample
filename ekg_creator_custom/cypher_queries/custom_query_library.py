from dataclasses import dataclass
from typing import Dict, Optional

from string import Template

from ekg_creator.database_managers.db_connection import Query


class CustomCypherQueryLibrary:

    @staticmethod
    def get_create_source_station_aggregation_query(entity_type):
        # language=sql
        query_str = '''
            MATCH (c_start:Activity)
            WHERE NOT EXISTS ((:Activity) - [:$df_c_type] -> (c_start))
            WITH c_start, right(c_start.activity, 2) as sensorId
            WITH c_start, sensorId, "SourceStation"+sensorId as id
            MERGE (station:Entity:Resource:Station:Location {type: "Source", sysId: id})
            MERGE (c_start) - [:OCCURS_AT] -> (station)
            WITH station, sensorId
            MATCH (sensor:Sensor {sysId: sensorId})
            MERGE (sensor) - [:PART_OF] -> (station)
        '''

        return Query(query_str=query_str,
                     template_string_parameters={"df_c_type": f"DF_C_{entity_type.upper()}"})

    @staticmethod
    def get_create_sink_station_aggregation_query(entity_type):
        # language=sql
        query_str = '''
                MATCH (c_end:Activity)
                WHERE NOT EXISTS ((c_end) - [:$df_c_type] -> (:Activity))
                WITH c_end, right(c_end.activity, 2) as sensorId
                WITH c_end, sensorId, "SinkStation"+sensorId as id
                MERGE (station:Entity:Resource:Station:Location {type: "Sink", sysId: id})
                MERGE (c_end) - [:OCCURS_AT] -> (station)
                WITH station, sensorId
                MATCH (sensor:Sensor {sysId: sensorId})
                MERGE (sensor) - [:PART_OF] -> (station)
            '''

        return Query(query_str=query_str,
                     template_string_parameters={"df_c_type": f"DF_C_{entity_type.upper()}"})

    @staticmethod
    def get_create_processing_stations_aggregation_query(entity_type):
        # language=sql
        query_str = '''
                    MATCH p=(c_start:Activity) - [:$df_c_type*] -> (c_end:Activity)
                    WHERE NOT EXISTS ((c_end) - [:$df_c_type] -> (:Activity)) AND NOT EXISTS 
                    ((:Activity) - [:$df_c_type] -> (c_start))
                    WITH nodes(p) as activityList
                    UNWIND range(1,size(activityList)-3,2) AS i
                    WITH activityList[i] as first, activityList[i+1] as second
                    WITH first, second, 
                            right(first.activity, 2) as startSensorId, right(second.activity, 2) as endSensorId
                    WITH first, second,  startSensorId, endSensorId, "ProcessingStation"+startSensorId+endSensorId as id
                    MERGE (station:Entity:Resource:Station:Location {type: "Processing", sysId: id})
                    MERGE (first) - [:OCCURS_AT] -> (station) <- [:OCCURS_AT] - (second)
                    WITH station, startSensorId, endSensorId
                    MATCH (startSensor:Sensor {sysId: startSensorId})
                    MATCH (endSensor:Sensor {sysId: endSensorId})
                    MERGE (startSensor) - [:PART_OF] -> (station)
                    MERGE (endSensor) - [:PART_OF] -> (station)
                '''

        return Query(query_str=query_str,
                     template_string_parameters={"df_c_type": f"DF_C_{entity_type.upper()}"})

    @staticmethod
    def get_observe_events_to_station_aggregation_query():
        # language=sql
        query_str = '''
            MATCH (e:Event) <- [:OBSERVED] - (:Activity) - [:OCCURS_AT] -> (l:Location)
            MERGE (e) - [:OCCURED_AT] -> (l)
        '''

        return Query(query_str=query_str)

    @staticmethod
    def get_connect_stations_queries(entity_type):
        # language=sql
        query_str = '''
            MATCH (s1:Station) <- [:OCCURS_AT] - (:Activity) 
                - [:$df_c_type] -> (:Activity) - [:OCCURS_AT] -> (s2:Station)
            WHERE s1 <> s2
            MERGE (s1) - [:CONN {movedEntity: "$entity_type"}] -> (s2)
        '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "df_c_type": f"DF_C_{entity_type.upper()}",
                         "entity_type": entity_type
                     })

    @staticmethod
    def get_connect_sensors_queries(entity_type):
        # language=sql
        query_str = '''
                 MATCH (s1:Sensor) <- [:EXECUTED_BY] - (:Event) <- [:OBSERVED] - (:Activity) 
                    - [:$df_c_type] -> (:Activity) - [:OBSERVED] -> (:Event) - [:EXECUTED_BY] -> (s2:Sensor)
                WHERE s1 <> s2
                WITH s1, s2
                MERGE (s1) - [:CONN {movedEntity: "$entity_type"}] -> (s2)
            '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "df_c_type": f"DF_C_{entity_type.upper()}",
                         "entity_type": entity_type
                     })

    @staticmethod
    def get_update_sensors_queries():
        # language=sql
        query_str = '''
                MATCH (s1:Sensor) - [:PART_OF] -> (station:Station)
                WITH s1, CASE
                    WHEN EXISTS((s1) - [:CONN] -> (:Sensor) - [:PART_OF] -> (station)) THEN "ENTER"
                    WHEN EXISTS((s1) <- [:CONN] - (:Sensor) - [:PART_OF] -> (station)) THEN "EXIT"
                    WHEN station.type = "Source" THEN "EXIT"
                    WHEN station.type = "Sink" THEN "ENTER"
                END AS sensor_type
                SET s1.type = sensor_type
            '''

        return Query(query_str=query_str)

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
            MATCH (p:Pizza) <- [:ACTS_ON] - (e:Event)-[:OCCURED_AT]->(station:Entity:Station)
            MATCH (e) - [:EXECUTED_BY] -> (sensor:Sensor)
            RETURN e.timestamp AS time, station.sysId AS station, station.type AS station_type, 
                p.sysId AS part, sensor.type as activity
            ORDER BY time, ID(e)
        '''

        return Query(query_str=query_str)

    @staticmethod
    def get_write_attributes_to_stations(station, buffer_capacity, machine_capacity, processing_time):
        # language=sql
        query_str = '''
            MATCH (c:Entity:Station {sysId: "$station"})
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
                           MATCH (:Entity:Station {sysId: "$connection_from"})
                                 -[conn:CONN {movedEntity: "Pizza"}]->
                                 (:Entity:Station {sysId: "$connection_to"})
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
