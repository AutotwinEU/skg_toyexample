import os
from pathlib import Path

from ekg_creator.data_managers.interpreters import Interpreter
from ekg_creator.data_managers.semantic_header import SemanticHeader
from ekg_creator.database_managers.EventKnowledgeGraph import EventKnowledgeGraph, DatabaseConnection
from ekg_creator.data_managers.datastructures import ImportedDataStructures
from ekg_creator.utilities.performance_handling import Performance

from ekg_creator.database_managers import authentication

from ekg_creator.cypher_queries.custom_query_library import CustomCypherQueryLibrary as ccql

# several steps of import, each can be switch on/off
from colorama import Fore

connection = authentication.connections_map[authentication.Connections.LOCAL]

dataset_name = 'ToyExample'
semantic_header_path = Path(f'json_files/{dataset_name}.json')
use_sample = False

query_interpreter = Interpreter("Cypher")
semantic_header = SemanticHeader.create_semantic_header(semantic_header_path, query_interpreter)
perf_path = os.path.join("..", "perf", dataset_name, f"{dataset_name}Performance.csv")
number_of_steps = 100

ds_path = Path(f'json_files/{dataset_name}_DS.json')
datastructures = ImportedDataStructures(ds_path)

step_clear_db = True
step_populate_graph = True
step_analysis = True

use_preloaded_files = False  # if false, read/import files instead
verbose = False

db_connection = DatabaseConnection(db_name=connection.user, uri=connection.uri, user=connection.user,
                                   password=connection.password, verbose=verbose)


def create_graph_instance(perf: Performance) -> EventKnowledgeGraph:
    """
    Creates an instance of an EventKnowledgeGraph
    @return: returns an EventKnowledgeGraph
    """

    return EventKnowledgeGraph(db_connection=db_connection, db_name=connection.user,
                               batch_size=5000, event_tables=datastructures, use_sample=use_sample,
                               semantic_header=semantic_header, perf=perf)


def clear_graph(graph: EventKnowledgeGraph, perf: Performance) -> None:
    """
    # delete all nodes and relations in the graph to start fresh
    @param graph: EventKnowledgeGraph
    @param perf: Performance
    @return: None
    """

    print("Clearing DB...")
    graph.clear_db()
    perf.finished_step(log_message=f"Cleared DB")


def populate_graph(graph: EventKnowledgeGraph, perf: Performance):
    graph.create_static_nodes_and_relations()

    # import the events from all sublogs in the graph with the corresponding labels
    graph.import_data()
    perf.finished_step(log_message=f"(:Event) nodes done")

    # TODO: constraints in semantic header?
    graph.set_constraints()
    perf.finished_step(log_message=f"All constraints are set")

    graph.create_log()
    perf.finished_step(log_message=f"(:Log) nodes and [:HAS] relations done")

    # for each entity, we add the entity nodes to graph and correlate them to the correct events
    graph.create_entities_by_nodes(node_label="Event")
    perf.finished_step(log_message=f"(:Entity) nodes done")

    graph.correlate_events_to_entities(node_label="Event")
    perf.finished_step(log_message=f"[:CORR] edges done")

    graph.create_classes()
    perf.finished_step(log_message=f"(:Class) nodes done")

    graph.create_entity_relations_using_nodes()
    graph.create_entity_relations_using_relations()
    perf.finished_step(log_message=f"[:REL] edges done")

    graph.create_entities_by_relations()
    perf.finished_step(log_message=f"Reified (:Entity) nodes done")

    graph.correlate_events_to_reification()
    perf.finished_step(log_message=f"[:CORR] edges for Reified (:Entity) nodes done")

    graph.create_df_edges()
    perf.finished_step(log_message=f"[:DF] edges done")

    graph.delete_parallel_dfs_derived()
    perf.finished_step(log_message=f"Deleted all duplicate parallel [:DF] edges done")

    graph.merge_duplicate_df()
    perf.finished_step(log_message=f"Merged duplicate [:DF] edges done")


def main() -> None:
    """
    Main function, read all the logs, clear and create the graph, perform checks
    @return: None
    """
    if use_preloaded_files:
        print(Fore.RED + '💾 Preloaded files are used!' + Fore.RESET)
    else:
        print(Fore.RED + '📝 Importing and creating files' + Fore.RESET)

    # performance class to measure performance

    perf = Performance(perf_path, number_of_steps=number_of_steps)
    graph = create_graph_instance(perf)

    if step_clear_db:
        clear_graph(graph=graph, perf=perf)

    if step_populate_graph:
        populate_graph(graph=graph, perf=perf)

    if step_analysis:
        graph.create_df_process_model(entity_type="Pizza")
        graph.do_custom_query("create_stations", entity_type="Pizza")
        graph.do_custom_query("correlate_events_to_station")

        graph.create_df_edges(entity_types=["Station"])

        graph.save_event_log(entity="Pizza", additional_event_attributes=["sensor"])
        graph.save_event_log(entity="Station", additional_event_attributes=["pizzaId"])

    perf.finish()
    perf.save()

    graph.print_statistics()

    db_connection.close_connection()


if __name__ == "__main__":
    main()
