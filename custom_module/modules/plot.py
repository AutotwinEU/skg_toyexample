from matplotlib import pyplot
import time

class Plot:
    def __init__(self,xs,ys,title,sensors):
        self.__xs=xs
        self.__ys=ys
        self.__title=title
        self.__sensors=sensors

    # check if all the values of the plot are positive. if not the plot will be discarded later
    def all_positive_values(self):
        for value in self.__ys:
            if value<0:
                return False
        return True
    
    def get_xs(self):
        return self.__xs

    def get_ys(self):
        return self.__ys

    def return_title(self):
        return self.__title
    
    def return_sensors(self):
        return self.__sensors
    
    def to_file(self, filename):
        pyplot.clf()
        pyplot.plot(self.__xs,self.__ys)
        pyplot.title(self.__title)
        pyplot.savefig(filename, dpi=200, format="svg")

    def to_screen(self):
        time.sleep(1)
        pyplot.clf()
        pyplot.plot(self.__xs,self.__ys)
        pyplot.title(self.__title)
        pyplot.show()