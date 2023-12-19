from ecdf_library import *
from get_dfs_from_pizza_db import *
from get_and_plot_ecdfs_from_pizza_db import *
import pickle
import codecs
import gzip

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "12341234"))

class Store_in_db:
    def __init__(self, perfobject, name, kind):
        self.__name=name
        self.__perfobject=perfobject
        self.__kind=kind
        
    def store(self,db_used):
        step0=self.__perfobject
        step1=pickle.dumps(step0)
        step2=gzip.compress(step1)
        step3=codecs.encode(step2, "base64").decode()
        id=runQueryMultipleSingleValue(driver,
                f'''create(n1:{self.__kind}:Performance{{name:"{self.__name}",val:"{step3}"}})
                    with n1
                    match(n2:Main{self.__kind})
                    CREATE(n2)-[:HAS_PERFORMANCE]->(n1)
                    RETURN id(n1)''',db_used)
        return id[0]

    def retrieve(name:str,db_used):
        ret=runQueryMultipleSingleValue(driver,f'''match(n:Performance{{name:"{name}"}}) return n.val''',db_used)
        step0=ret[0]
        step1=codecs.decode(step0.encode(), "base64")
        step2=gzip.decompress(step1)
        step3=pickle.loads(step2)
        return step3
    
    def retrieve_names(kind,db_used):
        return runQueryMultipleSingleValue(driver,f'''match(n:{kind}:Performance) return n.name''',db_used)

# creates two ecdf collections, adds them to the db, retrieves them from the db, displays them on the screen
def experiment1():
    test=Ecdf([1,2,3,4,5,6])
    ecdfc=Ecdf_collection([test],"1 to 6")
    ecdfcindb=Store_in_db(ecdfc,"Freek5","Latency","d11")
    ecdfcindb.store()

    ret_ecdfc=Store_in_db.retrieve("Freek5","d11")
    Ecdf_visualize.plot_to_screen(ret_ecdfc)

    e=experiment0_time_of_pizza_in_system()[2]
    edb=Store_in_db(e,"Freek31","Latency","d11")
    edb.store()

    ret_ecdfc=Store_in_db.retrieve("Freek31","d11")
    Ecdf_visualize.plot_to_screen(ret_ecdfc)

    print("")

# retrieves all the latency plots from the DB and displays them on the screen
def experiment2():
    for name in Store_in_db.retrieve_names("Latency","d11"):
        ecdfc=Store_in_db.retrieve(name)
        Ecdf_visualize.plot_to_screen(ecdfc)

#experiment1()
#experiment2()