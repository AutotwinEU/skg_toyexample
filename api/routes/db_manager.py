import json

from flask import Blueprint, current_app, jsonify, make_response

from promg.modules.db_management import DBManagement

from api.exceptions.exception_handler import db_exception_handler
from pizza_module import main_functionalities
from pizza_module.main_functionalities import clear_db, get_event_log, get_model_ids as pizza_get_model_ids
from pizza_module.modules.statistic_method import StatisticsMethod

db_manager_routes = Blueprint("db_manager", __name__, url_prefix="/db_manager")


@db_manager_routes.route("/test_response")
def test_repsonse():
    return make_response(
        'Test worked!',
        200
    )


@db_manager_routes.route('/clear_db', methods=['POST'])
@db_exception_handler
def clear_db_route():
    clear_db(current_app.connection)

    return make_response(
        'Database Cleared!',
        200
    )


@db_manager_routes.route('/statistics', methods=['GET'])
@db_exception_handler
def get_statistics_route():
    dao_db_manager = StatisticsMethod(current_app.connection)
    result = dao_db_manager.get_statistics()

    item_list = {"records": [], "nodes": [], "relationships": [], "nodeCount": 0, "edgeCount": 0}

    for item in result:
        if "labels" in item:
            label = ":".join(item["labels"])
            count = item["numberOfNodes"]
            is_simulated = item["is_simulated"]
            item_list["nodes"].append({"label": label, "count": count, "is_simulated": is_simulated})
            item_list["nodeCount"] += count
        elif "log" in item:
            log = item["log"]
            count = item["numberOfNodes"]
            is_simulated = item["is_simulated"]
            item_list["records"].append({"log": log, "count": count, "is_simulated": is_simulated})
        elif "type" in item:
            type = item["type"]
            count = item["numberOfRelations"]
            is_simulated = item["is_simulated"]
            item_list["relationships"].append({"type": type, "count": count, "is_simulated": is_simulated})
            item_list["edgeCount"] += count

    return jsonify(item_list)


@db_manager_routes.route('/logs', methods=['GET'])
@db_exception_handler
def get_logs_route():
    dao_db_manager = DBManagement(current_app.connection)
    result = dao_db_manager.get_imported_logs()

    return jsonify(result[0])


@db_manager_routes.route('/eventlog/<entity_type>', methods=['GET'])
@db_exception_handler
def get_event_logs_route(entity_type):
    # TODO add timestamps constraints
    event_log = get_event_log(current_app.connection, entity_type)
    if event_log is None:
        event_log = []

    return jsonify(event_log)


@db_manager_routes.route('/get_model_ids', methods=['GET'])
@db_exception_handler
def get_model_ids():
    # TODO add timestamps constraints
    model_ids = pizza_get_model_ids(current_app.connection)
    if model_ids is None:
        model_ids = []

    return jsonify(model_ids)
