from dataclasses import dataclass
from typing import Dict, Optional

from string import Template

from promg import Query

station_info = {
    'PackStation': {'enter_entity': 'Pizza', 'exit_entity': 'Pack', 'quantity': 'packCount'},
    'BoxStation': {'enter_entity': 'Pack', 'exit_entity': 'Box', 'quantity': 'boxCount'},
    'PalletStation': {'enter_entity': 'Box', 'exit_entity': 'Pallet', 'quantity': 'boxQuantity'}
}


class CustomCypherQueryLibrary:

    @staticmethod
    def get_create_source_station_aggregation_query(entity_type):
        # language=sql
        query_str = '''
            MATCH (c_start:Activity)
            WHERE NOT EXISTS ((:Activity) - [:$df_a_type] -> (c_start))
            WITH c_start, right(c_start.activity, 2) as sensorId
            WITH c_start, sensorId, "SourceStation"+sensorId as id
            MERGE (station:Entity:Resource:Station:Location {type: "Source", sysId: id})
            MERGE (c_start) - [:OCCURS_AT] -> (station)
            WITH station, sensorId
            MATCH (sensor:Sensor {sysId: sensorId})
            MERGE (sensor) - [:PART_OF] -> (station)
        '''

        return Query(query_str=query_str,
                     template_string_parameters={"df_a_type": f"DF_A_{entity_type.upper()}"})

    @staticmethod
    def get_create_sink_station_aggregation_query(entity_type):
        # language=sql
        query_str = '''
                MATCH (c_end:Activity)
                WHERE NOT EXISTS ((c_end) - [:$df_a_type] -> (:Activity))
                WITH c_end, right(c_end.activity, 2) as sensorId
                WITH c_end, sensorId, "SinkStation"+sensorId as id
                MERGE (station:Entity:Resource:Station:Location {type: "Sink", sysId: id})
                MERGE (c_end) - [:OCCURS_AT] -> (station)
                WITH station, sensorId
                MATCH (sensor:Sensor {sysId: sensorId})
                MERGE (sensor) - [:PART_OF] -> (station)
            '''

        return Query(query_str=query_str,
                     template_string_parameters={"df_a_type": f"DF_A_{entity_type.upper()}"})

    @staticmethod
    def get_create_processing_stations_aggregation_query(entity_type):
        # language=sql
        query_str = '''
                    MATCH p=(c_start:Activity) - [:$df_a_type*] -> (c_end:Activity)
                    WHERE NOT EXISTS ((c_end) - [:$df_a_type] -> (:Activity)) AND NOT EXISTS 
                    ((:Activity) - [:$df_a_type] -> (c_start))
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
                     template_string_parameters={"df_a_type": f"DF_A_{entity_type.upper()}"})

    @staticmethod
    def get_set_pp_changed_property_query(station_id, version_number):
        query_str = '''
            MATCH (e:Event:$version_number) - [:OCCURRED_AT] -> (:Station:$version_number {sysId: '$stationId'})
            SET e.tempPPChanged = True
        '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "version_number": version_number,
                         "stationId": station_id
                     })

    @staticmethod
    def get_determine_pp_changed_query(station_id, version_number):
        # determine when new production run changed on event level
        query_str = '''
        MATCH (e:Event:$version_number) - [:OCCURRED_AT] -> (:Station:$version_number {sysId: '$stationId'})
        MATCH (e) - [df:DF_SENSOR] -> (f)
        MATCH (e) - [:ACTS_ON] -> (:Entity:$version_number) - [:FOLLOWS] -> (pp1:ProductionPlan)
        MATCH (f) - [:ACTS_ON] -> (:Entity:$version_number) - [:FOLLOWS] -> (pp2:ProductionPlan)
        WITH CASE pp2.code
            WHEN pp1.code THEN FALSE
            ELSE TRUE END as change, f
        SET f.tempPPChanged = change
        '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "version_number": version_number,
                         "stationId": station_id
                     })

    @staticmethod
    def get_determine_entity_part_of_query(station_id, version_number):
        # determine whether entity should be part of another entity
        query_str = '''
            MATCH (e:Event:$version_number) - [:OCCURRED_AT] -> (:Station:$version_number {sysId: '$stationId'})
            MATCH (e) - [:EXECUTED_BY] -> (s:Sensor:$version_number {type:"ENTER"})
            WITH e, CASE
                WHEN EXISTS((e) - [:$df_enter_entity_label] -> (:Event)) THEN false
                ELSE true
                END AS partOf
            set e.tempPartOf = partOf 
        '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "version_number": version_number,
                         "df_enter_entity_label": "DF_" + station_info[station_id]["enter_entity"].upper(),
                         "stationId": station_id
                     })

    @staticmethod
    def get_determine_number_in_run_query(station_id, version_number):
        query_str = '''
            MATCH p = (e:Event:$version_number {tempPPChanged:TRUE}) - [:DF_SENSOR*] -> (f:Event)
            MATCH (e) - [:OCCURRED_AT] -> (:Station:$version_number {sysId: '$stationId'})
            WHERE (EXISTS ((f) - [:DF_SENSOR] -> (:Event:$version_number {tempPPChanged:TRUE})) 
                    OR NOT EXISTS((f) - [:DF_SENSOR] -> (:Event:$version_number))) 
            AND all(event in nodes(p)[1..] WHERE event.tempPPChanged = False)
            CALL {WITH p
                WITH nodes(p) as eventPaths
                UNWIND range(0,size(eventPaths)) AS i
                WITH i, eventPaths[i] as e
                WITH e, 
                    CASE e.tempPartOf
                    WHEN true THEN i
                    WHEN false then -1
                    ELSE i END as counter
                SET e.tempNumberInRun = counter
            }
        '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "version_number": version_number,
                         "stationId": station_id
                     })

    @staticmethod
    def get_determine_number_in_run_range_of_exit_stations_query(station_id, version_number):
        query_str = '''
            MATCH (f:Event:$version_number) - [:OCCURRED_AT] -> (:Station:$version_number {sysId: '$stationId'})
            MATCH  (f) - [:ACTS_ON] -> (:Entity:$version_number:$exit_entity_label) - [:FOLLOWS] -> (pp:ProductionPlan)
            MATCH (f) - [:EXECUTED_BY] -> (sensor:Sensor:$version_number {type: "EXIT"})
            WHERE NOT EXISTS ((:Event) - [:$df_exit_entity_label] -> (f))
            SET f.tempNumRange =  range(f.tempNumberInRun*pp.$quantity, (f.tempNumberInRun+1)*pp.$quantity-1)
        '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "version_number": version_number,
                         "exit_entity_label": station_info[station_id]["exit_entity"],
                         "df_exit_entity_label": "DF_" + station_info[station_id]["exit_entity"].upper(),
                         "quantity": station_info[station_id]["quantity"],
                         "stationId": station_id
                     })

    @staticmethod
    def get_create_part_of_relation(station_id, version_number):
        query_str = '''
            MATCH (e:Event:$version_number) - [:OCCURRED_AT] 
                -> (packingStation:Station:$version_number {sysId: '$stationId'})
            MATCH  (e) - [:ACTS_ON] -> (:Entity:$version_number:$enter_entity_label) - [:FOLLOWS] -> (pp:ProductionPlan)
            MATCH (e) - [:EXECUTED_BY] -> (sensor:Sensor:$version_number {type: "ENTER"})
            WHERE NOT EXISTS ((e) - [:$df_enter_entity_label] -> (:Event))
            CALL {WITH e, packingStation, pp
                  MATCH (f:Event:$version_number) - [:OCCURRED_AT] -> (packingStation)
                  MATCH  (f) - [:ACTS_ON] -> (:Entity:$version_number:$exit_entity_label) - [:FOLLOWS] -> (pp)
                  WHERE f.timestamp > e.timestamp AND e.tempNumberInRun in f.tempNumRange
                  RETURN f
                  ORDER BY f.timestamp ASC
                  LIMIT 1
                  }
            MATCH (e) - [:ACTS_ON] -> (enter:Entity:$version_number:$enter_entity_label)
            MATCH (f) - [:ACTS_ON] -> (exit:Entity:$version_number:$exit_entity_label)
            MERGE (enter) - [:PART_OF] -> (exit)
            MERGE (enter) - [:FROM] -> (combo:$enter_exit_combo:$version_number) - [:TO] -> (exit)
            MERGE (e) - [:ACTS_ON] -> (combo)
            MERGE (f) - [:ACTS_ON] -> (combo)
        '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "version_number": version_number,
                         "enter_entity_label": station_info[station_id]["enter_entity"],
                         "df_enter_entity_label": "DF_" + station_info[station_id]["enter_entity"].upper(),
                         "exit_entity_label": station_info[station_id]["exit_entity"],
                         "enter_exit_combo": station_info[station_id]["enter_entity"] + station_info[station_id][
                             "exit_entity"],
                         "quantity": station_info[station_id]["quantity"],
                         "stationId": station_id
                     })

    @staticmethod
    def get_create_part_of_FIFO_query(version_number, station_id):
        query_str = '''
            MATCH (e:Event:$version_number) - [:OCCURRED_AT] -> (packingStation {sysId:'$stationId'})
            MATCH (e) - [:EXECUTED_BY] -> (sensor:Sensor:$version_number {type: "ENTER"})
            WHERE NOT EXISTS ((e) - [:$df_enter_entity_label] -> (:Event))
            CALL {WITH e, packingStation
                  MATCH (f:Event:$version_number) - [:OCCURRED_AT] -> (packingStation)
                  MATCH  (f) - [:ACTS_ON] -> (:Entity:$version_number:$exit_entity_label)
                  WHERE f.timestamp > e.timestamp
                  RETURN f
                  ORDER BY f.timestamp ASC
                  LIMIT 1
                  }
            MATCH (e) - [:ACTS_ON] -> (enter:Entity:$version_number:$enter_entity_label)
            MATCH (f) - [:ACTS_ON] -> (exit:Entity:$version_number:$exit_entity_label)
            MERGE (enter) - [:PART_OF] -> (exit)
            MERGE (enter) - [:FROM] -> (combo:$enter_exit_combo:$version_number) - [:TO] -> (exit)
            MERGE (e) - [:ACTS_ON] -> (combo)
            MERGE (f) - [:ACTS_ON] -> (combo)
        '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "version_number": version_number,
                         "enter_entity_label": station_info[station_id]["enter_entity"],
                         "df_enter_entity_label": "DF_" + station_info[station_id]["enter_entity"].upper(),
                         "enter_exit_combo": station_info[station_id]["enter_entity"] + station_info[station_id][
                             "exit_entity"],
                         "exit_entity_label": station_info[station_id]["exit_entity"],
                         "stationId": station_id
                     })

    @staticmethod
    def get_delete_temp_properties_query(version_number, station_id):
        query_str = '''
                    MATCH (e:Event:$version_number) - [:OCCURRED_AT] -> (packingStation {sysId:'$stationId'})
                    REMOVE e.tempPPChanged, e.tempPartOf, e.tempNumberInRun, e.tempNumRange
                '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "version_number": version_number,
                         "stationId": station_id
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
            MATCH (a:AssemblyLine) - [:EXTRACTED_FROM] -> (record)
            MATCH (s:Sensor) - [:EXTRACTED_FROM] -> (record)
            MERGE (s) - [:PART_OF] -> (a)
        '''

        return Query(query_str=query_str,
                     template_string_parameters={"version_number": version_number})

    @staticmethod
    def get_complete_quality_query(version_number):
        query_str = '''
                MATCH (p:PizzaQualityAttribute:$version_number)
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
                    MATCH (q:PizzaQualityAttribute:$version_number) <- [:HAS_PROPERTY] - (p:Pizza:$version_number) <- 
                    [:ACTS_ON] - (e:Event)
                    MATCH (e) - [:EXECUTED_BY] -> (:Sensor:$version_number {type: "EXIT"}) 
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
            MATCH (s1:Sensor) <- [:EXECUTED_BY] - (e1:Event) - [df:DF_PIZZA|DF_PACK|DF_BOX|DF_PALLET] -> (e2:Event) - 
            [:EXECUTED_BY] -> (s2:Sensor) 
            WHERE s1 <> s2
            WITH DISTINCT s1, s2, df.entityType as movedEntity
            MERGE (s1) - [:CONN {movedEntity: movedEntity}] -> (s2)
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