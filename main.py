import os
from datetime import datetime
import time
from pathlib import Path
import random

import numpy as np
from promg import SemanticHeader
from promg import OcedPg
from promg import DatabaseConnection
from promg import DatasetDescriptions
from promg import Performance
from promg import authentication
from promg.database_managers.authentication import Credentials
from promg.modules.db_management import DBManagement
from promg.modules.process_discovery import ProcessDiscovery
from promg.modules.exporter import Exporter

from custom_module.modules.pizza_simulation import create_simulated_data
from custom_module.modules.pizza_line import PizzaLineModule
from custom_module.modules.pizza_performance import PizzaPerformanceModule
from tts_credentials import remote

# several steps of import, each can be switch on/off
from colorama import Fore

from process_discovery.discover_process_model import ProcessDiscoveryLog
randint = random.randint(0, 9999)

number = 3
dataset_name = f'ToyExamplev{number}'
version_number = f"V{number}"
semantic_header_path = Path(f'json_files/{dataset_name}.json')
config_path = Path(f'json_files/config.json')
use_sample = False

perf_path = os.path.join("..", "perf", dataset_name, f"{dataset_name}Performance.csv")
number_of_steps = 100

ds_path = Path(f'json_files/{dataset_name}_DS.json')

step_clear_db = True
step_populate_graph = True
step_analysis = True

perform_simulation = True       # perform a fresh simulation before generating the SKG?
performance_analysis = True     # add performance analysis to the SKG?

use_preprocessed_files = False  # if false, read/import files instead
verbose = False
use_local = True


def main(db_name,
         semantic_header_p, ds_p,
         html_output_dir,
         simulator_dir, config_filename, data_dir, production_plan_and_stations_dir) -> None:
    """
    Main function, read all the logs, clear and create the graph, perform checks
    @return: None
    """
    semantic_header = SemanticHeader.create_semantic_header(semantic_header_p)
    datastructures = DatasetDescriptions(ds_p)

    _step_clear_db = step_clear_db
    if not use_local:
        number_str = str(randint).zfill(4)
        request_permission = input(
            f"You are going to make changes to the TTS instance. Is this your intention? Type {number_str} for Yes or "
            f"N [No]")
        if request_permission.lower().strip() == number_str:
            _step_clear_db = False
            credentials = remote
            pass
        elif request_permission.lower().strip() == "n" or request_permission.lower().strip() == "no":
            print("As it is not your intention to make changes to the TTS instance, change use_local to True")
            return
        else:
            print("Invalid input")
            return
    else:
        credentials = authentication.connections_map[authentication.Connections.LOCAL]

    print("Started at =", datetime.now().strftime("%H:%M:%S"))
    if use_preprocessed_files:
        print(Fore.RED + '💾 Preloaded files are used!' + Fore.RESET)
    else:
        print(Fore.RED + '📝 Importing and creating files' + Fore.RESET)

    # performance class to measure performance

    performance = Performance.set_up_performance(dataset_name=dataset_name, use_sample=use_sample)
    db_connection = DatabaseConnection.set_up_connection(credentials=credentials,verbose=verbose,db_name=db_name)

    if perform_simulation:
        create_simulated_data(simulator_dir,config_filename,data_dir,production_plan_and_stations_dir)

    db_manager = DBManagement()
    if _step_clear_db:
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

    if performance_analysis:
        perf_module = PizzaPerformanceModule(html_output_dir)
        perf_module.add_performance_to_skg()
        perf_module.retrieve_performance_from_skg()

    performance.finish_and_save()
    db_manager.print_statistics()

    db_connection.close_connection()


if __name__ == "__main__":
    # only needs to be set when simulation is enabled (otherwise neglected)
    simulator_dir = "Q:/PizzaLineComplete_V3.7_2023_11_17" # the TTS simulator directory
    config_filename = "runargsnogui.ini" # assumed to be located in the simulator dir
    data_dir = "R:/git2/data/ToyExampleV3" # the target directory of the simulation results and starting point of building the SKG
    production_plan_and_stations_dir = "R:/git/data/ToyExampleV3.ava" # a directory with production_plan.csv and stations.csv
    headers_dir = "R:/git2/data/ToyExampleV3.ava" # a processed data directory to "steal" the headers from

    # only needs to be set when performance analysis is enabled (otherwise neglected)
    html_output_dir="d:/temp2" # a website with performance results will be written to this path

    db_name="freek667"

    main(db_name, semantic_header_path, ds_path, html_output_dir, simulator_dir, config_filename, data_dir,
         production_plan_and_stations_dir)
