import os
from datetime import datetime

from promg import SemanticHeader, DatabaseConnection, DatasetDescriptions, Performance, Configuration

from pizza_module.main_functionalities import check_remote_connection, clear_db, load_data, transform_data, \
    print_statistics, delete_data, prepare


def clear_db_config(config):
    db_connection = DatabaseConnection.set_up_connection(config=config)
    # only clear db if we are working with local connection
    clear_db(db_connection)


def populate_graph(config: Configuration,
                   step_preprocess_files: bool = True,
                   input_directory=os.path.join(os.getcwd(), "data"),
                   file_suffix=""):
    """
        Main function, read all the logs, clear and create the graph, perform checks
        @return: None
        """

    semantic_header = SemanticHeader.create_semantic_header(config=config)
    dataset_descriptions = DatasetDescriptions(config=config)
    # performance class to measure performance
    performance = Performance.set_up_performance(config=config)

    db_connection = DatabaseConnection.set_up_connection(config=config)

    if step_preprocess_files:
        prepare(input_path=input_directory, file_suffix=file_suffix)
    load_data(db_connection=db_connection,
              config=config,
              semantic_header=semantic_header,
              dataset_descriptions=dataset_descriptions)
    # EV: Fix required
    #transform_data(db_connection=db_connection,
    #               config=config,
    #               semantic_header=semantic_header,
    #               dataset_descriptions=dataset_descriptions)
    transform_data(db_connection=db_connection,
                   config=config)

    performance.finish_and_save()
    print_statistics(db_connection)

    db_connection.close_connection()


def delete_data(config):
    db_connection = DatabaseConnection.set_up_connection(config=config)
    semantic_header = SemanticHeader.create_semantic_header(config=config)
    dataset_descriptions = DatasetDescriptions(config=config)
    files = dataset_descriptions.get_structure_name_file_mapping()
    for _, file_names in files.items():
        delete_data(db_connection=db_connection,
                    semantic_header=semantic_header,
                    logs=file_names)


def main(step_clear_db,
         import_ground_truth,
         import_simulation_data,
         _config_ground_truth: Configuration,
         _config_simulation: Configuration) -> None:
    print("Started at =", datetime.now().strftime("%H:%M:%S"))

    if "bolt://localhost" not in _config_ground_truth.uri:
        use_remote_connection = check_remote_connection(_config_ground_truth)
        if not use_remote_connection:
            return
    else:
        use_remote_connection = False

    if not use_remote_connection and step_clear_db:
        clear_db_config(_config_ground_truth)

    if import_ground_truth:
        # import ground truth data
        populate_graph(config=_config_ground_truth,
                       step_preprocess_files=False)

    if import_simulation_data:
        populate_graph(config=_config_simulation,
                       step_preprocess_files=False,
                       input_directory=os.path.join(os.getcwd(), "data", "ToyExampleV3Simulation"),
                       file_suffix="_sim")


if __name__ == "__main__":
    config_ground_truth = Configuration.init_conf_with_config_file()
    config_simulation = Configuration.init_conf_with_config_file('config_sim.yaml')

    main(step_clear_db=True,
         import_ground_truth=True,
         import_simulation_data=True,
         _config_ground_truth=config_ground_truth,
         _config_simulation=config_simulation)

    delete_data(config_simulation)
