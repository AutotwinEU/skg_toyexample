from promg import DatabaseConnection
from custom_module.cypher_queries.performance_queries import PerformanceQueryLibrary as pfql
from custom_module.modules.ecdf_library import *
import pickle
import codecs
import gzip
from promg import authentication


class Store_in_db:
    def __init__(self, db_connection, perfobject, name, kind):
        self.__name= name
        self.__perfobject= perfobject
        self.__kind= kind
        self.connection = db_connection
        
    def store(self):
        step0=self.__perfobject
        step1=pickle.dumps(step0)
        step2=gzip.compress(step1)
        step3=codecs.encode(step2, "base64").decode()
        id=self.connection.exec_query(pfql.store_in_db, **{"kind": self.__kind, "name": self.__name, "value": step3})
        return id

    @staticmethod
    def retrieve(connection,name):
        ret=connection.exec_query(pfql.retrieve_from_db, **{"name": name})
        step0=ret[0]["value"]
        step1=codecs.decode(step0.encode(), "base64")
        step2=gzip.decompress(step1)
        step3=pickle.loads(step2)
        return step3

    @staticmethod
    def retrieve_names(connection,kind):
        return connection.exec_query(pfql.retrieve_performance_artifacts_from_db, **{"kind": kind})
