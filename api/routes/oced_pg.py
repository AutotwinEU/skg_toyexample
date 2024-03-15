import os

from flask import Blueprint, current_app, make_response, request, json

from promg import DatasetDescriptions, SemanticHeader

from api.exceptions.exception_handler import db_exception_handler
from pizza_module.main_functionalities import load_data, transform_data, prepare, delete_data

oced_pg_routes = Blueprint("ocedpg", __name__, url_prefix="/oced_pg")


def get_config(is_simulation_data):
    if is_simulation_data:
        config = current_app.promg_sim_config
    else:
        config = current_app.promg_config

    return config


@oced_pg_routes.route('/load', methods=['POST'])
@db_exception_handler
def load_records_route():
    is_simulation_data = request.args.get('is_simulation_data').lower() in ['true', '1']
    config = get_config(is_simulation_data)
    if is_simulation_data:
        prepare(input_path=os.path.join(os.getcwd(), "data/simulation/raw"),
                file_suffix="_sim")
    else:
        prepare(input_path=os.path.join(os.getcwd(), "data/groundtruth/raw"))

    load_data(db_connection=current_app.connection,
              config=config
              )

    return make_response(
        'Loaded data into database!',
        200
    )


@oced_pg_routes.route('/transform', methods=['POST'])
@db_exception_handler
def transform_records():
    is_simulation_data = request.args.get('is_simulation_data').lower() in ['true', '1']
    config = get_config(is_simulation_data)

    transform_data(db_connection=current_app.connection,
                   config=config,
                   is_simulated_data=is_simulation_data)

    return make_response(
        'Transformed data using semantic header!',
        200
    )


@oced_pg_routes.route('/delete_simulated_data', methods=['POST'])
@db_exception_handler
def delete_simulated_data():
    config = get_config(is_simulation_data=True)
    delete_data(db_connection=current_app.connection,
                config=config)

    return make_response(
        'Deleted simulated data!',
        200
    )
