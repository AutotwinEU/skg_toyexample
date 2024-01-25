from datetime import datetime
import random

from promg import SemanticHeader, OcedPg, DatabaseConnection, DatasetDescriptions, Performance, Configuration
from promg.modules.db_management import DBManagement
from promg.modules.exporter import Exporter

from custom_module.modules.process_model_discovery import ProcessDiscovery
from custom_module.modules.df_discovery import DFDiscoveryModule
from custom_module.modules.pizza_line import PizzaLineModule

# several steps of import, each can be switch on/off
from colorama import Fore

config = Configuration()
semantic_header = SemanticHeader.create_semantic_header(config=config)
dataset_descriptions = DatasetDescriptions(config=config)

# several steps of import, each can be switch on/off
step_clear_db = True
step_populate_graph = True


def check_remote_connection() -> bool:
    number_str = str(random.randint(0, 9999)).zfill(4)
    request_permission = input(
        f"You are going to make changes to {config.uri}. Is this your intention? Type {number_str} for Yes or "
        f"N [No]")
    if request_permission.lower().strip() == number_str:
        return True
    elif request_permission.lower().strip() == "n" or request_permission.lower().strip() == "no":
        print(f"As it is not your intention to make changes to {config.uri}, change use_local to True")
        return False
    else:
        print(f"Invalid input")
        return False


def main() -> None:
    """
    Main function, read all the logs, clear and create the graph, perform checks
    @return: None
    """
    print("Started at =", datetime.now().strftime("%H:%M:%S"))

    if "bolt://localhost" not in config.uri:
        use_remote_connection = check_remote_connection()
        if not use_remote_connection:
            return
    else:
        use_remote_connection = False

    db_connection = DatabaseConnection.set_up_connection(config=config)
    # performance class to measure performance
    performance = Performance.set_up_performance(config=config)
    db_manager = DBManagement()

    # only clear db if we are working with local connection
    if step_clear_db and not use_remote_connection:
        print(Fore.RED + 'Clearing the database.' + Fore.RESET)
        db_manager.clear_db(replace=True)
        db_manager.set_constraints()

    if step_populate_graph:
        if config.use_preprocessed_files:
            print(Fore.RED + '💾 Preloaded files are used!' + Fore.RESET)
        else:
            print(Fore.RED + '📝 Importing and creating files' + Fore.RESET)

        oced_pg = OcedPg(dataset_descriptions=dataset_descriptions,
                         use_sample=config.use_sample,
                         use_preprocessed_files=config.use_preprocessed_files,
                         import_directory=config.import_directory)

        oced_pg.load()
        oced_pg.create_nodes_by_records()

        pizza_module = PizzaLineModule()
        pizza_module.merge_sensor_events()
        pizza_module.connect_wip_sensor_to_assembly_line()

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
            df_discovery.create_df_edges_for_entity(entity_type=df["entity_type"], df_label=df["df_label"])

        for station_id in ["PackStation", "BoxStation", "PalletStation"]:
            pizza_module.infer_part_of_relation(station_id=station_id)

        df_edges_to_be_created = [
            {"entity_type": "PizzaPack", "df_label": "DF_CONTROL_FLOW_ITEM"},
            {"entity_type": "PackBox", "df_label": "DF_CONTROL_FLOW_ITEM"},
            {"entity_type": "BoxPallet", "df_label": "DF_CONTROL_FLOW_ITEM"}]

        for df in df_edges_to_be_created:
            df_discovery.create_df_edges_for_entity(entity_type=df["entity_type"], df_label=df["df_label"])

        pizza_module.complete_quality()
        pizza_module.connect_operators_to_station()

        process_discoverer = ProcessDiscovery()
        process_discoverer.create_df_process_model(df_label="DF_CONTROL_FLOW_ITEM", df_a_label="DF_A_CONTROL_FLOW_ITEM")

        pizza_module.connect_stations_and_sensors()

        exporter = Exporter()
        exporter.save_event_log(entity_type="Pizza")

    performance.finish_and_save()
    db_manager.print_statistics()

    db_connection.close_connection()


if __name__ == "__main__":
    main()
