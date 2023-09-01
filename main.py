import os
from datetime import datetime
from pathlib import Path

from promg import SemanticHeader, OcedPg
from promg import DatabaseConnection
from promg import DatasetDescriptions
from promg import Performance
from promg import authentication
from promg.modules.db_management import DBManagement
from promg.modules.process_discovery import ProcessDiscovery
from promg.modules.exporter import Exporter

from custom_module.modules.pizza_line import PizzaLineModule
from tts_credentials import remote

# several steps of import, each can be switch on/off
from colorama import Fore

from process_discovery.discover_process_model import ProcessDiscoveryLog

number = 3
dataset_name = f'ToyExamplev{number}'
version_number = f"V{number}"
semantic_header_path = Path(f'json_files/{dataset_name}.json')
config_path = Path(f'json_files/config.json')
use_sample = False

semantic_header = SemanticHeader.create_semantic_header(semantic_header_path)
perf_path = os.path.join("..", "perf", dataset_name, f"{dataset_name}Performance.csv")
number_of_steps = 100

ds_path = Path(f'json_files/{dataset_name}_DS.json')
datastructures = DatasetDescriptions(ds_path)

step_clear_db = True
step_populate_graph = True
step_analysis = True

use_preprocessed_files = False  # if false, read/import files instead
verbose = False
connection_key = authentication.Connections.LOCAL
# connection_key = authentication.Connections.REMOTE

def main() -> None:
    """
    Main function, read all the logs, clear and create the graph, perform checks
    @return: None
    """
    print("Started at =", datetime.now().strftime("%H:%M:%S"))
    if use_preprocessed_files:
        print(Fore.RED + '💾 Preloaded files are used!' + Fore.RESET)
    else:
        print(Fore.RED + '📝 Importing and creating files' + Fore.RESET)

    # performance class to measure performance

    performance = Performance.set_up_performance(dataset_name=dataset_name, use_sample=use_sample)
    db_connection = DatabaseConnection.set_up_connection_using_key(key=connection_key,
                                                                   verbose=verbose)

    db_manager = DBManagement()
    if step_clear_db:
        db_manager.clear_db(replace=True)
        db_manager.set_constraints()

    if step_populate_graph:
        oced_pg = OcedPg(dataset_descriptions=datastructures,
                         use_sample=use_sample,
                         use_preprocessed_files=use_preprocessed_files)
        pizza_module = PizzaLineModule()

        oced_pg.load()
        oced_pg.create_nodes_by_records()
        if version_number == "V3":
            pizza_module.merge_sensor_events(version_number=version_number)
            pizza_module.connect_wip_sensor_to_assembly_line(version_number=version_number)

        relations = [relation.type for relation in semantic_header.relations]
        relations_to_be_constructed_later = ["PART_OF_PIZZA_PACK", "PART_OF_PACK_BOX", "PART_OF_BOX_PALLET"]

        oced_pg.create_relations(list(set(relations) - set(relations_to_be_constructed_later)))

        oced_pg.create_df_edges()
        pizza_module.complete_corr(version_number=version_number)
        pizza_module.delete_df_edges(version_number=version_number)

        if version_number == "V3":
            pizza_module.complete_quality(version_number=version_number)
            pizza_module.connect_operators_to_station(version_number=version_number)

        oced_pg.create_relations(relations_to_be_constructed_later)

        oced_pg.create_df_edges()

        process_discoverer = ProcessDiscovery()

        process_discoverer.create_df_process_model(entity_type="Pizza")
        process_discoverer.create_df_process_model(entity_type="Pack")
        process_discoverer.create_df_process_model(entity_type="Box")
        process_discoverer.create_df_process_model(entity_type="Pallet")
        pizza_module.connect_stations_and_sensors()

        oced_pg.create_df_edges(entity_types=["Station"])

        exporter = Exporter()
        exporter.save_event_log(entity_type="Pizza")

        #
        # event_log = graph.custom_module.read_log()
        # process_model_graph = process_discovery.get_discovered_proces_model(event_log)
        # graph.custom_module.write_attributes(graph=process_model_graph)

    Performance().finish_and_save()
    db_manager.print_statistics()

    db_connection.close_connection()


if __name__ == "__main__":
    main()
