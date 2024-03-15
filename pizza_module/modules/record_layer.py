from typing import Optional, List

import pandas as pd

from promg import DatabaseConnection
from promg import Performance
from promg.data_managers.semantic_header import ConstructedNodes

from pizza_module.cypher_queries.custom_query_library import CustomCypherQueryLibrary as ccql


class RecordLayerModule:
    def __init__(self, db_connection):
        self.connection = db_connection

    @Performance.track()
    def delete_record_layer(self):
        self.connection.exec_query(ccql.delete_record_layer)

