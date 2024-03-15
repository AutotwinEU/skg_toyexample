from string import Template

from promg import Query
from promg.data_managers.semantic_header import ConstructedNodes


class EventLogExtractorQueryLibrary:

    @staticmethod
    def get_create_pizza_event_log_query() -> Query:
        # language=sql
        query_str = '''
                     MATCH (e) - [:ACTS_ON] -> (p:Pizza) - [:IS_OF_TYPE] -> (et:EntityType) 
                        WHERE NOT EXISTS ((:Event) - [:DF_CONTROL_FLOW_ITEM] -> (e)) 
                        WITH e, p, et
                        MATCH (g:Event) - [:ACTS_ON] -> (:Entity) <- [:PART_OF*0..] - (p)
                        WHERE NOT EXISTS ((g) - [:DF_CONTROL_FLOW_ITEM] -> (:Event)) 
                        WITH e, g, p, et
                        MATCH (p) - [:HAS_PROPERTY] -> (pq:PizzaQualityAttribute)
                        MATCH path = (e:Event) - [:DF_CONTROL_FLOW_ITEM*0..] -> (g:Event) 
                        UNWIND nodes(path) as event 
                        MATCH (event) -[:OCCURRED_AT]->(s:Station) 
                        MATCH (event) -[:EXECUTED_BY]->(sen:Sensor) 
                        RETURN
                            split(elementId(event), ":")[-1] as eventId,
                            event.activity as activity,
                            event.timestamp as timestamp, 
                            p.sysId as pizzaId,
                            et.weight as weight,
                            et.height as height,
                            et.diameter as diameter,
                            pq.burned as burned,
                            pq.defective as defective,
                            sen.sysId as SensorType,
                            s.sysId as station
                            ORDER by  p.sysId, event.timestamp
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
                         "activity1": activity1,
                         "activity2": activity2
                     })
