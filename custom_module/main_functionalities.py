import random

from promg import OcedPg
from promg.modules.db_management import DBManagement

from custom_module.modules.delete_method import DeleteModule
from custom_module.modules.process_model_discovery import ProcessDiscovery
from custom_module.modules.df_discovery import DFDiscoveryModule
from custom_module.modules.pizza_line import PizzaLineModule

# several steps of import, each can be switch on/off
from colorama import Fore

from preprocess.preprocess_data import prepare_files

# several steps of import, each can be switch on/off
step_clear_db = True
step_populate_graph = True
step_delete_data = True


def check_remote_connection(config) -> bool:
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


def prepare(input_path, file_suffix=""):
    prepare_files(input_path, file_suffix)


def clear_db(db_connection):
    db_manager = DBManagement(db_connection)
    print(Fore.RED + 'Clearing the database.' + Fore.RESET)
    db_manager.clear_db(replace=True)
    db_manager.set_constraints()


def print_statistics(db_connection):
    db_manager = DBManagement(db_connection)
    db_manager.print_statistics()


def load_data(db_connection, config, semantic_header, dataset_descriptions):
    if config.use_preprocessed_files:
        print(Fore.RED + '💾 Preloaded files are used!' + Fore.RESET)
    else:
        print(Fore.RED + '📝 Importing and creating files' + Fore.RESET)

    oced_pg = OcedPg(dataset_descriptions=dataset_descriptions,
                     use_sample=config.use_sample,
                     use_preprocessed_files=config.use_preprocessed_files,
                     import_directory=config.import_directory,
                     database_connection=db_connection,
                     semantic_header=semantic_header)

    oced_pg.load()


def transform_data(db_connection, config, semantic_header, dataset_descriptions):
    oced_pg = OcedPg(dataset_descriptions=dataset_descriptions,
                     use_sample=config.use_sample,
                     use_preprocessed_files=config.use_preprocessed_files,
                     import_directory=config.import_directory,
                     database_connection=db_connection,
                     semantic_header=semantic_header)
    oced_pg.create_nodes_by_records()

    pizza_module = PizzaLineModule(database_connection=db_connection)
    oced_pg.create_relations()

    df_discovery = DFDiscoveryModule(db_connection)
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

    process_discoverer = ProcessDiscovery(db_connection)
    process_discoverer.create_df_process_model(df_label="DF_CONTROL_FLOW_ITEM", df_a_label="DF_A_CONTROL_FLOW_ITEM")

    pizza_module.connect_stations_and_sensors()


def delete_data2(db_connection, semantic_header, logs):
    delete_module = DeleteModule(db_connection, semantic_header)
    delete_module.delete_records(logs=logs)
