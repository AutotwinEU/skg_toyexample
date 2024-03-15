from __future__ import annotations

import os

from flask import Flask
from flask_cors import CORS

from api.exceptions.notfound import NotFoundException

from .exceptions.badrequest import BadRequestException
from .exceptions.validation import ValidationException

from .neo4j import init_db_connection, init_promg_configuration, init_performance

from .routes.db_manager import db_manager_routes
from .routes.oced_pg import oced_pg_routes

from .routes.performance import performance_routes

from dotenv import load_dotenv, find_dotenv

from .routes.status import status_routes
from .routes.swagger import swagger_ui_blueprint


def getenv_bool(name: str, default_value: bool | None = None) -> bool:
    true_ = ('true', '1', 't')  # Add more entries if you want, like: `y`, `yes`, `on`, ...
    false_ = ('false', '0', 'f')  # Add more entries if you want, like: `n`, `no`, `off`, ...
    value: str | None = os.getenv(name, None)
    if value is None:
        if default_value is None:
            raise ValueError(f'Variable `{name}` not set!')
        else:
            value = str(default_value)
    if value.lower() not in true_ + false_:
        raise ValueError(f'Invalid value `{value}` for variable `{name}`')
    return value in true_


def create_app(test_config=None):
    # Create and configure app
    # static_folder = os.path.join(os.path.dirname(__file__), '..', 'public')
    app = Flask(__name__)

    cors = CORS(app)

    dotenv_location = find_dotenv()
    load_dotenv(dotenv_location)

    app.config.from_mapping(
        NEO4J_URI=os.getenv('NEO4J_URI'),
        NEO4J_USERNAME=os.getenv('NEO4J_USERNAME'),
        NEO4J_DB_NAME=os.getenv('NEO4J_DB_NAME'),
        NEO4J_PASSWORD=os.getenv('NEO4J_PASSWORD'),
        NEO4J_DATABASE=os.getenv('NEO4J_DATABASE'),
        PROMG_SEMANTIC_HEADER_PATH=os.getenv('PROMG_SEMANTIC_HEADER_PATH'),
        PROMG_DATASET_DESCRIPTION_PATH=os.getenv('PROMG_DATASET_DESCRIPTION_PATH'),
        PROMG_SIM_SEMANTIC_HEADER_PATH=os.getenv('PROMG_SIM_SEMANTIC_HEADER_PATH'),
        PROMG_SIM_DATASET_DESCRIPTION_PATH=os.getenv('PROMG_SIM_DATASET_DESCRIPTION_PATH'),
        PROMG_USE_SAMPLE=getenv_bool('PROMG_USE_SAMPLE', False),
        PROMG_BATCH_SIZE=os.getenv('PROMG_BATCH_SIZE'),
        IMPORT_DIRECTORY=os.getenv('IMPORT_DIRECTORY'),
        SSO_EDM_TOKEN_URL=os.getenv('SSO_EDM_TOKEN_URL'),
        EDM_BASE_URL=os.getenv('EDM_BASE_URL'),
        EDM_KEYCLOAK_URL=os.getenv('EDM_KEYCLOAK_URL')
    )
    # Apply Test Config
    if test_config is not None:
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with app.app_context():
        app.promg_config = init_promg_configuration(
            semantic_header_path=app.config.get('PROMG_SEMANTIC_HEADER_PATH'),
            dataset_description_path=app.config.get('PROMG_DATASET_DESCRIPTION_PATH'),
            db_name=app.config.get('NEO4J_DB_NAME'),
            uri=app.config.get('NEO4J_URI'),
            user=app.config.get('NEO4J_USER'),
            password=app.config.get('NEO4J_PASSWORD'),
            verbose=False,
            batch_size=app.config.get('PROMG_BATCH_SIZE'),
            use_sample=app.config.get('PROMG_USE_SAMPLE'),
            use_preprocessed_files=False,
            import_directory=app.config.get('IMPORT_DIRECTORY')
        )
        app.promg_sim_config = init_promg_configuration(
            semantic_header_path=app.config.get('PROMG_SIM_SEMANTIC_HEADER_PATH'),
            dataset_description_path=app.config.get('PROMG_SIM_DATASET_DESCRIPTION_PATH'),
            db_name=app.config.get('NEO4J_DB_NAME'),
            uri=app.config.get('NEO4J_URI'),
            user=app.config.get('NEO4J_USER'),
            password=app.config.get('NEO4J_PASSWORD'),
            verbose=False,
            batch_size=app.config.get('PROMG_BATCH_SIZE'),
            use_sample=app.config.get('PROMG_USE_SAMPLE'),
            use_preprocessed_files=False,
            import_directory=app.config.get('IMPORT_DIRECTORY')
        )
        init_db_connection(
            uri=app.config.get('NEO4J_URI'),
            db_name=app.config.get('NEO4J_USERNAME'),
            user=app.config.get('NEO4J_USERNAME'),
            password=app.config.get('NEO4J_PASSWORD')
        )

    # Register Routes
    app.register_blueprint(db_manager_routes)
    app.register_blueprint(oced_pg_routes)
    app.register_blueprint(status_routes)
    app.register_blueprint(swagger_ui_blueprint)
    app.register_blueprint(performance_routes)

    @app.errorhandler(BadRequestException)
    def handle_bad_request(err):
        return {"message": str(err)}, 400

    @app.errorhandler(ValidationException)
    def handle_validation_exception(err):
        return {"message": str(err)}, 422

    @app.errorhandler(NotFoundException)
    def handle_not_found_exception(err):
        return {"message": str(err)}, 404

    return app
