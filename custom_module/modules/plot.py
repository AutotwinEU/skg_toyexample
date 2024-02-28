from matplotlib import pyplot
import time

class Plot:
    def __init__(self,xs,ys,title,sensors):
        self.__xs=xs
        self.__ys=ys
        if len(xs)==0:
            self.__xs.append(0)
            self.__ys.append(0)
        self.__title=title
        self.__sensors=sensors

    def get_max(self):
        return max(self.__ys)

    def get_min(self):
        return min(self.__ys)

    def get_average(self):
        area=0
        previous_x=0
        for index in range(len(self.__xs)):
            new_x=self.__xs[index]
            area+=(new_x-previous_x)*self.__ys[index]
            previous_x=new_x
        if previous_x>0:
            return area/previous_x
        else:
            return 0

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