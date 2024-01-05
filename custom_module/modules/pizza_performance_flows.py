from promg import DatabaseConnection
from custom_module.cypher_queries.performance_queries import PerformanceQueryLibrary as pfql

class Graph:
    def __init__(self,dot):
        self.__dot = dot

    def return_dot(self,dot):
        return self.__dot

class PizzaPerformanceModuleFlows:
    def __init__(self,working_dir):
        self.connection = DatabaseConnection()
        self.__working_dir = working_dir
        self.__traces = self.connection.exec_query(pfql.all_sensor_pizza_combinations)

    def return_flows(self):
        return [self.ecdf_flow_graph(self.__working_dir)]+[self.frequency_graph()]

    def return_dictedges(self):
        traces = self.__traces
        dictedges = {}

        for counter in range(0, len(traces) - 1):
            if traces[counter]["trace"]["pizzaId"] == traces[counter + 1]["trace"]["pizzaId"]:
                activity1 = traces[counter]["trace"]["activity"]
                activity2 = traces[counter + 1]["trace"]["activity"]
                if (activity1, activity2) not in dictedges.keys():
                    dictedges[(activity1, activity2)] = 1
                else:
                    dictedges[(activity1, activity2)] += 1

        return dictedges

    def return_dictnodes(self):
        dictnodes = {}
        dictionarynodecounter = 0

        for trace in self.__traces:
            key = trace["trace"]["activity"]
            if key not in dictnodes:
                dictnodes[key] = dictionarynodecounter
                dictionarynodecounter += 1

        return dictnodes

    def frequency_graph(self) -> str:
        dictnodes=self.return_dictnodes()
        dictedges=self.return_dictedges()
        ret="digraph {"

        for (fromedge,toedge) in dictedges:
            fe=dictnodes[fromedge]
            te=dictnodes[toedge]
            ret+=("d"+str(fe)+"->"+"d"+str(te)+"[label=\""+str(dictedges[(fromedge,toedge)])+"\"];")
        for x in dictnodes:
            ret+=("d"+str(dictnodes[x])+"[label=\""+x+"\"];")

        ret+=("}")
        return Graph(ret)

    def ecdf_flow_graph(self,working_dir) -> str:
        dictnodes=self.return_dictnodes()
        dictedges=self.return_dictedges()
        ret = "digraph {"

        for (fromedge,toedge) in dictedges:
            fe=dictnodes[fromedge]
            te=dictnodes[toedge]
            ret+=("d"+str(fe)+"->"+fromedge+"_"+toedge+";")
            ret+=(fromedge+"_"+toedge+"->d"+str(te)+"[label=\""+str(dictedges[(fromedge,toedge)])+"\"];")
            ret+=(fromedge+"_"+toedge+"[image=\""+working_dir+"/"+fromedge+" "+toedge+".svg\", label=\"\", shape=box]")
        for x in dictnodes:
            ret+=("d"+str(dictnodes[x])+"[label=\""+x+"\", shape=box];")

        ret+=("}")
        return Graph(ret)