from promg import DatabaseConnection
from custom_module.cypher_queries.performance_queries import PerformanceQueryLibrary as pfql
import pydot

class Graph:
    def __init__(self, dot, title):
        self.__dot = dot
        self.__title = title

    def return_title(self):
        return self.__title

    def return_dot(self):
        return self.__dot

    def to_file(self,filename):
        pydot.graph_from_dot_data(self.__dot)[0].write_svg(filename)

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
            trace1 = traces[counter]["trace"]
            trace2 = traces[counter+1]["trace"]
            if trace1["pizzaId"] == trace2["pizzaId"]:
                activity1 = trace1["activity"]
                activity2 = trace2["activity"]
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
        return Graph(ret,"flow frequency")

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
        return Graph(ret, "flow ecdf")