
import networkx as nx
import matplotlib.pyplot as plt
import random
import os
import subprocess
import shutil

def decision(probability):
    return random.random() < probability

cwdir = os.getcwd()

print("Enter one of the following:")
print("1. Use default values for generation")
print("[Any other number for entering custom values]")
choice = int(input("Enter your choice: "))

if choice==1:
    total_nodes = int(input("Enter total number of devices: "))
    no_edge_nodes = int(0.6*total_nodes)
    no_fog_nodes = int(total_nodes-no_edge_nodes)
    proc_edge_low = 2
    proc_edge_high = 5
    proc_fog_low = 7
    proc_fog_high = 9

    prob_edge = 0.2
    prob_fog = 0.6
    prob_edge_fog = 0.5
    no_jobs = total_nodes

    job_size_low = 2
    job_size_high = 6

    prob_job_dependence = 0.2
else:
    print("#### Enter the number of devices in edge-fog cloud ####")
    print("#### Press enter to take the default value ####")

    total_nodes = int(input("Enter total number of devices: "))

    default_edge = int(0.6*total_nodes)
    default_fog = int(total_nodes-default_edge)

    no_edge_nodes = int(input("Enter the number of edge nodes [Default=60% of total devices]: ") or default_edge)
    no_fog_nodes = int(input("Enter the number of fog nodes [Default=40% of total devices]: ") or default_fog)

    ###Specify lower and upper bounds of processing costs
    print("#### Enter the processing power bounds of the devices ####")
    proc_edge_low = int(input("Lowest processing power of edge device [Default=2]: ") or "2")
    proc_edge_high = int(input("Highest processing power of edge device [Default=5]: ") or "5")
    proc_fog_low = int(input("Lowest processing power of fog device [Default=7]: ") or "7")
    proc_fog_high = int(input("Highest processing power of fog device [Default=9]: ") or "9")

    ##Specify probabilities for network connections
    print("#### Enter the network densities between the devices ####")
    prob_edge = float(input("Enter connections density between edge nodes (0-1) [Default=0.2]: ") or "0.2")
    prob_fog = float(input("Enter connections density between fog nodes (0-1) [Default=0.6]: ") or "0.6")
    prob_edge_fog = float(input("Enter connections density between edge and fog nodes (0-1) [Default=0.5]: ") or "0.5")

    ###Enter inputs for job graphs
    ##Enter total number of jobs (Change this later to accomodate more jobs than devices)
    no_jobs = 0
    while(no_jobs!=total_nodes):
        no_jobs=int(input("Enter number of jobs deployed on edge-fog cloud [Default=Total number of devices]: ") or total_nodes)
        if no_jobs!=total_nodes:
            print("Please enter number of jobs as equal to number of total available devices")

    ##Enter the sizes of the jobs
    job_size_low = int(input("Enter the lowest job size [Default=2]: ") or "2")
    job_size_high = int(input("Enter highest job size [Default=6]: ") or "6")

    ##Enter the inter dependence between the jobs
    prob_job_dependence = float(input("Enter the inter-dependence ratio between jobs (0-1) [Default=0.2]: ") or "0.2")

print("Choose analysis type:")
print("1. Confidence interval on constant network topology")
print("2. Job dependence analysis")
print("3. Device connection analysis")
print("[Any other number for normal operation]")
analysis_type = int(input("Enter your analysis: "))

# while (analysis_type!=1) or (analysis_type!=2):
#     analysis_type = input("Enter valid analysis type!: ")

if analysis_type==1: #confidence analysis
    no_iterations = int(input("Enter the number of iterations for confidence analysis: "))
    no_iterations = no_iterations+1

if analysis_type==2: #Job dependence analysis
    no_iterations = int(input("Enter step sizes for job dependence: "))

if analysis_type==3: #device connection analysis
    print("Enter the connection type to analyse")
    print("1. Connections between the Edge devices")
    print("2. Connections between the Fog devices")
    print("3. Connections between the Edge-Fog devices")
    connection_type = int(input())
    if connection_type==1:
        connection_min = float(input("Enter lower bound of connection density [default=0.2]: ") or "0.2")
    elif connection_type==2:
        connection_min = float(input("Enter lower bound of connection density [default=0.6]: ") or "0.6")
    elif connection_type == 3:
        connection_min = float(input("Enter lower bound of connection density [default=0.5]: ") or "0.5")
    connection_max = float(input("Enter upper bound of connection density: "))
    connection_step_size = float(input("Enter step size [Default=0.1]: ") or "0.1")

##Create an empty graph
G=nx.Graph()   #Graph for devices

H=nx.Graph()   #Graph for jobs

edge_nodes = list(range(0,no_edge_nodes))
fog_nodes = list(range(no_edge_nodes,total_nodes))

job_list = list(range(0,no_jobs))

##Create a filepath for writing files for scripts
filepath = "Files/"+str(total_nodes)

##Create the directory if it doesnt exist. Can raise an exception on race
if not os.path.exists(filepath):
    os.makedirs(filepath)
else:
    shutil.rmtree(filepath)
    os.makedirs(filepath)

if analysis_type==1: ##Confidence Analysis
#####################################################
#
# In this analysis, we are checking the confidence
# convergence in randomness of python. We keep the
# job sizes and connections same but find its ass-
# ignmnet in multiple iterations of device graphs.
# The goal is to find the confidence interval in
# which the network and processing cost will remain.
#
######################################################

    ##Add job nodes to graph
    for i in enumerate(job_list):
        H.add_node(i[1], size=random.randint(job_size_low, job_size_high), name=i[1])

    ##get job sizes
    sizes = list(nx.get_node_attributes(H, 'size').values())

    # write job size to file
    f = open(filepath + "/job_size", "w")
    for j in enumerate(sizes):
        f.write(str(j[1]) + " ")
    f.close()

    ###Add connections between jobs
    for i in range(len(job_list)):
        j=i+1       ##Avoid self loops
        while j<len(job_list):
            choice = decision(prob_job_dependence)
            if choice==True:
                H.add_edge(job_list[i],job_list[j])
            j=j+1

    ##Write edge connections to file
    f = open(filepath+"/job_conn","w")
    for i in range(len(job_list)):
        for j in range(len(job_list)):
            if H.has_edge(i,j):
                f.write("1 ")
            else:
                f.write("0 ")
        if i!=len(job_list)-1:
            f.write("\n")
    f.close()

    for i in range(0,no_iterations):
        ##Add Device nodes to graph
        for i in enumerate(edge_nodes):
            G.add_node(i[1],processing=random.randint(proc_edge_low,proc_edge_high),name=i[1])

        for i in enumerate(fog_nodes):
            G.add_node(i[1],processing=random.randint(proc_fog_low,proc_fog_high),name=i[1])

        ##get processing costs
        processing = list(nx.get_node_attributes(G,'processing').values())

        #####################################
        ###Add connections between devices

        ##Connections between the edge
        for i in range(len(edge_nodes)):
            j=i+1
            while j<len(edge_nodes):
                choice = decision(prob_edge)
                if choice==True:
                    G.add_edge(edge_nodes[i],edge_nodes[j], weight=random.randint(1,2))
                j=j+1

        ##Connections between the fog
        for i in range(len(fog_nodes)):
            j = i + 1
            while j < len(fog_nodes):
                choice = decision(prob_fog)
                if choice == True:
                    G.add_edge(fog_nodes[i], fog_nodes[j], weight=random.randint(1, 2))
                j = j + 1

        #Connections between the edge and fog
        lastCount = 0
        for i in range(len(edge_nodes)):
            alreadyConnected = False
            for j in range(len(fog_nodes)):
                lastCount = lastCount + 1
                choice = decision(prob_edge_fog)
                if choice == True:
                    G.add_edge(edge_nodes[i], fog_nodes[j], weight=random.randint(3,5))
                    alreadyConnected=True
                if (lastCount==len(fog_nodes)-1 and alreadyConnected==False): #to ensure that edge node is connected to atleast one fog node
                    randomNode = random.randint(0,len(fog_nodes)-1)
                    G.add_edge(edge_nodes[i], fog_nodes[randomNode], weight=random.randint(3,5))

        ###############################################
                    #OUTPUTS
        ###############################################
        ######Write to files for input to scripts

        # write processing cost to file
        f = open(filepath + "/device_proc", "w")
        for j in enumerate(processing):
            f.write(str(j[1]) + " ")
        f.close()

        ##write network costs to file
        f = open(filepath+"/device_conn","w")
        for i in range(total_nodes):
            for j in range(total_nodes):
                if i==j:
                    f.write("99 ")
                else:
                    f.write(str(nx.dijkstra_path_length(G,i,j,weight="weight")) + " ")
            if i!=total_nodes-1:
                f.write("\n")
        f.close()

        analysis_filepath = "Files/Confidence_Analysis/"
        # print(filepath)

        ##Create the directory if it doesnt exist. Can raise an exception on race
        if not os.path.exists(analysis_filepath):
            os.makedirs(analysis_filepath)

        ##Run algorthm to find the assignment with generated topology
        process = subprocess.Popen("python3 "+cwdir+"/"+"assignment_processing.py "+str(total_nodes)+" 3", shell=True)
        process.wait()

if analysis_type==2: ##Job dependence
#####################################################
# In this analysis, we are checking the increase ratio
# in networking cost when we increase the dependence
# between the jobs to be deployed on devices. We keep
# the device placement and processing powers the same
# and find the networking cost through Edge-Fog, Min
# and Max bounds while increasing the dependence.
######################################################

    ##Add job nodes to graph
    for i in enumerate(job_list):
        H.add_node(i[1], size=random.randint(job_size_low, job_size_high), name=i[1])

    ##get job sizes
    sizes = list(nx.get_node_attributes(H, 'size').values())

    ##Add Device nodes to graph
    for i in enumerate(edge_nodes):
        G.add_node(i[1], processing=random.randint(proc_edge_low, proc_edge_high), name=i[1])

    for i in enumerate(fog_nodes):
        G.add_node(i[1], processing=random.randint(proc_fog_low, proc_fog_high), name=i[1])

    ##get processing costs
    processing = list(nx.get_node_attributes(G, 'processing').values())

    #####################################
    ###Add connections between devices

    ##Connections between the edge
    for i in range(len(edge_nodes)):
        j = i + 1
        while j < len(edge_nodes):
            choice = decision(prob_edge)
            if choice == True:
                G.add_edge(edge_nodes[i], edge_nodes[j], weight=random.randint(1, 2))
            j = j + 1

    ##Connections between the fog
    for i in range(len(fog_nodes)):
        j = i + 1
        while j < len(fog_nodes):
            choice = decision(prob_fog)
            if choice == True:
                G.add_edge(fog_nodes[i], fog_nodes[j], weight=random.randint(1, 2))
            j = j + 1

    # Connections between the edge and fog
    lastCount = 0
    for i in range(len(edge_nodes)):
        alreadyConnected = False
        for j in range(len(fog_nodes)):
            lastCount = lastCount + 1
            choice = decision(prob_edge_fog)
            if choice == True:
                G.add_edge(edge_nodes[i], fog_nodes[j], weight=random.randint(3, 5))
                alreadyConnected = True
            if (lastCount == len(
                    fog_nodes) - 1 and alreadyConnected == False):  # to ensure that edge node is connected to atleast one fog node
                randomNode = random.randint(0, len(fog_nodes) - 1)
                G.add_edge(edge_nodes[i], fog_nodes[randomNode], weight=random.randint(3, 5))

    ###############################################
    # OUTPUTS
    ###############################################
    ######Write to files for input to scripts

    # write job size to file
    f = open(filepath + "/job_size", "w")
    for j in enumerate(sizes):
        f.write(str(j[1]) + " ")
    f.close()

    # write processing cost to file
    f = open(filepath + "/device_proc", "w")
    for j in enumerate(processing):
        f.write(str(j[1]) + " ")
    f.close()

    ##write network costs to file
    f = open(filepath + "/device_conn", "w")
    for i in range(total_nodes):
        for j in range(total_nodes):
            if i == j:
                f.write("99 ")
            else:
                try:
                    f.write(str(nx.dijkstra_path_length(G, i, j, weight="weight")) + " ")
                except:
                    f.write("0 ")
        if i != total_nodes - 1:
            f.write("\n")
    f.close()

    ##########################################################
    step_size = 1/no_iterations
    prob_job_dependence = 0
    ###Add connections between jobs
    for k in range(0, no_iterations):
        prob_job_dependence += step_size
        for i in range(len(job_list)):
            j = i + 1  ##Avoid self loops
            while j < len(job_list):
                choice = decision(prob_job_dependence)
                if choice == True:
                    H.add_edge(job_list[i], job_list[j])
                j = j + 1

        ##Write edge connections to file
        f = open(filepath + "/job_conn", "w")
        for i in range(len(job_list)):
            for j in range(len(job_list)):
                if H.has_edge(i, j):
                    f.write("1 ")
                else:
                    f.write("0 ")
            if i != len(job_list) - 1:
                f.write("\n")
        f.close()
        analysis_filepath = "Files/Job_Dependence_Analysis/"
        # print(filepath)

        ##Create the directory if it doesnt exist. Can raise an exception on race
        if not os.path.exists(analysis_filepath):
            os.makedirs(analysis_filepath)

        ##Run algorthm to find the assignment with generated topology
        process1 = subprocess.Popen("python3 " + cwdir + "/" + "assignment_processing.py " + str(total_nodes) + " 4", shell=True)
        process2 = subprocess.Popen("python3 "+ cwdir + "/" + "MinMax_bound.py " + str(total_nodes) + " 1", shell=True)
        process1.wait()
        process2.wait()

if analysis_type==3: ##Device Connection Analysis
#####################################################
#
# In this analysis, we try to find the effect of.
# networking cost with device connectivity at edge,
# fog and intermediate connections. The aim of this
# analysis is to find the best possible connection
# density at each layer for a balanced networking cost
#
######################################################

    first_run = True
    ##Add job nodes to graph
    for i in enumerate(job_list):
        H.add_node(i[1], size=random.randint(job_size_low, job_size_high), name=i[1])

    ##get job sizes
    sizes = list(nx.get_node_attributes(H, 'size').values())

    # write job size to file
    f = open(filepath + "/job_size", "w")
    for j in enumerate(sizes):
        f.write(str(j[1]) + " ")
    f.close()

    ###Add connections between jobs
    for i in range(len(job_list)):
        j=i+1       ##Avoid self loops
        while j<len(job_list):
            choice = decision(prob_job_dependence)
            if choice==True:
                H.add_edge(job_list[i],job_list[j])
            j=j+1

    ##Write edge connections to file
    f = open(filepath+"/job_conn","w")
    for i in range(len(job_list)):
        for j in range(len(job_list)):
            if H.has_edge(i,j):
                f.write("1 ")
            else:
                f.write("0 ")
        if i!=len(job_list)-1:
            f.write("\n")
    f.close()

    ##Add Device nodes to graph
    for i in enumerate(edge_nodes):
        G.add_node(i[1], processing=random.randint(proc_edge_low, proc_edge_high), name=i[1])

    for i in enumerate(fog_nodes):
        G.add_node(i[1], processing=random.randint(proc_fog_low, proc_fog_high), name=i[1])

    ##get processing costs
    processing = list(nx.get_node_attributes(G, 'processing').values())

    # write processing cost to file
    f = open(filepath + "/device_proc", "w")
    for j in enumerate(processing):
        f.write(str(j[1]) + " ")
    f.close()

    if connection_type == 1: #change edge nodes
        filename = str(total_nodes)+"_edge_" + str(prob_fog) + "_" + str(prob_edge_fog)
        ##Connections between the fog
        for i in range(len(fog_nodes)):
            j = i + 1
            while j < len(fog_nodes):
                choice = decision(prob_fog)
                if choice == True:
                    G.add_edge(fog_nodes[i], fog_nodes[j], weight=random.randint(1, 2))
                j = j + 1

        # Connections between the edge and fog
        lastCount = 0
        for i in range(len(edge_nodes)):
            alreadyConnected = False
            for j in range(len(fog_nodes)):
                lastCount = lastCount + 1
                choice = decision(prob_edge_fog)
                if choice == True:
                    G.add_edge(edge_nodes[i], fog_nodes[j], weight=random.randint(3, 5))
                    alreadyConnected = True
                if (lastCount == len(
                        fog_nodes) - 1 and alreadyConnected == False):  # to ensure that edge node is connected to atleast one fog node
                    randomNode = random.randint(0, len(fog_nodes) - 1)
                    G.add_edge(edge_nodes[i], fog_nodes[randomNode], weight=random.randint(3, 5))

    if connection_type == 2: #change fog nodes
        filename = str(total_nodes) + "_fog_" + str(prob_edge) + "_" + str(prob_edge_fog)
        ##Connections between the edge
        for i in range(len(edge_nodes)):
            j = i + 1
            while j < len(edge_nodes):
                choice = decision(prob_edge)
                if choice == True:
                    G.add_edge(edge_nodes[i], edge_nodes[j], weight=random.randint(1, 2))
                j = j + 1

        # Connections between the edge and fog
        lastCount = 0
        for i in range(len(edge_nodes)):
            alreadyConnected = False
            for j in range(len(fog_nodes)):
                lastCount = lastCount + 1
                choice = decision(prob_edge_fog)
                if choice == True:
                    G.add_edge(edge_nodes[i], fog_nodes[j], weight=random.randint(3, 5))
                    alreadyConnected = True
                if (lastCount == len(
                        fog_nodes) - 1 and alreadyConnected == False):  # to ensure that edge node is connected to atleast one fog node
                    randomNode = random.randint(0, len(fog_nodes) - 1)
                    G.add_edge(edge_nodes[i], fog_nodes[randomNode], weight=random.randint(3, 5))

    if connection_type==3: #change edge-fog nodes
        filename = str(total_nodes) + "_edge-fog_" + str(prob_edge) + "_" + str(prob_fog)
        ##Connections between the edge
        for i in range(len(edge_nodes)):
            j = i + 1
            while j < len(edge_nodes):
                choice = decision(prob_edge)
                if choice == True:
                    G.add_edge(edge_nodes[i], edge_nodes[j], weight=random.randint(1, 2))
                j = j + 1

        ##Connections between the fog
        for i in range(len(fog_nodes)):
            j = i + 1
            while j < len(fog_nodes):
                choice = decision(prob_fog)
                if choice == True:
                    G.add_edge(fog_nodes[i], fog_nodes[j], weight=random.randint(1, 2))
                j = j + 1

    analysis_filepath = "Files/Device_Connection_Analysis/"
    # print(filepath)

    ##Create the directory if it doesnt exist. Can raise an exception on race
    if not os.path.exists(analysis_filepath):
        os.makedirs(analysis_filepath)


    while connection_min<=connection_max:

        if connection_type==1:
            if first_run==False: #remove all previous connections
                for i in range(len(edge_nodes)):
                    j = i + 1
                    while j < len(edge_nodes):
                        try:
                            G.remove_edge(edge_nodes[i], edge_nodes[j])
                            j += 1
                        except:
                            j += 1

            ##Connections between the edge
            for i in range(len(edge_nodes)):
                j=i+1
                while j<len(edge_nodes):
                    choice = decision(connection_min)
                    if choice==True:
                        G.add_edge(edge_nodes[i],edge_nodes[j], weight=random.randint(1,2))
                    j=j+1

        if connection_type==2:
            if first_run == False:  # remove all previous connections
                for i in range(len(fog_nodes)):
                    j = i + 1
                    while j < len(fog_nodes):
                        try:
                            G.remove_edge(fog_nodes[i], fog_nodes[j])
                            j += 1
                        except:
                            j += 1

            ##Connections between the fog
            for i in range(len(fog_nodes)):
                j = i + 1
                while j < len(fog_nodes):
                    choice = decision(connection_min)
                    if choice == True:
                        G.add_edge(fog_nodes[i], fog_nodes[j], weight=random.randint(1, 2))
                    j = j + 1

        if connection_type==3:
            if first_run == False:  # remove all previous connections
                for i in range(len(edge_nodes)):
                    for j in range(len(fog_nodes)):
                        try:
                            G.remove_edge(edge_nodes[i], fog_nodes[j])
                        except:
                            pass

            #Connections between the edge and fog
            lastCount = 0
            for i in range(len(edge_nodes)):
                alreadyConnected = False
                for j in range(len(fog_nodes)):
                    lastCount = lastCount + 1
                    choice = decision(connection_min)
                    if choice == True:
                        G.add_edge(edge_nodes[i], fog_nodes[j], weight=random.randint(3,5))
                        alreadyConnected=True
                    if (lastCount==len(fog_nodes)-1 and alreadyConnected==False): #to ensure that edge node is connected to atleast one fog node
                        randomNode = random.randint(0,len(fog_nodes)-1)
                        G.add_edge(edge_nodes[i], fog_nodes[randomNode], weight=random.randint(3,5))

        ###############################################
                    #OUTPUTS
        ###############################################
        ######Write to files for input to script

        ##write network costs to file
        f = open(filepath+"/device_conn","w")
        for i in range(total_nodes):
            for j in range(total_nodes):
                if i==j:
                    f.write("99 ")
                else:
                    f.write(str(nx.dijkstra_path_length(G,i,j,weight="weight")) + " ")
            if i!=total_nodes-1:
                f.write("\n")
        f.close()

        ##Run algorthm to find the assignment with generated topology
        process = subprocess.Popen("python3 "+cwdir+"/"+"assignment_processing.py "+str(total_nodes)+" 5", shell=True)
        process.wait()

        file = open(analysis_filepath + str(total_nodes))
        network_cost = file.read()

        f = open(analysis_filepath + filename + ".csv", "a")
        f.write(str(connection_min) + ", " + str(network_cost) + "\n")
        f.close()

        connection_min += connection_step_size
        connection_min = round(connection_min, 1)
        first_run=False

    os.remove(analysis_filepath + str(total_nodes))
