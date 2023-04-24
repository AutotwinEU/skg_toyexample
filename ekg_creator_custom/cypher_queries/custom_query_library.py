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
            MERGE (s:Entity:Station {entityType: "Station", type: "Source", sensors: [c_start.cID],
                                             ID: id, uID:"Station_"+id})
            MERGE (c_start) - [:OCCURS_AT] -> (l:Location {locationType: "station", ID: id})
            MERGE (s) - [:LOCATED_AT] -> (l)
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
                MERGE (s:Entity:Station {entityType: "Station", type: "Sink", sensors: [c_end.cID],
                                             ID: id, uID:"Station_"+id})
                MERGE (c_end) - [:OCCURS_AT] -> (l:Location {locationType: "station", ID: id})
                MERGE (s) - [:LOCATED_AT] -> (l)
            '''

        return Query(query_str=query_str,
                     template_string_parameters={"df_c_type": f"DF_C_{entity_type.upper()}"})

    @staticmethod
    def get_create_processing_stations_aggregation_query(entity_type):
        # language=sql
        query_str = '''
                    MATCH p=(c_start:Class {classType: "sensor"}) - [:$df_c_type*] -> (c_end:Class {classType: "sensor"})
                    WHERE NOT EXISTS ((c_end) - [:$df_c_type] -> (:Class {classType: "sensor"})) AND NOT EXISTS ((:Class {classType: "sensor"}) - [
                    :$df_c_type] -> (c_start))
                    WITH nodes(p) as classList
                    UNWIND range(1,size(classList)-3,2) AS i
                    WITH classList[i] as first, classList[i+1] as second
                    WITH first, second, "ProcessingStation"+first.cID+second.cID as id
                    MERGE (s:Entity:Station {entityType: "Station", type: "Processing", 
                                             sensors: [first.cID, second.cID],
                                              ID: id, uID:"Station_"+id})
                    MERGE (first) - [:OCCURS_AT] -> (l:Location {locationType: "station", 
                                                ID: id}) <- [:OCCURS_AT] - (second)
                    MERGE (s) - [:LOCATED_AT] -> (l)
                '''

        return Query(query_str=query_str,
                     template_string_parameters={"df_c_type": f"DF_C_{entity_type.upper()}"})

    @staticmethod
    def get_observe_events_to_station_aggregation_query():
        # language=sql
        query_str = '''
            MATCH (e:Event) - [:OBSERVED] -> (c:Class {classType: "sensor"}) - [:OCCURS_AT] -> (l:Location)
            MERGE (e) - [:OCCURRED_AT] -> (l)
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
