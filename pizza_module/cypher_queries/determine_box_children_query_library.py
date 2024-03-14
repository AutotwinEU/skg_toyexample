from promg import Query


class BoxCypherQueryLibrary:

    @staticmethod
    def get_set_box_event_labels_based_on_activity_query(is_simulated):

        simulated_check = "{simulated:True}" if is_simulated else ""
        # language=sql
        query_str = '''
            MATCH (e:Event $simulated_check)
            WHERE e.activity =  "Pass Sensor CS4401" OR e.activity = "Pass Sensor CS4301"
            OPTIONAL MATCH (f:Event) - [:DF_BOX] -> (e)
            SET e:NewBoxEvent, f:NewBoxLastEvent
        '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "simulated_check": simulated_check
                     })

    @staticmethod
    def get_delete_box_event_labels_query():
        # language=sql
        query_str = '''
            MATCH (e:NewBoxEvent|NewBoxLastEvent)
            REMOVE e:NewBoxEvent:NewBoxLastEvent
        '''

        return Query(query_str=query_str)

    @staticmethod
    def get_set_box_event_labels_based_on_first_event_query(is_simulated):

        simulated_check = "{simulated:True}" if is_simulated else ""
        # language=sql
        query_str = '''
            MATCH (e:Event) - [:ACTS_ON] -> (b:Box $simulated_check)
            WHERE NOT EXISTS ((:Event) - [:DF_BOX] -> (e))
            SET e:NewBoxEvent
        '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "simulated_check": simulated_check
                     })

    @staticmethod
    def get_set_box_event_labels_based_on_last_event_query(is_simulated):

        simulated_check = "{simulated:True}" if is_simulated else ""
        # language=sql
        query_str = '''
            MATCH (f:Event) - [:ACTS_ON] -> (b:Box $simulated_check)
            WHERE NOT EXISTS ((f) - [:DF_BOX] -> (:Event))
            SET f:NewBoxLastEvent
        '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "simulated_check": simulated_check
                     })

    @staticmethod
    def get_create_box_children_query(is_simulated):

        simulated_check = "{simulated:True}" if is_simulated else ""
        # language=sql
        query_str = '''
            MATCH (start_event:Event:NewBoxEvent)
            CALL apoc.path.expandConfig(start_event, {relationshipFilter: "DF_BOX>", 
            labelFilter:"+Event|/NewBoxLastEvent"})
            YIELD path
            MATCH (start_event) - [:ACTS_ON] -> (b:Box $simulated_check)
            CALL apoc.refactor.cloneNodes([b])
            YIELD input, output as new_b, error
            SET new_b:Run
            CREATE (new_b) - [:HAS_RUN] -> (b)
            WITH nodes(path) as events, b, new_b
            CALL {WITH events, b, new_b
             UNWIND events as  box_event
            MATCH (box_event) - [r:ACTS_ON] -> (b)
            DELETE r
            CREATE (box_event) - [:ACTS_ON] -> (new_b)}
        '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "simulated_check": simulated_check
                     })
    @staticmethod
    def get_create_box_single_children_query(is_simulated):
        simulated_check = "{simulated:True}" if is_simulated else ""
        # language=sql
        query_str = '''
            MATCH (start_event:Event:NewBoxEvent:NewBoxLastEvent)
            MATCH (start_event) - [:ACTS_ON] -> (b:Box $simulated_check)
            CALL apoc.refactor.cloneNodes([b])
            YIELD input, output as new_b, error
            SET new_b:Run
            SET b:AllRuns
            CREATE (new_b) - [:HAS_RUN] -> (b)
            WITH start_event, b, new_b
            CALL {WITH start_event, b, new_b
            MATCH (start_event) - [r:ACTS_ON] -> (b)
            DELETE r
            CREATE (start_event) - [:ACTS_ON] -> (new_b)}
        '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "simulated_check": simulated_check
                     })

    @staticmethod
    def get_create_df_path_boxes_query(is_simulated):
        simulated_check = "{simulated:True}" if is_simulated else ""
        # language=sql
        query_str = '''
            MATCH (parent:Box $simulated_check) <- [:HAS_RUN] - (b:Box:Run) <- [:ACTS_ON] - (e:Event)
            WITH parent, b, e ORDER by e.timestamp
            WITH parent, collect(distinct b) as children
            CALL {WITH children
                UNWIND range(0,size(children)-2) AS i
                WITH children[i] as first, children[i+1] as second, i
                CREATE (first) - [:NEXT_RUN] -> (second)
            }
            CALL {WITH children
                UNWIND range(0, size(children)-1) AS i
                WITH children[i] as child, i
                SET child.runId = child.sysId + "-" + i}
            CALL {WITH children, parent
                UNWIND children as child
                MATCH (parent) - [:EXTRACTED_FROM] -> (r:Record)    
                MERGE (child) - [:EXTRACTED_FROM] -> (r) 
            }
        '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "simulated_check": simulated_check
                     })

    @staticmethod
    def get_create_run_id_children_query(is_simulated):

        simulated_check = "{simulated:True}" if is_simulated else ""
        # language=sql
        query_str = '''
                MATCH (parent:Box $simulated_check) <- [:HAS_RUN] - (b:Box:Run) <- [:ACTS_ON] - (e:Event)
                WITH parent, b, e ORDER by e.timestamp
                WITH parent, collect(distinct b) as children
                CALL {WITH children
                    UNWIND range(0, size(children)-1) AS i
                    WITH children[i] as child, i
                    SET child.runId = child.sysId + "-" + i}
            '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "simulated_check": simulated_check
                     })

    @staticmethod
    def get_create_extracted_from_record_query(is_simulated):
        simulated_check = "{simulated:True}" if is_simulated else ""
        # language=sql
        query_str = '''
            MATCH (parent:Box $simulated_check) <- [:HAS_RUN] - (b:Box:Run) <- [:ACTS_ON] - (e:Event)
            WITH parent, b, e ORDER by e.timestamp
            WITH parent, collect(distinct b) as children
            CALL {WITH children, parent
                UNWIND children as child
                MATCH (parent) - [:EXTRACTED_FROM] -> (r:Record)    
                MERGE (child) - [:EXTRACTED_FROM {inferred: true}] -> (r) 
            }
            DETACH DELETE parent
        '''

        return Query(query_str=query_str,
                     template_string_parameters={
                         "simulated_check": simulated_check
                     })
