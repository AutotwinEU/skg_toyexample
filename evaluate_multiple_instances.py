from promg import DatabaseConnection
from promg.database_managers import authentication

from custom_module.modules.pizza_design_space_exploration import one_random_neighbour, best_performance_neighbour, \
    starting_design_space, design_space_all, simulator_config, design_space_small_to_test, random_instance, \
    most_similar_neighbour, d_instance_to_database_name, d_instance_to_filename
from custom_module.modules.pizza_performance_aggregated import add_aggregated_performance
from custom_module.cypher_queries.db_management_queries import DBManagementQueries as dbmq
from evaluate_one_instance import evaluate_one_instance


def delete_all_dbs_except_for_neo4j_and_system():
    credentials = authentication.connections_map[authentication.Connections.LOCAL]
    db_connection = DatabaseConnection.set_up_connection(credentials=credentials, verbose=False)
    dbs = db_connection.exec_query(dbmq.return_db_list)
    if dbs is not None:
        for db in dbs:
            db_connection.exec_query(dbmq.drop_db, **{"dbname": db["name"]})


def create_db(db_name):
    credentials = authentication.connections_map[authentication.Connections.LOCAL]
    db_connection = DatabaseConnection.set_up_connection(credentials=credentials, verbose=False)
    db_connection.exec_query(dbmq.create_db, **{"dbname": db_name})


def brute_force_evaluation(d_space_to_evaluate):
    d_instances_dir = "Q:/PizzaLineComplete_V3.7_2023_11_17/design_instances"  # the folder in which simulator .ini are stored
    simulator_dir = "Q:/PizzaLineComplete_V3.7_2023_11_17"  # the TTS simulator directory
    data_dir = "R:/git2/data/ToyExampleV3"  # the target directory of the simulation results and starting point of building the SKG
    data_example_dir = "R:/git2/data/ToyExampleV3.ava"  # a directory with production_plan.csv and stations.csv, and example headers
    html_output_dir = "D:/perf_analysis"  # a website with performance results will be written to this path
    json_dir = "R:/git2/json_files"  # the location of the semantic header and dataset descriptions
   
    delete_all_dbs_except_for_neo4j_and_system()
    for d_instance in d_space_to_evaluate:
        evaluate_one_instance(d_instance, html_output_dir, simulator_dir, d_instances_dir, data_dir, data_example_dir, json_dir)
    add_aggregated_performance(html_output_dir + "/aggregated")

def design_space_exploration(d_instance_to_evaluate, d_space_all, d_space_evaluated=None, first_time=True):
    if d_space_evaluated is None:
        d_space_evaluated = []
    d_instances_dir = "Q:/PizzaLineComplete_V3.7_2023_11_17/design_instances"  # the folder in which simulator .ini are stored
    simulator_dir = "Q:/PizzaLineComplete_V3.7_2023_11_17"  # the TTS simulator directory
    data_dir = "R:/git2/data/ToyExampleV3"  # the target directory of the simulation results and starting point of building the SKG
    data_example_dir = "R:/git2/data/ToyExampleV3.ava"  # a directory with production_plan.csv and stations.csv, and example headers
    html_output_dir = "D:/perf_analysis"  # a website with performance results will be written to this path
    json_dir = "R:/git2/json_files"  # the location of the semantic header and dataset descriptions

    if first_time:
        delete_all_dbs_except_for_neo4j_and_system()

    evaluate_one_instance(d_instance_to_evaluate, html_output_dir, simulator_dir, d_instances_dir, data_dir, data_example_dir, json_dir)

    d_space_evaluated.append(d_instance_to_evaluate)
    one_neighbour = best_performance_neighbour(d_space_evaluated, d_space_all)
    if one_neighbour is not None:
        design_space_exploration(one_neighbour, d_space_all, d_space_evaluated, False)
    else:
        print("Finished! No neighbours left -> Local optimum")


def conformance_checking(d_instance_begin, d_instance_goal, d_space_all, d_space_evaluated=None, first_time=True):
    if d_space_evaluated is None:
        d_space_evaluated = []
    d_instances_dir = "Q:/PizzaLineComplete_V3.7_2023_11_17/design_instances"  # the folder in which simulator .ini are stored
    simulator_dir = "Q:/PizzaLineComplete_V3.7_2023_11_17"  # the TTS simulator directory
    data_dir = "R:/git2/data/ToyExampleV3"  # the target directory of the simulation results and starting point of building the SKG
    data_example_dir = "R:/git2/data/ToyExampleV3.ava"  # a directory with production_plan.csv and stations.csv, and example headers
    html_output_dir = "D:/perf_analysis"  # a website with performance results will be written to this path
    json_dir = "R:/git2/json_files"  # the location of the semantic header and dataset descriptions

    if first_time:
        delete_all_dbs_except_for_neo4j_and_system()
        evaluate_one_instance(d_instance_goal, html_output_dir, simulator_dir, d_instances_dir, data_dir, data_example_dir, json_dir)
    evaluate_one_instance(d_instance_begin, html_output_dir, simulator_dir, d_instances_dir, data_dir, data_example_dir, json_dir)
    d_space_evaluated.append(d_instance_begin)
    add_aggregated_performance(html_output_dir + "/aggregated")
    most_similar_design_neighbour=most_similar_neighbour(d_instance_goal,d_space_evaluated,d_space_all)
    if most_similar_design_neighbour is not None:
        conformance_checking(most_similar_design_neighbour, d_instance_goal, d_space_all, d_space_evaluated, False)

# DSE
# design_space_exploration(starting_design_space()[0], design_space_all())

# evaluate four designs
brute_force_evaluation(design_space_small_to_test())

# conformance checking
# conformance_checking(starting_design_space()[0], random_instance(design_space_all()), design_space_all())
