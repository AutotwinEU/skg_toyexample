from dataclasses import dataclass
from typing import Dict, Optional

from string import Template

from promg import Query


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
    def get_complete_corr_query(version_number):
        query_str = '''
            MATCH (p:Entity:$version_number) <-[:ACTS_ON] - (e:Event:$version_number) - [:OCCURRED_AT] -> (s:Station:$version_number)
            WITH s, apoc.coll.flatten(collect (distinct labels(p))) as labels
            CALL {
                WITH s, labels
                UNWIND labels as _label
                WITH s, _label
                WHERE _label = "Pizza" or _label = "Pack" or _label = "Box" or _label = "Pallet"
                WITH s, collect(distinct _label) as unique_labels 
                WHERE size(unique_labels) > 1
                RETURN s as packingStation, unique_labels
            }
            MATCH (e:Event:$version_number) - [:OCCURRED_AT] -> (packingStation)
            MATCH (e) - [:EXECUTED_BY] -> (sensor:Sensor:$version_number {sensorType: "ENTER"})
            WHERE NOT EXISTS ((e) - [:DF_PIZZA|DF_PACK|DF_BOX] -> (:Event))
            CALL {WITH e, packingStation
                  MATCH (f:Event:$version_number) - [:OCCURRED_AT] -> (packingStation)
                  MATCH (f) - [:EXECUTED_BY] -> (sensor:Sensor {sensorType: "EXIT"})
                  WHERE f.timestamp > e.timestamp
                  RETURN f
                  ORDER BY f.timestamp ASC
                  LIMIT 1
                  }
            MATCH (e) - [:ACTS_ON] -> (n)
            MERGE (f) - [:ACTS_ON] -> (n)
        '''

        return Query(query_str=query_str,
                     template_string_parameters={"version_number": version_number
                     })

    @staticmethod
    def get_delete_df_query(version_number):
        query_str = '''
            MATCH (e:Event:$version_number) - [df:DF_PIZZA|DF_PACK|DF_BOX|DF_PALLET] -> (f:Event:$version_number)
            DELETE df
        '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "version_number": version_number
                     })

    @staticmethod
    def get_merge_sensor_events_query(version_number):
        query_str = '''
            MATCH (e:SensorStatusEvent:$version_number)
            WITH e.timestamp as timestamp, e.activity as activity, collect(e) as batchedEvents
            CALL apoc.refactor.mergeNodes(batchedEvents, {properties:"combine", mergeRels: true})
            YIELD node
            return count(*)
        '''

        return Query(query_str=query_str,
                     template_string_parameters={"version_number": version_number})

    @staticmethod
    def get_connect_wip_sensor_to_assembly_line_query(version_number):
        query_str = '''
            MATCH (record:AssemblyLineRecord&SensorRecord&$version_number&!StationRecord)
            MATCH (a:AssemblyLine) - [:PREVALENCE] -> (record)
            MATCH (s:Sensor) - [:PREVALENCE] -> (record)
            MERGE (s) - [:PART_OF] -> (a)
        '''

        return Query(query_str=query_str,
                     template_string_parameters={"version_number": version_number})

    @staticmethod
    def get_complete_quality_query(version_number):
        query_str = '''
                MATCH (p:pizzaQualityAttribute:$version_number)
                SET p.defective = NOT(p.burned)
            '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "version_number": version_number
                     })

    @staticmethod
    def get_connect_operators_to_station_query(version_number, operator, station):
        query_str = '''
            MATCH (operator:Operator:$version_number {sysId: $operator})
            MATCH (station:Station:$version_number {sysId: $station})
            MERGE (operator) - [:OPERATES] -> (station)
        '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "version_number": version_number
                     },
                     parameters={
                         "operator": operator,
                         "station": station
                     })

    @staticmethod
    def get_create_quality_for_pizzas_query(version_number):
        query_str = '''
                MATCH (p:Pizza:$version_number)
                WHERE NOT EXISTS ((p) - [:HAS_PROPERTY] -> (:PizzaQualityAttribute:$version_number))
                CREATE (q:EntityAttribute:PizzaQualityAttribute:$version_number {burned: false, defective: false})
                CREATE (p) - [:HAS_PROPERTY] -> (q)
            '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "version_number": version_number
                     })

    @staticmethod
    def get_create_qualifier_rel_to_pizza_quality_query(version_number):
        query_str = '''
                    MATCH (q:PizzaQualityAttribute:$version_number) <- [:HAS_PROPERTY] - (p:Pizza:$version_number) <- [:ACTS_ON] - (e:Event)
                    MATCH (e) - [:EXECUTED_BY] -> (:Sensor:$version_number {sensorType: "EXIT"}) 
                        - [:PART_OF] -> (:Station:$version_number {sysId: "Oven"})
                    CREATE (e) - [:CREATES] -> (q)
                '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "version_number": version_number
                     })

    @staticmethod
    def get_reset_used_prop_query(batch_size):
        query_str = '''
                CALL apoc.periodic.commit('
                MATCH (e:Event)
                WHERE e.used = True
                WITH e LIMIT $limit
                SET e.used = Null
                RETURN count(*)',
                {limit: $limit})
            '''

        return Query(query_str=query_str,
                     parameters={"limit": batch_size})

    @staticmethod
    def get_connect_activities_to_location_query():
        # language=sql
        query_str = '''
            MATCH (l:Location) <- [:PART_OF] - (:Sensor) <- [:EXECUTED_BY] - (e:Event) <- [:OBSERVED] - (a:Activity)
            MERGE (a) - [:OCCURS_AT] -> (l)
        '''

        return Query(query_str=query_str)

    @staticmethod
    def get_observe_events_to_station_aggregation_query():
        # language=sql
        query_str = '''
            MATCH (e:Event) <- [:OBSERVED] - (:Activity) - [:OCCURS_AT] -> (l:Location)
            MERGE (e) - [:OCCURED_AT] -> (l)
        '''

        return Query(query_str=query_str)

    @staticmethod
    def get_connect_stations_queries():
        # language=sql
        query_str = '''
            MATCH (s1:Station) <- [:OCCURS_AT] - (:Activity) 
                - [df] -> (:Activity) - [:OCCURS_AT] -> (s2:Station)
            WHERE s1 <> s2
            MERGE (s1) - [:CONN {movedEntity: df.entityType}] -> (s2)
        '''

        return Query(query_str=query_str)

    @staticmethod
    def get_connect_sensors_queries():
        # language=sql
        query_str = '''
            MATCH (e1:Event) - [:EXECUTED_BY] -> (s1:Sensor) - [:PART_OF] -> (:Station) <- [:OCCURS_AT] - (:Activity) 
                    - [df] -> (:Activity) - [:OCCURS_AT] -> (:Station) <- [:PART_OF] - (s2:Sensor) <- [:EXECUTED_BY] 
                    - (e2:Event) <- [] - (e1)
            WHERE s1 <> s2
            WITH s1, s2, df
            MERGE (s1) - [:CONN {movedEntity: df.entityType}] -> (s2)
            '''

        return Query(query_str=query_str)

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
