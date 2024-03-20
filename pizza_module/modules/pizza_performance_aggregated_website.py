from promg import DatabaseConnection, Configuration

from pizza_module.modules.ecdf_library import Ecdf_visualize, Ecdf_collection
from pizza_module.modules.store_in_db import Store_in_db

from pizza_module.cypher_queries.performance_queries import PerformanceQueryLibrary as pfql

import os
import numpy as np

def retrieve_ecdfcs_from_skg(connection):
    ecdfcs = []
    for ecdfcname in Store_in_db.retrieve_names(connection, "Latency"):
        ecdfs = [Store_in_db.retrieve(connection, ecdf["ecdf"], None)
                 for ecdf in connection.exec_query(pfql.all_ecdfs_of_an_ecdfc_all,
                                                        **{"name": ecdfcname["names"]})]
        ecdfcs.append(Ecdf_collection(ecdfs, ecdfcname["names"]))
    return ecdfcs
def write_performance_objects_to_file(ecdfcs,working_dir):
    for count in range(0, len(ecdfcs)):
        Ecdf_visualize.plot_to_file(working_dir + "/" + ecdfcs[count].return_title(),
                                    ecdfcs[count], 80, "svg")

def create_index_file(ecdfcs,working_dir, connection):
    f=open(working_dir+"/index.html", "w")
    f.write("<h2>Ecdfcs</h2>\n")
    for count in range(0, len(ecdfcs)):
        f.write("<h4>" + ecdfcs[count].return_title() + "\n")
        f.write("<a id=\"eCDF" + str(count) + "\"></h4><img src=\"" + ecdfcs[
            count].return_title() + ".svg\"><a href=\"#top\">back to top<a><br>\n")
        print_ecdfc_conformance(ecdfcs[count],f, connection)
    f.close()

def print_ecdfs_aggregated_data(ecdfc,f,connection):
    f.write("<br>Aggregated values:<br>")
    f.write("<table border=1><tr><td><b>Design</b></td><td><b>Minimum</b></td><td><b>Maximum</b></td><td><b>Average</b></td><td><b>Median</b></td></tr>")
    ecdf=ecdfc.return_ecdfs()[0]
    min_max_average_median = connection.exec_query(pfql.get_ecdf_properties, **{"name": ecdf.legend()+" gt"})
    f.write("<tr><td><p style=color:red;>" + ecdf.legend()+ " sim</p></td>")
    f.write("<td>" + str(round(min_max_average_median[0]["min"],2)) + "</td>")
    f.write("<td>" + str(round(min_max_average_median[0]["max"],2)) + "</td>")
    f.write("<td>" + str(round(min_max_average_median[0]["average"],2)) + "</td>")
    f.write("<td>" + str(round(min_max_average_median[0]["median"],2)) + "</td><tr>")
    min_max_average_median = connection.exec_query(pfql.get_ecdf_properties, **{"name": ecdf.legend()+" sim"})
    f.write("<tr><td><p style=color:blue;>" + ecdf.legend()+ " gt</p></td>")
    f.write("<td>" + str(round(min_max_average_median[0]["min"],2)) + "</td>")
    f.write("<td>" + str(round(min_max_average_median[0]["max"],2)) + "</td>")
    f.write("<td>" + str(round(min_max_average_median[0]["average"],2)) + "</td>")
    f.write("<td>" + str(round(min_max_average_median[0]["median"],2)) + "</td><tr>")
    f.write("</table>")

def print_ecdfc_conformance(ecdfc:Ecdf_collection,f,connection):
    print_ecdfs_aggregated_data(ecdfc, f, connection)
    size=len(ecdfc.return_ecdfs())
    sim=np.zeros((size,size))
    diff=np.zeros((size,size))
    perf=np.zeros((size,size))
    kolm=np.zeros((size, size))
    for index1 in range(size):
        for index2 in range(size):
            ecdfleg=ecdfc.return_ecdfs()[index1].legend()
            add1=" sim"
            add2=" sim"
            if index1==1:
                add1=" gt"
            if index2==1:
                add2=" gt"
            sim_diff_perf=connection.exec_query(pfql.similarity_difference_and_performance,
                                  **{"ecdf_name1": ecdfleg+add1, "ecdf_name2": ecdfleg+add2})
            sim[index1,index2]=sim_diff_perf[0]["sim"]
            diff[index1,index2]=sim_diff_perf[0]["diff"]
            perf[index1,index2]=sim_diff_perf[0]["perf"]
            kolm[index1, index2] = sim_diff_perf[0]["kolm"]
    f.write("<br>Similarity:<br>")
    print_metric_table(sim, ecdfc, f)
    f.write("<br>Difference:<br>")
    print_metric_table(diff, ecdfc, f)
    #f.write("<br>Performance:<br>")
    #print_metric_table(perf, ecdfc, f)
    f.write("<br>Kolmogorov:<br>")
    print_metric_table(kolm, ecdfc, f)
    f.write("<br><br>")

def print_metric_table(data,ecdfc,f):
    size=len(ecdfc.return_ecdfs())
    f.write("<table border=1><tr><td></td>")
    for index in range(size):
        add1 = " gt"
        if index == 1:
            add1 = " sim"
        f.write("<td><b>"+ecdfc.return_ecdfs()[index].legend()+add1+"</b></td>")
    for index1 in range(size):
        add1 = " gt"
        if index1 == 1:
            add1 = " sim"
        f.write("</tr><tr><td><b>"+ecdfc.return_ecdfs()[index1].legend()+add1+"</b></td>")
        for index2 in range(size):
            f.write("<td>"+str(round(data[index1][index2],3))+"</td>")
        f.write("</tr>")
    f.write("</table>")

def create_aggregated_performance_html(config, working_dir):
    db_connection = DatabaseConnection.set_up_connection(config=config)
    ecdfcs=retrieve_ecdfcs_from_skg(db_connection)
    write_performance_objects_to_file(ecdfcs,working_dir)
    create_index_file(ecdfcs,working_dir,db_connection)
