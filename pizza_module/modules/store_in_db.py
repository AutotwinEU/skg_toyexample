from promg import DatabaseConnection
from pizza_module.modules.ecdf_library import *
from pizza_module.cypher_queries.performance_queries import PerformanceQueryLibrary as pfql
import pickle
import codecs
import gzip
from promg import authentication


class Store_in_db:
    def __init__(self, db_connection, perfobject, name, kind, gt_sim="unknown"):
        self.__name= name
        self.__perfobject= perfobject
        self.__kind= kind
        self.connection = db_connection
        self.gt_sim= gt_sim
        
    def store(self):
        step0=self.__perfobject
        step1=pickle.dumps(step0)
        step2=gzip.compress(step1)
        step3=codecs.encode(step2, "base64").decode()
        id=self.connection.exec_query(pfql.store_in_db, **{"kind": self.__kind, "name": self.__name, "value": step3, "gt_sim": self.gt_sim})
        return id

    @staticmethod
    def retrieve(connection,name,gt_sim=None):
        ret=""
        if gt_sim==None:
            ret=connection.exec_query(pfql.retrieve_from_db_all, **{"name": name})
        else:
            ret=connection.exec_query(pfql.retrieve_from_db, **{"name": name, "gt_sim": gt_sim})
        step0=ret[0]["value"]
        step1=codecs.decode(step0.encode(), "base64")
        step2=gzip.decompress(step1)
        step3=pickle.loads(step2)
        return step3

    @staticmethod
    def retrieve_names(connection,kind):
        return connection.exec_query(pfql.retrieve_performance_artifacts_from_db, **{"kind": kind})
