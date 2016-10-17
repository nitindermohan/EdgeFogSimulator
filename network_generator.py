
import networkx as nx
import matplotlib.pyplot as plt
import random
import os
import subprocess

def decision(probability):
    return random.random() < probability

cwdir = os.getcwd()

####Enter inputs for device placements
###Specify number of device nodes
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

####################################

##Create an empty graph
G=nx.Graph()   #Graph for devices

H=nx.Graph()   #Graph for jobs

edge_nodes = list(range(0,no_edge_nodes))
fog_nodes = list(range(no_edge_nodes,total_nodes))

job_list = list(range(0,no_jobs))

##Create a filepath for writing files for scripts
filepath = "Files/"+str(total_nodes)
#print(filepath)

##Create the directory if it doesnt exist. Can raise an exception on race
if not os.path.exists(filepath):
    os.makedirs(filepath)

##Add Device nodes to graph
for i in enumerate(edge_nodes):
    G.add_node(i[1],processing=random.randint(proc_edge_low,proc_edge_high),name=i[1])

for i in enumerate(fog_nodes):
    G.add_node(i[1],processing=random.randint(proc_fog_low,proc_fog_high),name=i[1])

##Add job nodes to graph
for i in enumerate(job_list):
    H.add_node(i[1],size=random.randint(job_size_low,job_size_high),name=i[1])

##get processing costs
processing = list(nx.get_node_attributes(G,'processing').values())

##get job sizes
sizes = list(nx.get_node_attributes(H,'size').values())

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

###Add connections between jobs
for i in range(len(job_list)):
    j=i+1       ##Avoid self loops
    while j<len(job_list):
        choice = decision(prob_job_dependence)
        if choice==True:
            H.add_edge(job_list[i],job_list[j])
        j=j+1

###############################################
            #OUTPUTS
###############################################
######Write to files for input to scripts

# write processing cost to file
f = open(filepath + "/device_proc", "w")
for j in enumerate(processing):
    f.write(str(j[1]) + " ")
f.close()

#write job size to file
f = open(filepath + "/job_size", "w")
for j in enumerate(sizes):
    f.write(str(j[1]) + " ")
f.close()

##write network costs to file
f = open(filepath+"/device_conn","w")
for i in range(total_nodes):
    for j in range(total_nodes):
        if i==j:
            f.write("99 ")
        else:
            try:
                f.write(str(nx.dijkstra_path_length(G,i,j,weight="weight")) + " ")
            except:
                f.write("0 ")
    if i!=total_nodes-1:
        f.write("\n")
f.close()

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

#########Draw the device graph
pos = nx.spring_layout(G)

plt.figure(1, figsize=(20,20))
node_name_labels = nx.get_edge_attributes(G, "name")
nx.draw_networkx_nodes(G,pos,nodelist=edge_nodes,node_color='b', node_size=300 ,alpha=0.7)
nx.draw_networkx_nodes(G,pos,nodelist=fog_nodes,node_color='r', node_size=500, node_shape='s',alpha=0.7)
nx.draw_networkx_labels(G, pos, edge_labels=node_name_labels)

edge_weight_labels = nx.get_edge_attributes(G, "weight")

nx.draw_networkx_edges(G, pos)
nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_weight_labels)

plt.savefig(filepath+"/device_layout.png")

###Draw job graph
plt.figure(2,figsize=(20,20))
jobs_labels = nx.get_node_attributes(H,"name")

nx.draw_networkx_nodes(H, pos, alpha=0.7)
nx.draw_networkx_labels(H, pos,labels=jobs_labels)

nx.draw_networkx_edges(H, pos)

plt.savefig(filepath+"/jobs_layout.png")

plt.show(block=False)

##Run algorthm to find the assignment with generated topology
subprocess.Popen("python3 "+cwdir+"/"+"assignment_processing.py "+str(total_nodes)+" 1", shell=True)

plt.show()