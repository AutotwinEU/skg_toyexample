from string import Template

from promg import Query
from promg.data_managers.semantic_header import ConstructedNodes
class EventLogExtractorQueryLibrary:

    @staticmethod
    def get_create_pizza_event_log_query() -> Query:

        # language=sql
        query_str = '''
                     MATCH path = (e:Event) - [:DF_CONTROL_FLOW_ITEM*] -> (g:Event) 
                        MATCH (e) - [:ACTS_ON] -> (p:Pizza) - [:IS_OF_TYPE] -> (et:EntityType) 
                        MATCH (p) - [:HAS_PROPERTY] -> (pq:PizzaQualityAttribute)
                        WHERE NOT EXISTS ((:Event) - [:DF_CONTROL_FLOW_ITEM] -> (e)) 
                        AND NOT EXISTS ((g) - [:DF_CONTROL_FLOW_ITEM] -> (:Event)) 
                        UNWIND nodes(path) as event 
                        MATCH (event) -[:OCCURRED_AT]->(s:Station) 
                        MATCH (event) -[:EXECUTED_BY]->(sen:Sensor) 
                        WITH p, collect({eventId: right(elementId(event),5), 
                        activity: event.activity,
                        timestamp: event.timestamp, 
                        pizzaId: p.sysId,
                        weight: et.weight,
                        height: et.height,
                        diameter: et.diameter,
                        burned: pq.burned,
                        defective: pq.defective,
                        SensorType: sen.sysId,
                        station: s.sysId
                    }) as trace 
                    RETURN trace
                    '''

        return Query(query_str=query_str)
    

    
    @staticmethod
    def get_set_directly_causes(activity1, activity2, coefficient):
        query_str = '''
            MATCH (a1:Activity {activity: '$activity1'})
            OPTIONAL MATCH (a2:Activity {activity: '$activity2'})
            MERGE (a1) - [:CAUSES {weight: '$coefficient'}] -> (a2)

        '''
        return Query(query_str=query_str,
                     template_string_parameters={
                         "coefficient": coefficient,
                         "activity1":activity1,
                         "activity2": activity2
                     })
    
  