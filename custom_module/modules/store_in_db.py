from promg import DatabaseConnection
from custom_module.cypher_queries.performance_queries import PerformanceQueryLibrary as pfql
from custom_module.modules.ecdf_library import *
import pickle
import codecs
import gzip


class Store_in_db:
    def __init__(self, perfobject, name, kind):
        self.__name= name
        self.__perfobject= perfobject
        self.__kind= kind
        self.connection = DatabaseConnection()
        
    def store(self):
        step0=self.__perfobject
        step1=pickle.dumps(step0)
        step2=gzip.compress(step1)
        step3=codecs.encode(step2, "base64").decode()
        id=self.connection.exec_query(pfql.store_in_db, **{"kind": self.__kind, "name": self.__name, "value": step3})
        return id

    def retrieve(self, name):
        ret=self.connection.exec_query(pfql.retrieve_from_db, **{"name": name})
        step0=ret[0]
        step1=codecs.decode(step0.encode(), "base64")
        step2=gzip.decompress(step1)
        step3=pickle.loads(step2)
        return step3
    
    def retrieve_names(self, kind):
        return self.connection.exec_query(pfql.retrieve_performance_artifacts_from_db, **{"kind": kind})