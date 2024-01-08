import os
from pathlib import Path
import shutil

def perform_simulation(simulator_dir, config_filename):
    os.chdir(simulator_dir)
    simulator_command = "jdk\\bin\\java.exe -Dsun.java2d.noddraw=true -Dsun.awt.noerasebackground=true -jar DDDSimulatorProject.jar -runargs " + config_filename
    os.system(simulator_command)
    paths = sorted(Path(simulator_dir).iterdir(), key=os.path.getmtime)
    return [f for f in paths if f.is_dir()][-1]  # the folder in which the results are stored

def copy_simulation_results(results_path, data_dir):
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
    shutil.move(results_path, data_dir)

def add_production_plan_and_stations(production_plan_and_stations_dir, data_dir):
    for file in ["production_plan.csv", "stations.csv"]:
        shutil.copyfile(production_plan_and_stations_dir + "/" + file, data_dir + "/" + file)

def add_headers(headers_dir, data_dir):
    filefirstlines = []
    for file in os.listdir(headers_dir):
        if os.path.isfile(headers_dir + "\\" + file):
            f = open(headers_dir + "\\" + file, "r")
            filefirstlines.append((file, f.readline()))
    for file in os.listdir(headers_dir):
        for (fl, firstl) in filefirstlines:
            if file == fl and file != 'production_plan.csv' and file != 'stations.csv':
                prepend(firstl, data_dir + "\\" + file)

def prepend(str, file):
    with open(file, "r") as fr:
        read = fr.read()
        with open(file, "w") as fw:
            fw.write(str + read)
            fw.close()

def create_simulated_data(simulator_dir, config_filename, data_dir, production_plan_and_stations_dir, headers_dir):
    print("Staring simulation...")
    results_path = perform_simulation(simulator_dir, config_filename)
    copy_simulation_results(results_path, data_dir)
    add_production_plan_and_stations(production_plan_and_stations_dir, data_dir)
    add_headers(headers_dir, data_dir)
    print("Finished simulation...")