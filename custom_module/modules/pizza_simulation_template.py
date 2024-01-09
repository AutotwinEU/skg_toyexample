import itertools as it
from pizza_simulation import create_simulated_data

# the complete design space.
# mostly for illustration, viz., contains 3^9=19683 design instances.
def design_space_all():
    return list(list(it.product([1,2,3],[0.8,1,1.2],[0.8,1,1.2],[0.8,1,1.2],[0.8,1,1.2],[0.8,1,1.2],[0.8,1,1.2],[0.8,1,1.2],[0.8,1,1.2])))

# the design space in which only changes in one dimension are taken into account.
# contains 8*2+4=20 design instances.
def design_space_different_on_one_dimension():
    return list(list(list(it.product([1,2,4,8],[1],[1],[1],[1],[1],[1],[1],[1]))+
                list(it.product([1],[0.8,1.2],[1],[1],[1],[1],[1],[1],[1]))+
                list(it.product([1],[1],[0.8,1.2],[1],[1],[1],[1],[1],[1]))+
                list(it.product([1],[1],[1],[0.8,1.2],[1],[1],[1],[1],[1]))+
                list(it.product([1],[1],[1],[1],[0.8,1.2],[1],[1],[1],[1]))+
                list(it.product([1],[1],[1],[1],[1],[0.8,1.2],[1],[1],[1]))+
                list(it.product([1],[1],[1],[1],[1],[1],[0.8,1.2],[1],[1]))+
                list(it.product([1],[1],[1],[1],[1],[1],[1],[0.8,1.2],[1]))+
                list(it.product([1],[1],[1],[1],[1],[1],[1],[1],[0.8,1.2]))))

# creates a template for the TTS simulator based on a design instance
# processing time (pt): pt=1 default, pt=2 twice as slow, pt=0.5 twice as fast
# breakdowns (bd)     : pt=1 default, pt=2 twice as often and as long breakdowns, pt=0.5 half as often and half as long breakdowns
def pizza_config(d_instance):
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

def write_design_instances_to_output_dir(d_space):
    d_instances_dir = "Q:/PizzaLineComplete_V3.7_2023_11_17/design_instances"
    simulator_dir = "Q:/PizzaLineComplete_V3.7_2023_11_17" # the TTS simulator directory
    #data_dir = "R:/git/data/ToyExampleV3" # the target directory of the simulation results and starting point of building the SKG
    production_plan_and_stations_dir = "R:/git/data/ToyExampleV3.ava" # a directory with production_plan.csv and stations.csv
    headers_dir = "R:/git/data/ToyExampleV3.ava" # a processed data directory to "steal" the headers from

    for d_instance in d_space:
        filename='_'.join(map(str,d_instance))
        path=d_instances_dir+"/"+filename+".ini"
        data_dir=d_instances_dir+"/"+filename
        f = open(path,"w")
        f.write(pizza_config(d_instance))
        f.close()
        create_simulated_data(simulator_dir,path,data_dir,production_plan_and_stations_dir,headers_dir)



dspace=design_space_different_on_one_dimension()
write_design_instances_to_output_dir(dspace)