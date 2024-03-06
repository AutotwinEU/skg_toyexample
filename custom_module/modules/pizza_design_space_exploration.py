import random
import sys
import itertools as it

from promg import DatabaseConnection
from promg.database_managers import authentication
from custom_module.cypher_queries.performance_queries import PerformanceQueryLibrary as pfql

# the complete design space, which contains 5^8=390625 design instances.
def design_space_all():
    dim_var = [0.15, 0.3, 0.45, 0.66, 1, 1.5, 2, 5, 10]
    return list(list(it.product([1], dim_var, dim_var, dim_var, dim_var, dim_var, dim_var, dim_var, dim_var)))

def design_space_refined():
    dim_var = [0.3, 0.45, 0.66, 1, 1.5, 2]
    return list(list(it.product([1], dim_var, dim_var, dim_var, dim_var, dim_var, dim_var, dim_var, dim_var)))

def starting_design_space():
    return list(list(it.product([1], [1], [1], [1], [1], [1], [1], [1], [1])))

# a small design space for testing
def design_space_small_dim1():
    dim_var = [0.15, 0.3, 0.45, 0.66, 1, 1.5, 2, 5, 9]
    return list(list(it.product([1], dim_var, [1], [1], [1], [1], [1], [1], [1])))

def design_space_small_dim2():
    dim_var = [0.15, 0.3, 0.45, 0.66, 1, 1.5, 2, 5, 9]
    return list(list(it.product([1], [1], dim_var, [1], [1], [1], [1], [1], [1])))

def design_space_small_dim3():
    dim_var = [0.15, 0.3, 0.45, 0.66, 1, 1.5, 2, 5, 9]
    return list(list(it.product([1], [1], [1], dim_var, [1], [1], [1], [1], [1])))

def design_space_small_dim4():
    dim_var = [0.15, 0.3, 0.45, 0.66, 1, 1.5, 2, 5, 9]
    return list(list(it.product([1], [1], [1], [1], dim_var, [1], [1], [1], [1])))

def design_space_small_dim5():
    dim_var = [0.15, 0.3, 0.45, 0.66, 1, 1.5, 2, 5, 9]
    return list(list(it.product([1], [1], [1], [1], [1], dim_var, [1], [1], [1])))

def design_space_small_dim6():
    dim_var = [0.15, 0.3, 0.45, 0.66, 1, 1.5, 2, 5, 9]
    return list(list(it.product([1], [1], [1], [1], [1], [1], dim_var, [1], [1])))

def design_space_small_dim7():
    dim_var = [0.15, 0.3, 0.45, 0.66, 1, 1.5, 2, 5, 9]
    return list(list(it.product([1], [1], [1], [1], [1], [1], [1], dim_var, [1])))

def design_space_small_dim8():
    dim_var = [0.15, 0.3, 0.45, 0.66, 1, 1.5, 2, 5, 9]
    return list(list(it.product([1], [1], [1], [1], [1], [1], [1], [1], dim_var)))

# creates a template for the TTS simulator based on a design instance
# processing time (pt): pt=1 default, pt=2 twice as slow, pt=0.5 twice as fast
# breakdowns (bd)     : pt=1 default, pt=2 twice as often and as long breakdowns, pt=0.5 half as often and half as long breakdowns
def simulator_config(d_instance):
    sim_length = (d_instance[0])
    fridge_bd = (d_instance[1])
    oven_bd = (d_instance[2])
    op_box_pt = (d_instance[3])
    op_box_bd = (d_instance[4])
    op_pack_pt = (d_instance[5])
    op_pack_bd = (d_instance[6])
    warehouse_pt = (d_instance[7])
    robot_bd = (d_instance[8])

    return f"""
    %config/boxer_max_output_queue=3
    %config/max_cooking_time=6000
    %config/packer_max_output_queue=7
    %config/plant_maxWIP=300
    %config/robot_max_out_of_refrigerator_time=80000
    %config/robot_mtbf=15/{robot_bd}
    %config/robot_mttr=2*{robot_bd}
    %config/warehouse_exit_request_time=uniReal({warehouse_pt}*10*60*1000,{warehouse_pt}*20*60*1000)
    %In1/prodPlanFileName=ProductionPlan0.csv
    %opBox/breakDuration=uniReal({op_box_bd}*3*60*1000,{op_box_bd}*4*60*1000)
    %opBox/breakEvery=uniReal(13*60*1000/{op_box_bd},15*60*1000/{op_box_bd})
    %opBox/fixedProcessingTime=uniReal({op_box_pt}*3200,{op_box_pt}*4500)
    %opBox/variableProcessingTime=uniReal({op_box_pt}*1000,{op_box_pt}*1400)
    %opPack/breakDuration=uniReal({op_pack_bd}*2*60*1000,{op_pack_bd}*3*60*1000)
    %opPack/breakEvery=uniReal(28*60*1000/{op_pack_bd},30*60*1000/{op_pack_bd})
    %opPack/fixedProcessingTime=uniReal({op_pack_pt}*2000,{op_pack_pt}*2200)
    %opPack/variableProcessingTime=uniReal({op_pack_pt}*500,{op_pack_pt}*1000)
    %OvenBreakdown/mtbfMin=15/{oven_bd}
    %OvenBreakdown/mttrMin=1*{oven_bd}
    %RefrigeratorBreakdown/mtbfMin=20/{fridge_bd}
    %RefrigeratorBreakdown/mttrMin=2*{fridge_bd}
    force.load.geometries=true
    loglevel=CONFIG
    paused=true
    simulationEndTime={sim_length}.0
    simulationEndTimeUnits=h
    ui=false
    """

def d_instance_to_database_name(d_instance):
    return "xx"+'xx'.join(map(str,d_instance)).replace(".","yyy")

def d_instancedbname_to_d_instance(d_instancedbname):
    xs=d_instancedbname.replace("yyy",".").split("xx")
    xs.pop(0)
    d=[]
    for x in xs:
        d.append(float(x))
    return tuple(d)

def d_instance_to_filename(d_instance):
    return ','.join(map(str, d_instance))

def d_instancefilename_to_d_instance(d_instancefilename):
    x=d_instancefilename.split("xx")
    x.pop(0)
    return tuple(x)

def best_performance_neighbour(d_instances,d_space):
    credentials = authentication.connections_map[authentication.Connections.LOCAL]
    dbconnection = DatabaseConnection.set_up_connection(credentials=credentials, verbose=False)
    max_average_performance = sys.float_info.max
    best_d_instance = ""
    for d_instance in d_instances:
        dbconnection.change_db(d_instance_to_database_name(d_instance))
        db_performance=dbconnection.exec_query(pfql.get_overall_performance_query)
        if db_performance[0]["average"]<max_average_performance:
            best_d_instance=d_instance
            max_average_performance=db_performance[0]["average"]
    potential_neighbours = [x for x in d_instances_neighbours([best_d_instance],d_space) if x not in d_instances]
    if not potential_neighbours:
        return None
    else:
        return random.choice(potential_neighbours)

def most_similar_neighbour(d_instance_goal,d_space_evaluated,d_space):
    credentials = authentication.connections_map[authentication.Connections.LOCAL]
    dbconnection = DatabaseConnection.set_up_connection(credentials=credentials, verbose=False)
    dbconnection.change_db("aggregated")
    most_similar=dbconnection.exec_query(pfql.get_similarity_of_designs, **{"goal_design": d_instance_to_database_name(d_instance_goal)})
    most_similar_d = d_instancedbname_to_d_instance(most_similar[0]["p1db"])
    potential_neighbours = [x for x in d_instances_neighbours([most_similar_d], d_space) if x not in d_space_evaluated]
    if not potential_neighbours:
        return None
    else:
        return random.choice(potential_neighbours)

def one_random_neighbour(d_instances,d_space):
    return random.choice(d_instances_neighbours(d_instances,d_space))

def random_instance(d_space):
    return random.choice(d_space)

def d_instances_neighbours(d_instances,d_space):
    neighbours = []
    for d_instance in d_instances:
        for d_instance_to_add in d_instance_neighbours(d_instance,d_space):
            if d_instance_to_add not in neighbours and d_instance_to_add not in d_instances:
                neighbours.append(d_instance_to_add)
    return neighbours

def d_instance_neighbours(d_instance,d_space):
    neighbours = []
    for d_neighbour in d_space:
        if is_neighbour(d_instance, d_neighbour, d_space):
            neighbours.append(d_neighbour)
    return neighbours

def is_neighbour(d_instance,d_neighbour,d_space):
    one_different_dimension=False
    for index in range(len(d_instance)):
        if d_instance[index] != d_neighbour[index] and one_different_dimension:
            return False
        if d_instance[index] != d_neighbour[index]:
            one_different_dimension=True
    for d_instance_inbetween in d_space:
        if is_d_instance_inbetween(d_instance,d_neighbour,d_instance_inbetween):
            return False
    return True

def is_d_instance_inbetween(d_instance,d_neighbour,d_instance_inbetween):
    for index in range(len(d_instance)):
        if d_instance[index]<d_instance_inbetween[index] and d_instance_inbetween[index]<d_neighbour[index]:
            return True
        if d_neighbour[index]<d_instance_inbetween[index] and d_instance_inbetween[index]<d_instance[index]:
            return True
    return False