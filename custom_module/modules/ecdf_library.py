from matplotlib import pyplot
import random
import numpy as np
from functools import reduce
import pickle
import time


# an Ecdf represented by a set of values and a legend
class Ecdf:
    def __init__(self, vals:[int], legend="", sensors=[]):
        self.__values=sorted(vals)
        self.__legend=legend
        self.__sensors=sensors

    # draws a random value from the list and therefore adheres to the distribution.
    def draw_random_sample(self):
        index=random.randint(0,len(self.__values)-1)
        return self.__values[index]
        
    # return a value (between 0 and 1); the probability that the value is smaller than the input value
    def result(self,inputvalue:float):
        count=0
        for v in self.__values:
            if inputvalue<v:
                return count/self.num_values()
            count=count+1
        return 1
    
    # returns an inverse value based on a certain probability, e.g., 0.5 yields the median value.
    def inverse_result(self,probability:float):
        for value in self.__values:
            if probability<=self.result(value):
                return value

    # prints the values of the eCDF textually
    def print(self):
        for v in self.__values:
            print(str(v)+" ",end="")
        print("")

    # returns the value of the eCDF
    def values(self):
        return self.__values
    
    # returns the number of values of the eCDF
    def num_values(self):
        return len(self.__values)

    # returns the minimum value of the eCDF
    def min_value(self):
        return self.__values[0]
    
    # returns the median value of the eCDF
    def median_value(self):
        return self.__values[len(self.__values)/2]
    
    # returns the average value of the eCDF
    def avg_value(self):
        sum=0
        for v in self.__values:
            sum=sum+v
        return v/len(self.__values)

    # returns the maximum value of the eCDF
    def max_value(self):
        return self.__values[-1]
    
    # returns the legend of the eCDF
    def legend(self):
        return self.__legend

    # returns the associated sensors of an Ecdf
    def sensors(self):
        return self.__sensors


# a collection of Ecdf_s plus a title, e.g., for plotting on the screen or write as image to file
class Ecdf_collection:
    def __init__(self, ecdfs:[Ecdf], title=""):
        self.__ecdfs=ecdfs
        self.__title=title
    
    def return_ecdfs(self):
        return self.__ecdfs

    def return_title(self):
        return self.__title
    
    def serialize(self):
        return pickle.dumps(self)
    
    def deserialize(str):
        return pickle.loads(str)
    

class Ecd_transform:
    # returns only the values n for which: valuefrom < ecdf(n) < valueto
    def values_subset(ecdf:Ecdf, valuefrom:float, valueto:float) -> Ecdf:
        num_vals=ecdf.num_values()
        return Ecdf(ecdf.values()[int(num_vals*valuefrom):int(num_vals*valueto)])

    # smears out the values using a window of a certain size
    # warning: often leads to new values that have not been observed
    def smear_values(ecdf:Ecdf, windowsize:int) -> Ecdf:
        ret_vals=[]
        num_vals=ecdf.num_values()
        
        for w in range(0,num_vals-windowsize+1):
            subset=ecdf.values()[w:w+windowsize]
            average=sum(subset)/windowsize
            ret_vals=ret_vals+[average]

        return Ecdf(ret_vals)
     
    # only keep every other "skipratio" values in an ecdf
    def skip_values(ecdf:Ecdf,skipratio:int) -> Ecdf:
        values=[]
        for n in range(0,ecdf.num_values(),skipratio):
            values=values+[ecdf.values()[n]]
        return Ecdf(values)

    # combines the values of different ecdfs in a new ecdf
    def combine_ecdfs(ecdfs:[Ecdf], legend="") -> Ecdf:
        values=[]
        for ecdf in ecdfs:
            values=values+ecdf.values()
        return Ecdf(values,legend)

    # returns the values n for which: valuefrom < ecdf(n) < valueto, and skips values outside this range using "skipratio"
    def skip_values_in_outliers(ecdf:Ecdf, valuefrom:float, valueto:float, skipratio:int, legend="") -> Ecdf:
        bottom_ecdf=Ecd_transform.skip_values(Ecd_transform.values_subset(ecdf,0,valuefrom),skipratio)
        middle_edf=Ecd_transform.values_subset(ecdf,valuefrom,valueto)
        top_ecdf=Ecd_transform.skip_values(Ecd_transform.values_subset(ecdf,valueto,ecdf.num_values()),skipratio)
        return Ecd_transform.combine_ecdfs([bottom_ecdf,middle_edf,top_ecdf],legend)

    # returns the values n for which: valuefrom < ecdf(n) < valueto, and smears out the values using a window of a certain size outside this range
    def smear_values_in_outliers(ecdf:Ecdf, valuefrom:float, valueto:float, windowsize:int, legend="") -> Ecdf:
        bottom_ecdf=Ecd_transform.smear_values(Ecd_transform.values_subset(ecdf,0,valuefrom),windowsize)
        middle_edf=Ecd_transform.values_subset(ecdf,valuefrom,valueto)
        top_ecdf=Ecd_transform.smear_values(Ecd_transform.values_subset(ecdf,valueto,ecdf.num_values()),windowsize)
        return Ecd_transform.combine_ecdfs([bottom_ecdf,middle_edf,top_ecdf],legend)


class Ecdf_simplify:
    def search_for_simple_ecdf_skip(ecdf:Ecdf):
        ret=[]
        for valuefrom in np.arange(0.0,0.21,0.02):
            for valueto in np.arange (0.0,0.21,0.02):
                for skipratio in range (1,10):
                    ecdf2=Ecd_transform.skip_values_in_outliers(ecdf,valuefrom,valueto,skipratio)
                    difference=Ecdf_compute.difference(ecdf,ecdf2)
                    ret.append((valuefrom,valueto,skipratio,ecdf,ecdf2,difference))
                    print(valuefrom,valueto,skipratio,round(difference,2),ecdf2.num_values())
        return ret
    
    def search_for_simple_ecdf_smear(ecdf:Ecdf):
        ret=[]
        for valuefrom in np.arange(0.0,0.21,0.02):
            for valueto in np.arange (0.0,0.21,0.02):
                for windowsize in range (1,10):
                    ecdf2=Ecd_transform.smear_values_in_outliers(ecdf,valuefrom,valueto,windowsize)
                    difference=Ecdf_compute.difference(ecdf,ecdf2)
                    ret.append((valuefrom,valueto,windowsize,ecdf,ecdf2,difference))
                    print(valuefrom,valueto,windowsize,round(difference,2),ecdf2.num_values())
        return ret


class Ecdf_compute:
    # returns the difference between two eCDFs by comparing the surface between the graphs
    def difference(ecdf1:Ecdf, ecdf2:Ecdf):
        values=sorted(ecdf1.values()+ecdf2.values())
        previous_value=0
        area=0
        for value in values:
            delta_x=value-previous_value
            ecdf1res=ecdf1.result(previous_value)
            ecdf2res=ecdf2.result(previous_value)
            delta_y=abs(ecdf1res-ecdf2res)
            area=area+(delta_x*delta_y)
            previous_value=value
        return area

    # returns the similarity between two eCDFs based on the surface difference
    def similarity(ecdf1:Ecdf, ecdf2:Ecdf):
        diff=Ecdf_compute.difference(ecdf1,ecdf2)
        if ecdf1.num_values()==0 or ecdf2.num_values()==0:
            return 1
        maximum=max(ecdf1.max_value(),ecdf2.max_value())
        return 1-(diff/maximum)
    
    # compares two eCDFs for performance based on their ratio for a certain probability
    # -1 means the second eCDF performs superior
    # 0 means they perform equally
    # 1 means the first eCDFs performs superior
    def performance_ratio(ecdf1:Ecdf, ecdf2:Ecdf, probability=0.5):
        res1 = ecdf1.inverse_result(probability)
        res2 = ecdf2.inverse_result(probability)
        if (res1==0 and res2==0) or (res1==res2):
            return 0
        elif res1==0:
            return 1
        elif res2==0:
            return -1
        elif res1<res2:
            return 1-(res1/res2)
        else:
            return -Ecdf_compute.performance_ratio(ecdf2,ecdf1,probability)


    # the "true" distribution of throwing two dices an infinite amount of times
    def distr_two_dices () -> Ecdf:
        ret=[]
        for dice1 in range(1,7):
            for dice2 in range(1,7):
                ret=ret+[dice1+dice2]
        return Ecdf(ret,"Infinite two dices")

    # the distribution of throwing two dices a "num_throws" amount of times
    def emperical_two_dices (num_throws:int) -> Ecdf:
        ret=[]
        for count in range(1,num_throws+1):
            ret=ret+[random.randint(1,6)+random.randint(1,6)]
        return Ecdf(ret,str(num_throws)+" throws two dices")
    
    # a made up distribution
    def made_up_distribution (num_throws:int) -> Ecdf:
        ret=[]
        for count in range(1,num_throws+1):
            ret=ret+[Ecdf_compute.add_up_random_numbers(20,1,100)]
        return Ecdf(ret,"made up distribution")
    
    # a distribution with "howmany" of values between "min" and "max"
    def add_up_random_numbers(howmany,min,max):
        ret=0
        for n in range(howmany):
            ret=ret+random.randint(min,max)
        return ret


class Ecdfs_compute:
    # three functions that compare the average, minimum and maximum performance of two sets of eCDFs
    def avg_similarity (ecdfs1:[Ecdf],ecdfs2:[Ecdf]) -> float:
        sum=0
        for n in range(len(ecdfs1)):
            sum+=Ecdf_compute.similarity(ecdfs1[n],ecdfs2[n])
        return sum/len(ecdfs1)

    def min_similarity (ecdfs1:[Ecdf],ecdfs2:[Ecdf]) -> float:
        minimum=1
        for n in range(len(ecdfs1)):
            minimum=min(minimum,Ecdf_compute.similarity(ecdfs1[n],ecdfs2[n]))
        return minimum
    
    def max_similarity (ecdfs1:[Ecdf],ecdfs2:[Ecdf]) -> float:
        maximum=0
        for n in range(len(ecdfs1)):
            maximum=max(maximum,Ecdf_compute.similarity(ecdfs1[n],ecdfs2[n]))
        return maximum

    # functions that compare the performance of two sets of eCDFs
    # the probability corresponds with the inverse values of the eCDFS. Default=0.5 (median value)
    def avg_performance (ecdfs1:[Ecdf],ecdfs2:[Ecdf],probability=0.5) -> float:
        sum=0
        for n in range(len(ecdfs1)):
            sum+=Ecdf_compute.performance_ratio(ecdfs1[n],ecdfs2[n],probability)
        return sum/len(ecdfs1)

    def min_performance (ecdfs1:[Ecdf],ecdfs2:[Ecdf],probability=0.5) -> float:
        minimum=1
        for n in range(len(ecdfs1)):
            minimum=min(minimum,Ecdf_compute.performance_ratio(ecdfs1[n],ecdfs2[n],probability))
        return minimum

    def max_performance (ecdfs1:[Ecdf],ecdfs2:[Ecdf],probability=0.5) -> float:
        maximum=-1
        for n in range(len(ecdfs1)):
            maximum=max(maximum,Ecdf_compute.performance_ratio(ecdfs1[n],ecdfs2[n],probability))
        return maximum


class Ecdf_visualize:  
    def max_value(ecdfs:[Ecdf]):
        ret=0
        for ecdf in ecdfs:
            ret=max(ret,ecdf.max_value())
        return ret
    
    def plot(ecdfc:Ecdf_collection, max=9999999):
        pyplot.clf()
        legend=[]
        for ecdf in ecdfc.return_ecdfs():
            legend.append(ecdf.legend())
            xPoints=[]
            yPoints=[]
            previous_x=0
            for x in ecdf.values():
                if x<max:
                    xPoints.append(previous_x)
                    yPoints.append(ecdf.result(previous_x))
                    xPoints.append(x)
                    yPoints.append(ecdf.result(previous_x))
                    previous_x=x
            xPoints.append(previous_x)
            yPoints.append(1)
            pyplot.plot(xPoints, yPoints)
        pyplot.legend(legend, loc ="lower right", fontsize="6")
        pyplot.title(ecdfc.return_title())
        return pyplot

    def plot_to_screen(ecdfc:Ecdf_collection,max=9999999):
        time.sleep(1)
        pp=Ecdf_visualize.plot(ecdfc,max)
        pp.show()

    def plot_to_file(filename,ecdfc:Ecdf_collection,dpi=200,format="png",max=9999999):
        pp=Ecdf_visualize.plot(ecdfc,max)
        pp.ioff()
        pp.savefig(filename+"."+format, dpi=dpi, format=format)

    def plot_histogram(ecdf:Ecdf,num_bins:int, title=""):
        pyplot.title(title)
        pyplot.hist(ecdf.values(),num_bins)
        pyplot.show()



#######################################################
#                                                     #
# Plots three Ecdfs based on a large number of values #
# of which two plots are modified for outliers.       #
# Also plots a histogram of one of the Ecdfs.         #
#                                                     #
#######################################################
def experiment1():
    test=Ecdf([1,4,7,10,100,105,108,111,112,114,115,116,117,130,135,136,138,140,160,180,200,205,210,300,350,400,600,800,1000,2000,5000,8000,10000,20000,40000],"Original")
    test.print()
    print(Ecdf_compute.similarity(test,test))
    test2=Ecd_transform.skip_values_in_outliers(test,0.0,0.6,3,"Skipping")
    test2.print()
    print(Ecdf_compute.similarity(test,test2))
    test3=Ecd_transform.smear_values_in_outliers(test,0.0,0.6,4,"Smearing")
    test3.print()
    print(Ecdf_compute.similarity(test,test3))

    Ecdf_visualize.plot_to_screen(Ecdf_collection([test,test2,test3],"The result of dealing with outliers"),500)
    Ecdf_visualize.plot_histogram(test,10,"Histogram of first Ecdf")


#######################################################
#                                                     #
# Plots Ecdfs in which two random dices are thrown    #
# a number of times. The more often dices are thrown, #
# the closer the Ecdf looks like the "true" one.      #
#                                                     #
#######################################################
def experiment2():
    ecdfs=[]
    eninf=Ecdf_compute.distr_two_dices()
    ecdfs.append(eninf)
    for num_dices in [1,10,100,1000]:
        print("*** num dices: "+str(num_dices))
        en=Ecdf_compute.emperical_two_dices(num_dices)
        ecdfs.append(en)
        en.print()
        print("* difference: "+str(Ecdf_compute.difference(eninf,en)))
        print("* similarity: "+str(Ecdf_compute.similarity(eninf,en)))
    Ecdf_visualize.plot_to_screen(Ecdf_collection(ecdfs,"Throwing two dices multiple times"))

def experiment3():
    test=Ecdf_compute.made_up_distribution(200)
    
    #Ecdf_simplify.search_for_simple_ecdf_skip(test)
    #Ecdf_simplify.search_for_simple_ecdf_smear(test)

    test.print()

def experiment4():
    test=Ecdf([1,2,3,4,5,6,6,6,6,6])
    for n in range(20):
        print(test.draw_random_sample(),end=" ")
    print("")

def experiment5():
    test=Ecdf([1,2,3,4,5,6])
    Ecdf_visualize.plot_to_screen(Ecdf_collection([test],"1 to 6"))
    Ecdf_visualize.plot_to_file("p:/test.png",[test])

def experiment6_inverse_result():
    test=Ecdf([1,2,3,4,5,6,140,200])
    print(test.inverse_result(0))
    print(test.inverse_result(0.1))
    print(test.inverse_result(0.2))
    print(test.inverse_result(0.3))
    print(test.inverse_result(0.4))
    print(test.inverse_result(0.5))
    print(test.inverse_result(0.6))
    print(test.inverse_result(0.7))
    print(test.inverse_result(0.8))
    print(test.inverse_result(0.9))
    print(test.inverse_result(1))

def experiment_7_test_performance_function():
    test1=Ecdf([2])
    test2=Ecdf([3])
    test3=Ecdf([0])
    print(Ecdf_compute.performance_ratio(test1,test2)) # 0.333
    print(Ecdf_compute.performance_ratio(test2,test1)) # -0.333
    print(Ecdf_compute.performance_ratio(test1,test3)) # -1
    print(Ecdf_compute.performance_ratio(test3,test1)) # 1
    print(Ecdf_compute.performance_ratio(test3,test3)) # 0
    print(Ecdf_compute.performance_ratio(test1,test1)) # 0

def experiment_8_serialize_and_deserialize():
    test=Ecdf([1,2,3,4,5,6])
    ecdfc=Ecdf_collection([test],"1 to 6")
    ser=ecdfc.serialize()
    Ecdf_visualize.plot_to_screen(Ecdf_collection.deserialize(ser))


#experiment1()
#experiment2()
#experiment3()
#experiment4()
#experiment5()
#experiment6_inverse_result()
#experiment_7_test_performance_function()
#experiment_8_serialize_and_deserialize()