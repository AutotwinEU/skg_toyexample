from promg.database_managers.db_connection import Query

class AnalysisQueryLibrary:

    @staticmethod
    def get_aggregate_df_relations_query(df_label: str,
                                         df_a_label: str,
                                         df_threshold: int = 0,
                                         relative_df_threshold: float = 0,
                                         exclude_self_loops=True) -> Query:

        # add relations between classes when desired
        if df_threshold == 0 and relative_df_threshold == 0:
            # corresponds to aggregate_df_relations &  aggregate_df_relations_for_entities in graphdb-event-logs
            # aggregate only for a specific entity type and event classifier

            # language=sql
            query_str = '''
                                MATCH 
                                (c1:Activity) -[:OBSERVED]-> (e1:Event) 
                                    -[df:$df_label]-> 
                                (e2:Event) <-  [:OBSERVED] - (c2:Activity)
                                $classifier_self_loops
                                WITH c1, c2, df.entityType as df_entity_type, count(df) AS df_freq
                                MERGE 
                                (c1) 
                                    -[rel2:$df_a_label {entityType: df_entity_type, type:'DF_A'}]-> 
                                (c2) 
                                ON CREATE SET rel2.count=df_freq'''
        else:
            # aggregate only for a specific entity type and event classifier
            # include only edges with a minimum threshold, drop weak edges (similar to heuristics miner)

            # language=sql
            query_str = '''
                                MATCH 
                                (c1:Activity) 
                                    -[:OBSERVED]->
                                (e1:Event) 
                                    -[df:$df_label]-> 
                                (e2:Event) <-[:OBSERVED]- (c2:Activity)
                                MATCH (e1) -[:CORR] -> (n) <-[:CORR]- (e2)
                                $classifier_self_loops
                                WITH c1, c2, df.entityType as df_entity_type, count(df) AS df_freq
                                WHERE df_freq > $df_threshold
                                OPTIONAL MATCH (c2:Activity) -[:OBSERVED]-> (e2b:Event) -[df2:$df_label]-> 
                                    (e1b:Event) <-[:OBSERVED]- (c2:Activity)
                                WITH c1,df_freq,df_entity_type, count(df2) AS df_freq2,c2
                                WHERE (df_freq*$relative_df_threshold > df_freq2)
                                MERGE 
                                (c1) 
                                    -[rel2:$df_a_label {entityType: df_entity_type, type:'DF_A'}]-> 
                                (c2) 
                                ON CREATE SET rel2.count=df_freq'''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "df_label": df_label,
                         "df_a_label": df_a_label,
                         "classifier_self_loops": "WHERE c1 <> c2" if exclude_self_loops else "",
                         "df_threshold": df_threshold,
                         "relative_df_threshold": relative_df_threshold
                     })
