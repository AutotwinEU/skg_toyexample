from promg import SemanticHeader
from promg.database_managers.db_connection import DatabaseConnection
from promg.utilities.performance_handling import Performance
from custom_module.cypher_queries.event_log_query_language import EventLogExtractorQueryLibrary as event_log_ql
import pandas as pd


class EventLogExtractor:
    def __init__(self):
        self.connection = DatabaseConnection()

    #@Performance.track("entity_type")
    def extract_event_log(self, entity_type):
        """
        Create event_log
        """
        if entity_type == "Pizza":
            event_log = self.connection.exec_query(event_log_ql.get_create_pizza_event_log_query)            
        
            df = pd.DataFrame()        
            for record in event_log:          
                single_pizza = record.values()
                for entry in single_pizza:                                             
                    df = pd.concat([df, pd.DataFrame(entry)], axis=0, ignore_index=True)                
                        
            df = df.groupby('pizzaId').apply(lambda x: x.drop_duplicates(subset='eventId')).reset_index(drop=True)
            # Sort by 'pizzaId' and 'timestamp'
            sorted_df = df.sort_values(by=['pizzaId', 'timestamp']).reset_index(drop=True)                       
                    
            return sorted_df
        else:
            raise ValueError(f"Function not defined for entity type {entity_type}.")
        
    #@Performance.track("entity_type")
    def create_causal_links(self, entity_type,mapping):
        """
        Create event_log
        """
        if entity_type == "Pizza":
            for index, row in mapping.iterrows():
            # Access individual values in the row
                column1 = row['column1']
                column2 = row['column2']
                coefficient = row['coefficient']
                self.connection.exec_query(event_log_ql.get_set_directly_causes,
                                    **{
                                       "activity1": column1, "activity2": column2, "coefficient":coefficient
                                   })        
            
        else:
            raise ValueError(f"Function not defined for entity type {entity_type}.")
        
            
        
