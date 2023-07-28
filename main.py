import os
from pathlib import Path

from promg import SemanticHeader
from promg import EventKnowledgeGraph, DatabaseConnection
from promg import ImportedDataStructures
from promg import Performance
from promg import authentication

from ekg_creator_custom.ekg_modules.ekg_custom_module import CustomModule
from tts_credentials import remote

# several steps of import, each can be switch on/off
from colorama import Fore

from process_discovery.discover_process_model import ProcessDiscovery

connection = authentication.connections_map[authentication.Connections.LOCAL]
use_local = False

dataset_name = 'ToyExamplev2'
semantic_header_path = Path(f'json_files/{dataset_name}.json')
config_path = Path(f'json_files/config.json')
use_sample = False

process_discovery = ProcessDiscovery(config_path)
semantic_header = SemanticHeader.create_semantic_header(semantic_header_path)
perf_path = os.path.join("..", "perf", dataset_name, f"{dataset_name}Performance.csv")
number_of_steps = 100

ds_path = Path(f'json_files/{dataset_name}_DS.json')
datastructures = ImportedDataStructures(ds_path)

step_clear_db = False
step_populate_graph = True
step_analysis = True

use_preloaded_files = False  # if false, read/import files instead
verbose = False

if use_local:
    db_connection = DatabaseConnection(db_name=connection.user, uri=connection.uri, user=connection.user,
                                       password=connection.password, verbose=verbose)
else:
    db_connection = DatabaseConnection(db_name=remote.user, uri=remote.uri, user=remote.user,
                                       password=remote.password, verbose=verbose)


def create_graph_instance(perf: Performance) -> EventKnowledgeGraph:
    """
    Creates an instance of an EventKnowledgeGraph
    @return: returns an EventKnowledgeGraph
    """

    return EventKnowledgeGraph(db_connection=db_connection, db_name=connection.user,
                               batch_size=5000, specification_of_data_structures=datastructures, use_sample=use_sample,
                               semantic_header=semantic_header, perf=perf,
                               custom_module_name=CustomModule)


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
    perf.finished_step(log_message=f"(:Record) nodes done")

    # TODO: constraints in semantic header?
    graph.set_constraints()
    perf.finished_step(log_message=f"All constraints are set")

    # for each entity, we add the entity nodes to graph and correlate them to the correct events
    graph.create_nodes_by_records()
    perf.finished_step(log_message=f"(:Entity) nodes done")

    graph.custom_module.complete_corr()

    graph.create_relations_using_record()
    graph.create_relations_using_relations()
    perf.finished_step(log_message=f"Reified (:Entity) nodes done")

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
        graph.create_df_process_model(entity_type="Pack")
        graph.create_df_process_model(entity_type="Box")
        graph.create_df_process_model(entity_type="Pallet")
        # graph.custom_module.create_station_aggregation(entity_type="Pizza")
        graph.custom_module.connect_activities_to_location()
        graph.custom_module.observe_events_to_station_aggregation_query()
        graph.custom_module.connect_stations_and_sensors()
        # graph.custom_module.update_sensor_attributes()

        # create Station Entities
        # graph.do_custom_query("create_station_entities_and_correlate_to_events")

        graph.create_df_edges(entity_types=["Station"])

        # graph.save_event_log(entity_type="Pizza")
        # graph.save_event_log(entity_type="Station")
        #
        # event_log = graph.custom_module.read_log()
        # process_model_graph = process_discovery.get_discovered_proces_model(event_log)
        # graph.custom_module.write_attributes(graph=process_model_graph)

    perf.finish()
    perf.save()

    graph.print_statistics()

    db_connection.close_connection()


if __name__ == "__main__":
    main()
