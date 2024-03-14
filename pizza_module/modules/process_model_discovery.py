from promg import SemanticHeader
from promg.database_managers.db_connection import DatabaseConnection
from promg.utilities.performance_handling import Performance
from pizza_module.cypher_queries.process_model_discovery_query_library import AnalysisQueryLibrary as analysis_ql
from pizza_module.cypher_queries.custom_query_library import CustomCypherQueryLibrary as cql


class ProcessDiscovery:
    def __init__(self, database_connection):
        self.connection = database_connection

    def create_df_process_model(self, df_label, df_a_label):
        """
        Create a DF process model

        Args:
            df_label: The df label that should be tracked
            df_a_label: The df_label on activity level
        """
        self._create_df_process_model(df_label, df_a_label)

    @Performance.track("df_label")
    def _create_df_process_model(self, df_label, df_a_label):
        self.connection.exec_query(analysis_ql.get_aggregate_df_relations_query,
                                   **{
                                       "df_label": df_label,
                                       "df_a_label": df_a_label
                                   })

    # EV: Copied from v4.
    def get_model_ids(self):
        model_ids = self.connection.exec_query(cql.get_model_ids_query)
        return model_ids
