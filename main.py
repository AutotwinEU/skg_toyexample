import os
from datetime import datetime
import time
from pathlib import Path
import random

import numpy as np
from promg import SemanticHeader, OcedPg
from promg import DatabaseConnection
from promg import DatasetDescriptions
from promg import Performance
from promg import authentication
from promg.database_managers.authentication import Credentials
from promg.modules.db_management import DBManagement
from custom_module.modules.process_model_discovery import ProcessDiscovery
from promg.modules.exporter import Exporter

from custom_module.modules.df_discovery import DFDiscoveryModule
from custom_module.modules.pizza_line import PizzaLineModule
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
use_local = True


def main() -> None:
    """
    Main function, read all the logs, clear and create the graph, perform checks
    @return: None
    """
    _step_clear_db = step_clear_db
    if not use_local:  # swap
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
    db_connection = DatabaseConnection.set_up_connection(credentials=credentials,
                                                         verbose=verbose)

    db_manager = DBManagement()
    if _step_clear_db:
        db_manager.clear_db(replace=True)
        db_manager.set_constraints()

    if step_populate_graph:
        oced_pg = OcedPg(dataset_descriptions=datastructures,
                         use_sample=use_sample,
                         use_preprocessed_files=use_preprocessed_files)

        oced_pg.load()
        oced_pg.create_nodes_by_records()

        pizza_module = PizzaLineModule()
        if version_number == "V3":
            pizza_module.merge_sensor_events(version_number=version_number)
            pizza_module.connect_wip_sensor_to_assembly_line(version_number=version_number)

        oced_pg.create_relations()

        df_discovery = DFDiscoveryModule()
        df_edges_to_be_created = [
            {"entity_type": "Pizza", "df_label": "DF_CONTROL_FLOW_ITEM"},
            {"entity_type": "Pack", "df_label": "DF_CONTROL_FLOW_ITEM"},
            {"entity_type": "Box", "df_label": "DF_CONTROL_FLOW_ITEM"},
            {"entity_type": "Pallet", "df_label": "DF_CONTROL_FLOW_ITEM"},
            {"entity_type": "Sensor", "df_label": "DF_SENSOR"},
            {"entity_type": "Station", "df_label": "DF_STATION"},
            {"entity_type": "Operator", "df_label": "DF_OPERATOR"}]

        for df in df_edges_to_be_created:
            df_discovery.create_df_edges_for_entity(entity_type=df["entity_type"], df_label=df["df_label"],
                                                    version_number=version_number)

        for station_id in ["PackStation", "BoxStation", "PalletStation"]:
            pizza_module.infer_part_of_relation(version_number=version_number, station_id=station_id)

        df_edges_to_be_created = [
            {"entity_type": "PizzaPack", "df_label": "DF_CONTROL_FLOW_ITEM"},
            {"entity_type": "PackBox", "df_label": "DF_CONTROL_FLOW_ITEM"},
            {"entity_type": "BoxPallet", "df_label": "DF_CONTROL_FLOW_ITEM"}]

        for df in df_edges_to_be_created:
            df_discovery.create_df_edges_for_entity(entity_type=df["entity_type"], df_label=df["df_label"],
                                                    version_number=version_number)

        if version_number == "V3":
            pizza_module.complete_quality(version_number=version_number)
            pizza_module.connect_operators_to_station(version_number=version_number)

        process_discoverer = ProcessDiscovery()
        process_discoverer.create_df_process_model(df_label="DF_CONTROL_FLOW_ITEM", df_a_label="DF_A_CONTROL_FLOW_ITEM")

        pizza_module.connect_stations_and_sensors()

        exporter = Exporter()
        exporter.save_event_log(entity_type="Pizza")

        #
        # event_log = graph.custom_module.read_log()
        # process_model_graph = process_discovery.get_discovered_proces_model(event_log)
        # graph.custom_module.write_attributes(graph=process_model_graph)

    performance.finish_and_save()
    db_manager.print_statistics()

    db_connection.close_connection()


if __name__ == "__main__":
    main()
