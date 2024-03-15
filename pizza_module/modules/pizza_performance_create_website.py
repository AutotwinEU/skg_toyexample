from pizza_module.modules.pizza_performance_ecdfs import *
import os
import numpy as np

def d_instancedbname_to_printable_d_instance(d_instancedbname):
    return d_instancedbname.replace("yyy",".").replace("xx"," ")


class Performance_website:
    def __init__(self, dbconnection, working_dir, ecdfcs, queues, flows, utils, first_time):
        if not os.path.exists(working_dir):
            os.makedirs(working_dir)
        self.__working_dir = "./performance_results/"+working_dir
        self.__design_dir = working_dir+"/"
        self.__ecdfcs = ecdfcs
        self.__utils = utils
        self.__queues = queues
        self.__flows = flows
        self.dbconnection = dbconnection
        self.first_time = first_time

    def write_performance_objects_to_file(self):
        for count in range(0, len(self.__ecdfcs)):
            Ecdf_visualize.plot_to_file(self.__working_dir + "/" + self.__ecdfcs[count].return_title(),
                                        self.__ecdfcs[count], 80, "svg")
            for ecdf in self.__ecdfcs[count].return_ecdfs():
                Ecdf_visualize.plot_to_file(self.__working_dir + "/" + ecdf.legend(),
                                            Ecdf_collection([ecdf], ecdf.legend()), 80, "svg")

    def create(self):
        self.write_performance_objects_to_file()
        self.create_website_index()

    def create_website_index(self):
        f = open(self.__working_dir + "/index.html", "w")
        f.write("<a id=\"top\"><h2>Performance result</h2><ul>\n")
        self.print_toc_performance_objects(f)
        f.write("</ul>")
        self.print_performance_objects(f)
        f.close()

        if self.first_time:
            f = open(self.__working_dir + "/../index.html", "w")
            f.write("<html><table border=1><tr>")
            f.close()

        f = open(self.__working_dir + "/../index.html", "a")
        f.write("<td><a id=\"top\"><h2>Performance result</h2><ul>\n")
        self.print_toc_performance_objects(f)
        f.write("</ul>")
        self.print_performance_objects(f,self.__design_dir)
        f.write("</td>")
        f.close()

        if not self.first_time:
            f = open(self.__working_dir + "/../index.html", "a")
            f.write("</tr></table></html>")
            f.close()

    def print_toc_performance_objects(self, f):
        for count in range(0, len(self.__ecdfcs)):
            f.write("<li><a href=\"#eCDF" + str(count) + "\">" + self.__ecdfcs[count].return_title() + "</a></li>\n")
        for count in range(0, len(self.__utils)):
            f.write("<li><a href=\"#uCDF" + str(count) + "\">" + self.__utils[count].return_title() + "</a></li>\n")
        for count in range(0, len(self.__queues)):
            f.write("<li><a href=\"#qCDF" + str(count) + "\">" + self.__queues[count].return_title() + "</a></li>\n")
        for count in range(0, len(self.__flows)):
            f.write("<li><a href=\"#fCDF" + str(count) + "\">" + self.__flows[count].return_title() + "</a></li>\n")

    def print_performance_objects(self, f,design_dir="./"):
        self.print_ecdfcs(f,design_dir)
        self.print_utils(f)
        self.print_queues(f)
        self.print_flows(f)

    def print_ecdfcs(self,f,design_dir):
        f.write("<h2>Ecdfcs</h2>\n")
        for count in range(0, len(self.__ecdfcs)):
            f.write("<h4>" + self.__ecdfcs[count].return_title() + "\n")
            f.write("<a id=\"eCDF" + str(count) + "\"></h4><img src=\"" + design_dir+self.__ecdfcs[
                count].return_title() + ".svg\"><a href=\"#top\">back to top<a><br>\n")
            self.print_ecdfc_conformance(self.__ecdfcs[count],f)

    def print_ecdfc_conformance(self,ecdfc:Ecdf_collection,f):
        self.print_ecdfs_aggregated_data(ecdfc, f)
        connection = self.dbconnection
        size=len(ecdfc.return_ecdfs())
        sim=np.zeros((size,size))
        diff=np.zeros((size,size))
        perf=np.zeros((size,size))
        kolm=np.zeros((size, size))
        for index1 in range(size):
            for index2 in range(size):
                ecdf1=ecdfc.return_ecdfs()[index1]
                ecdf2=ecdfc.return_ecdfs()[index2]
                sim_diff_perf=connection.exec_query(pfql.similarity_difference_and_performance,
                                      **{"ecdf_name1": ecdf1.legend(), "ecdf_name2": ecdf2.legend()})
                if sim_diff_perf is None:
                    return
                sim[index1,index2]=sim_diff_perf[0]["sim"]
                diff[index1,index2]=sim_diff_perf[0]["diff"]
                perf[index1,index2]=sim_diff_perf[0]["perf"]
                kolm[index1, index2] = sim_diff_perf[0]["kolm"]
        f.write("<br>Similarity:<br>")
        self.print_metric_table(sim, ecdfc, f)
        f.write("<br>Difference:<br>")
        self.print_metric_table(diff, ecdfc, f)
        f.write("<br>Performance:<br>")
        self.print_metric_table(perf, ecdfc, f)
        f.write("<br>Kolmogorov:<br>")
        self.print_metric_table(kolm, ecdfc, f)

    def print_metric_table(self,data,ecdfc,f):
        size=len(ecdfc.return_ecdfs())
        f.write("<table border=1><tr><td></td>")
        for index in range(size):
            f.write("<td><b>"+d_instancedbname_to_printable_d_instance(ecdfc.return_ecdfs()[index].legend())+"</b></td>")
        for index1 in range(size):
            f.write("</tr><tr><td><b>"+d_instancedbname_to_printable_d_instance(ecdfc.return_ecdfs()[index1].legend())+"</b></td>")
            for index2 in range(size):
                f.write("<td>"+str(round(data[index1][index2],3))+"</td>")
            f.write("</tr")
        f.write("</table>")

    def print_ecdfs_aggregated_data(self,ecdfc,f):
        connection = self.dbconnection
        f.write("<br>Aggregated values:<br>")
        f.write("<table border=1><tr><td><b>Design</b></td><td><b>Minimum</b></td><td><b>Maximum</b></td><td><b>Average</b></td><td><b>Median</b></td></tr>")
        for ecdf in ecdfc.return_ecdfs():
            min_max_average_median = connection.exec_query(pfql.get_ecdf_properties, **{"name": ecdf.legend()})
            f.write("<tr><td><b>" + ecdf.legend()+ "</b></td>")
            f.write("<td>" + str(round(min_max_average_median[0]["min"],2)) + "</td>")
            f.write("<td>" + str(round(min_max_average_median[0]["max"],2)) + "</td>")
            f.write("<td>" + str(round(min_max_average_median[0]["average"],2)) + "</td>")
            f.write("<td>" + str(round(min_max_average_median[0]["median"],2)) + "</td><tr>")
        f.write("</table>")

    def print_utils(self,f):
        f.write("<h2>Utils</h2>\n")
        for count in range(0, len(self.__utils)):
            f.write("<h4>" + self.__utils[count].return_title() + "\n")
            f.write("<a id=\"uCDF" + str(count) + "\"></h4><img src=" + "/u" + str(
                count) + ".svg><a href=\"#top\">back to top<a><br>\n")

    def print_queues(self,f):
        f.write("<h2>Queues</h2>\n")
        for count in range(0, len(self.__queues)):
            f.write("<h4>" + self.__queues[count].return_title() + "\n")
            f.write("<a id=\"qCDF" + str(count) + "\"></h4><img src=" + "/q" + str(
                count) + ".svg><a href=\"#top\">back to top<a><br>\n")
            self.print_queues_aggregated_data(self.__queues[count].return_title(),f)

    def print_queues_aggregated_data(self,queue_name,f):
        connection = DatabaseConnection()
        min_max_average = connection.exec_query(pfql.get_queue_properties, **{"name": queue_name })
        f.write("<br>Aggregated values:<br>")
        f.write("<table border=1><tr><td><b>Minimum</b></td><td><b>Maximum</b></td><td><b>Average</b></td></tr>")
        f.write("<tr><td>" + str(round(min_max_average[0]["min"], 2)) + "</td>")
        f.write("<td>" + str(round(min_max_average[0]["max"], 2)) + "</td>")
        f.write("<td>" + str(round(min_max_average[0]["average"], 2)) + "</td></tr></table>")

    def print_flows(self,f):
        f.write("<h2>Flows</h2>\n")
        for count in range(0, len(self.__flows)):
            f.write("<h4>" + self.__flows[count].return_title() + "\n")
            f.write("<a id=\"fCDF" + str(count) + "\"></h4><img src=" + "/f" + str(
                count) + ".svg><a href=\"#top\">back to top<a><br>\n")
