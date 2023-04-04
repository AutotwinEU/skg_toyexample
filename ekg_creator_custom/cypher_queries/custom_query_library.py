from dataclasses import dataclass
from typing import Dict, Optional

from string import Template


@dataclass
class Query:
    query_string: str
    kwargs: Optional[Dict[str, any]]


class CustomCypherQueryLibrary:

    @staticmethod
    def get_create_source_station_aggregation_query(entity_type):
        query_str = '''
            MATCH (c_start:Class_sensor)
            WHERE NOT EXISTS ((:Class) - [:$df_c_type] -> (c_start))
            WITH c_start, "SourceStation"+c_start.cID as id
            MERGE (c_start) - [:COMPOSED] -> (:Class:Class_station {classType: "station", type: "Source", sensor: c_start.cID,
                                                           ID: id, uID:"Station_"+id})
        '''

        query_str = Template(query_str).substitute(df_c_type=f"DF_C_{entity_type.upper()}")
        return Query(query_string=query_str, kwargs={})

    @staticmethod
    def get_create_sink_station_aggregation_query(entity_type):
        query_str = '''
                MATCH (c_end:Class_sensor)
                WHERE NOT EXISTS ((c_end) - [:$df_c_type] -> (:Class))
                WITH c_end, "SinkStation"+c_end.cID as id
                MERGE (c_end) - [:COMPOSED] -> (:Class:Class_station {classType: "station", type: "Sink", sensor: c_end.cID,
                                                           ID: id, uID:"Station_"+id})
            '''

        query_str = Template(query_str).substitute(df_c_type=f"DF_C_{entity_type.upper()}")
        return Query(query_string=query_str, kwargs={})

    @staticmethod
    def get_create_processing_stations_aggregation_query(entity_type):
        query_str = '''
                    MATCH p=(c_start:Class_sensor) - [:$df_c_type*] -> (c_end:Class_sensor)
                    WHERE NOT EXISTS ((c_end) - [:$df_c_type] -> (:Class_sensor)) AND NOT EXISTS ((:Class_sensor) - [:$df_c_type] -> (c_start))
                    WITH nodes(p) as classList
                    UNWIND range(1,size(classList)-3,2) AS i
                    WITH classList[i] as first, classList[i+1] as second
                    WITH first, second, "ProcessingStation"+first.cID+second.cID as id
                    MERGE (first) - [:COMPOSED] -> (:Class:Class_station {classType: "station", type: "Processing", 
                                                start_sensor: first.cID, end_sensor: second.cID,
                                                ID: id, uID:"Station_"+id}) <- [:COMPOSED] - (second)
                '''

        query_str = Template(query_str).substitute(df_c_type=f"DF_C_{entity_type.upper()}")
        return Query(query_string=query_str, kwargs={})

    @staticmethod
    def get_observe_events_to_station_aggregation_query():
        query_str = '''
            MATCH (e:Event) - [:OBSERVED] -> (c:Class_sensor) - [:COMPOSED] -> (s:Class_station)
            MERGE (e) - [:OBSERVED] -> (s)
        '''
        return Query(query_string=query_str, kwargs={})

    @staticmethod
    def get_create_processing_station_entities_and_correlate_to_events_query():
        query_str = '''
            MATCH (e) - [:OBSERVED] ->  (cs:Class_station {type:"Processing"})
            WITH e, cs, cs.type + cs.start_sensor+cs.end_sensor AS id
            MERGE (s:Entity:Station {entityType: "Station", type: cs.type, 
                                    start_sensor: cs.start_sensor, end_sensor: cs.end_sensor,
                                    ID: id, uID:"Station_"+id})
            MERGE (e) - [:CORR] -> (s)
        '''
        return Query(query_string=query_str, kwargs={})

    @staticmethod
    def get_create_non_processing_station_entities_and_correlate_to_events_query():
        query_str = '''
                MATCH (e) - [:OBSERVED] -> (cs:Class_station)
                WHERE cs.type <> "Processing"
                WITH e, cs, cs.type + cs.sensor AS id
                MERGE (s:Entity:Station {entityType: "Station", type: cs.type, 
                                        sensor: cs.sensor, 
                                        ID: id, uID:"Station_"+id})
                MERGE (e) - [:CORR] -> (s)
            '''
        return Query(query_string=query_str, kwargs={})
