from flask import make_response
from neo4j.exceptions import ServiceUnavailable


def db_exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except ServiceUnavailable:
            return make_response(
                'No connection to the Neo4j database could be made because the service is unavailable. \n'
                'Check whether the database is up and running!',
                503
            )
        else:
            return result

    # Renaming the function name:
    wrapper.__name__ = func.__name__
    return wrapper
