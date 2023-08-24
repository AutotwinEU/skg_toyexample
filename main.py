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
use_local = True

dataset_name = 'ToyExamplev3'
semantic_header_path = Path(f'json_files/{dataset_name}.json')
config_path = Path(f'json_files/config.json')
use_sample = False

process_discovery = ProcessDiscovery(config_path)
semantic_header = SemanticHeader.create_semantic_header(semantic_header_path)
perf_path = os.path.join("..", "perf", dataset_name, f"{dataset_name}Performance.csv")
number_of_steps = 100

ds_path = Path(f'json_files/{dataset_name}_DS.json')
datastructures = ImportedDataStructures(ds_path)

step_clear_db = True
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


def create_graph_instance() -> EventKnowledgeGraph:
    """
    Creates an instance of an EventKnowledgeGraph
    @return: returns an EventKnowledgeGraph
    """

    return EventKnowledgeGraph(db_connection=db_connection, db_name=connection.user,
                               batch_size=5000, specification_of_data_structures=datastructures, use_sample=use_sample,
                               semantic_header=semantic_header, perf_path=perf_path,
                               custom_module_name=CustomModule)


def clear_graph(graph: EventKnowledgeGraph) -> None:
    """
    # delete all nodes and relations in the graph to start fresh
    @param graph: EventKnowledgeGraph
    @return: None
    """

    print("Clearing DB...")
    graph.clear_db()


def populate_graph(graph: EventKnowledgeGraph):
    graph.set_constraints()
    graph.create_static_nodes_and_relations()

    # import the events from all sublogs in the graph with the corresponding labels
    graph.import_data()

    # for each entity, we add the entity nodes to graph and correlate them to the correct events
    graph.create_nodes_by_records()

    relations = [relation.type for relation in graph.semantic_header.relations]
    relations_to_be_constructed_later = ["PART_OF_PIZZA_PACK", "PART_OF_PACK_BOX", "PART_OF_BOX_PALLET"]

    graph.create_relations(list(set(relations) - set(relations_to_be_constructed_later)))
    graph.custom_module.complete_quality(version_number="V3")
    graph.custom_module.complete_corr(version_number="V3")
    graph.custom_module.connect_operators_to_station(version_number="V3")
    graph.create_relations(relations_to_be_constructed_later)

    graph.create_df_edges()

    graph.delete_parallel_dfs_derived()

    graph.merge_duplicate_df()


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

    graph = create_graph_instance()

    if step_clear_db:
        clear_graph(graph=graph)

    if step_populate_graph:
        populate_graph(graph=graph)

    if step_analysis:
        graph.create_df_process_model(entity_type="Pizza")
        graph.create_df_process_model(entity_type="Pack")
        graph.create_df_process_model(entity_type="Box")
        graph.create_df_process_model(entity_type="Pallet")
        graph.custom_module.connect_stations_and_sensors()

        graph.create_df_edges(entity_types=["Station"])

        graph.save_event_log(entity_type="Pizza")
        # graph.save_event_log(entity_type="Station")
        #
        # event_log = graph.custom_module.read_log()
        # process_model_graph = process_discovery.get_discovered_proces_model(event_log)
        # graph.custom_module.write_attributes(graph=process_model_graph)

    graph.save_perf()
    graph.print_statistics()

    db_connection.close_connection()


if __name__ == "__main__":
    main()
