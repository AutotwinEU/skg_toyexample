from custom_module.modules.pizza_performance_ecdfs import *
class Performance_website:
    def __init__(self, working_dir, ecdfcs, queues, flows, utils):
        self.__working_dir=working_dir
        self.__ecdfcs=ecdfcs
        self.__utils=utils
        self.__queues=queues
        self.__flows=flows

    def write_performance_objects_to_file(self):
        for count in range(0,len(self.__ecdfcs)):
            Ecdf_visualize.plot_to_file(self.__working_dir+"/"+self.__ecdfcs[count].return_title(),self.__ecdfcs[count],80,"svg")
            for ecdf in self.__ecdfcs[count].return_ecdfs():
                Ecdf_visualize.plot_to_file(self.__working_dir+"/"+ecdf.legend(),Ecdf_collection([ecdf],ecdf.legend()),80,"svg")
        for count in range(0,len(self.__utils)):
            continue
        for count in range(0,len(self.__queues)):
            self.__queues[count].to_file(self.__working_dir+"/q"+str(count)+".svg")
        for count in range(0,len(self.__flows)):
            self.__flows[count].to_file(self.__working_dir+"/f"+str(count)+".svg")

    def create(self):
        self.write_performance_objects_to_file()
        self.create_website_index()

    def create_website_index(self):
        f = open(self.__working_dir + "/index.html", "w")
        f.write("<html><a id=\"top\"><h2>Performance result</h2><ul>\n")
        self.print_toc_performance_objects(f)
        f.write("</ul>")
        self.print_performance_objects(f)
        f.write("</html>\n")
        f.close()

    def print_toc_performance_objects(self,f):
        for count in range(0,len(self.__ecdfcs)):
            f.write("<li><a href=\"#eCDF"+str(count)+"\">"+self.__ecdfcs[count].return_title()+"</a></li>\n")
        for count in range(0,len(self.__utils)):
            f.write("<li><a href=\"#uCDF"+str(count)+"\">"+self.__utils[count].return_title()+"</a></li>\n")
        for count in range(0,len(self.__queues)):
            f.write("<li><a href=\"#qCDF"+str(count)+"\">"+self.__queues[count].return_title()+"</a></li>\n")
        for count in range(0,len(self.__flows)):
            f.write("<li><a href=\"#fCDF"+str(count)+"\">"+self.__flows[count].return_title()+"</a></li>\n")

    def print_performance_objects(self,f):
        f.write("<h2>Ecdfcs</h2>\n")
        for count in range(0,len(self.__ecdfcs)):
            f.write("<h4>"+self.__ecdfcs[count].return_title()+"\n")
            f.write("<a id=\"eCDF"+str(count)+"\"></h4><img src=\""+self.__working_dir+"/"+self.__ecdfcs[count].return_title()+".svg\"><a href=\"#top\">back to top<a><br>\n")
        f.write("<h2>Utils</h2>\n")
        for count in range(0,len(self.__utils)):
            f.write("<h4>"+self.__utils[count].return_title()+"\n")
            f.write("<a id=\"uCDF"+str(count)+"\"></h4><img src="+self.__working_dir+"/u"+str(count)+".svg><a href=\"#top\">back to top<a><br>\n")
        f.write("<h2>Queues</h2>\n")
        for count in range(0,len(self.__queues)):
            f.write("<h4>"+self.__queues[count].return_title()+"\n")
            f.write("<a id=\"qCDF"+str(count)+"\"></h4><img src="+self.__working_dir+"/q"+str(count)+".svg><a href=\"#top\">back to top<a><br>\n")
        f.write("<h2>Flows</h2>\n")
        for count in range(0,len(self.__flows)):
            f.write("<h4>"+self.__flows[count].return_title()+"\n")
            f.write("<a id=\"fCDF"+str(count)+"\"></h4><img src="+self.__working_dir+"/f"+str(count)+".svg><a href=\"#top\">back to top<a><br>\n")
