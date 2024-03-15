import os

from flask import Blueprint, current_app, make_response, request, json

from api.exceptions.exception_handler import db_exception_handler
from performance_functionalities import evaluate_performance

# EV: Changed blueprint name to avoid name clash.
performance_routes = Blueprint("performance", __name__, url_prefix="/performance")


@performance_routes.route('/run', methods=['POST'])
@db_exception_handler
def evaluate_perf():
    # EV: Set both imports to false, data should already be loaded in database.
    evaluate_performance(False,False,False,True)

    return make_response(
        'Evaluated the performance!',
        200
    )
