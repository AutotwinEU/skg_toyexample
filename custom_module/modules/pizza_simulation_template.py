import itertools as it
from pizza_simulation import create_simulated_data
import shutil
from promg import DatabaseConnection
from promg import authentication
from evaluate_one_scenario import evaluate_one_scenario
from custom_module.cypher_queries.db_management_queries import DBManagementQueries as dbmq
from pathlib import Path

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

def design_space_small_to_test():
    return list(list(it.product([1],[0.8,1.2],[0.8,1.2],[1],[1],[1],[1],[1],[1])))


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

def d_instance_to_name(d_instance):
    return "xxx"+'xxx'.join(map(str,d_instance)).replace(".","yyy")

def delete_all_dbs_expect_for_neo4j_and_system(d_space):
    credentials = authentication.connections_map[authentication.Connections.LOCAL]
    db_connection = DatabaseConnection.set_up_connection(credentials=credentials, verbose=False)
    for db in db_connection.exec_query(dbmq.return_db_list):
        if db["name"]!="system" and db["name"]!="neo4j":
            db_connection.exec_query(dbmq.drop_db, **{"dbname": db["name"]})

def create_db_per_d_instance(d_space):
    credentials = authentication.connections_map[authentication.Connections.LOCAL]
    db_connection = DatabaseConnection.set_up_connection(credentials=credentials, verbose=False)
    for d_instance in d_space:
        db_connection.exec_query(dbmq.create_db, **{"dbname": d_instance_to_name(d_instance)})

def write_design_instances_to_output_dir(d_space):
    d_instances_dir = "Q:/PizzaLineComplete_V3.7_2023_11_17/design_instances"
    simulator_dir = "Q:/PizzaLineComplete_V3.7_2023_11_17" # the TTS simulator directory
    data_dir = "R:/git/data/ToyExampleV3" # the target directory of the simulation results and starting point of building the SKG
    production_plan_and_stations_dir = "R:/git/data/ToyExampleV3.ava" # a directory with production_plan.csv and stations.csv
    headers_dir = "R:/git/data/ToyExampleV3.ava" # a processed data directory to "steal" the headers from
    config_filename=""

    delete_all_dbs_expect_for_neo4j_and_system(d_space)
    create_db_per_d_instance(d_space)

    for d_instance in d_space:
        # write pizza config
        filename=d_instance_to_name(d_instance)
        path=d_instances_dir+"/"+filename+".ini"
        f = open(path,"w")
        f.write(pizza_config(d_instance))
        f.close()

        # perform simulation
        create_simulated_data(simulator_dir,path,data_dir,production_plan_and_stations_dir,headers_dir)

        # create SKG + performance
        semantic_header_path = Path(f'R:/git/json_files/ToyExamplev3.json')
        ds_path = Path(f'R:/git/json_files/ToyExamplev3_DS.json')
        html_output_dir = "d:/temp2"  # a website with performance results will be written to this path
        evaluate_one_scenario(filename, semantic_header_path, ds_path, html_output_dir, simulator_dir, config_filename,
                              data_dir, production_plan_and_stations_dir, headers_dir)



dspace=design_space_small_to_test()
#dspace=design_space_different_on_one_dimension()
write_design_instances_to_output_dir(dspace)
