### Assigning Jobs to Edge and Fog nodes#####
###Nitinder Mohan####

from munkres import Munkres
from collections import defaultdict
import itertools
import copy
import sys
import os
import time

#############################
#INPUT

start_time = time.time()

filepath = "Files/"+ sys.argv[1]

print_topology = int(sys.argv[2])

totalNodes = str(sys.argv[1])

with open(filepath+"/device_conn") as f:
    device_conn = [[int(num) for num in line.split()] for line in f]

with open(filepath+"/device_proc") as f:
    for line in f:
        device_proc = [int(i) for i in line.split()]

with open(filepath+"/job_conn") as f:
    job_conn = [[int(num) for num in line.split()] for line in f]

with open(filepath+"/job_size") as f:
    for line in f:
        job_size = [int(i) for i in line.split()]
################################

def list_duplicates(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return (locs for key,locs in tally.items()
                            if len(locs)>1)

def print_assignment(index, command):
    proc_cost=0
    for row, column in index:
        proc = matrix[row][column]
        proc_cost += proc
        if (command==1):
            print("Job %d -> Device %d" % (row+1, column+1))
    if (command==1):
        print("total processing cost: %.3f" % proc_cost)
    else:
        return proc_cost

def print_network_cost(index, connections, command):
    net_cost = 0
    for i in range(len(connections)):
        job1 = connections[i][0]
        job2 = connections[i][1]
        for j in range(len(index)):
            if(index[j][0]==job1):
                device1 = index[j][1]
                continue
            if(index[j][0]==job2):
                device2 = index[j][1]
        cost = device_conn[device1][device2]
        net_cost += cost
    if (command==1):
        print("Networking cost: %d" % net_cost)
    else:
        return net_cost

assign = 1
netw_conn = []

####create processing cost matrix
matrix = []
for i in enumerate(job_size):
    row = []
    for j in enumerate(device_proc):
        row.append(round(i[1]/j[1], 3))
    matrix.append(row)

######get possible combinations yielding to same processing cost#####
duplicates = []
for dup in sorted(list_duplicates(device_proc)):
    duplicates.append(dup)

for p in duplicates:
    if (len(p)>2):
        comb = list(itertools.combinations(p,2))
        duplicates.remove(p)
        for l in comb:
            duplicates.append(list(l))

#####get all possible job connections
connections = []
for i, lst in enumerate(job_conn):
    for j, conn in enumerate(lst):
        if conn == 1:
            if i<j:
                connections.append([i, j])
            else:
                connections.append([j, i])

#remove duplicate both ways connections
b_set = set(tuple(x) for x in connections)
connections = [ list(x) for x in b_set ]
#print(connections)

#####Apply Hungarian assignment algorithm of processing cost##########
m = Munkres();
index = m.compute(matrix)
index = [list(elem) for elem in index]

print("LAP calculation time: " + str(time.time()-start_time))

###################################
best_netw_cost = print_network_cost(index, connections, 2)
best_index=copy.deepcopy(index)
assign = assign+1

permutation_count = 0
index_new=[]
end = 0
for i in range(len(duplicates)):
    index_new = index
    end = i
    while end >= 0:
        first = duplicates[end][0]
        second = duplicates[end][1]
        for j in range(len(index_new)):
            if index_new[j][1] == first:
                index_new[j][1] = second
                continue
            if index_new[j][1] == second:
                index_new[j][1] =first
        netw_cost = print_network_cost(index_new, connections, 2)
        permutation_count = permutation_count+1
        if netw_cost < best_netw_cost:
            best_netw_cost = netw_cost
            best_index = copy.deepcopy(index_new)  # copy the objects of the list as well and not references
        assign = assign+1
        end -= 1

if print_topology==1:
    print_assignment(best_index, 1)
    print_network_cost(best_index, connections, 1)
    print("Sub-permutations: " + str(permutation_count))
    print("")

if print_topology==2:
    print("Processing cost: " + str(print_assignment(best_index, 2)))
    print_network_cost(best_index, connections, 1)
    print("Sub-permutations: "+str(permutation_count))
    print("")
    print("Total completion time: "+str(time.time()-start_time))

if print_topology==3:
    analysis_filepath = "Files/Confidence_Analysis/"
    ##Format output is: Processing cost, Network Cost, Sub-permutations
    f = open(analysis_filepath+totalNodes+".csv", "a")
    if os.path.getsize(analysis_filepath+totalNodes+".csv") == 0:
        f.write("Processing cost, Networking cost, Sub-permutations\n")
    else:
        f.write(str(print_assignment(best_index, 2)) + ", "+str(print_network_cost(best_index, connections, 2)) + ", " + str(permutation_count) + "\n")
    f.close()

if print_topology==4:
    analysis_filepath = "Files/Job_Dependence_Analysis/"
    ##Format output is: Processing cost, Network Cost, Sub-permutations
    f = open(analysis_filepath+totalNodes+"_EF.csv", "a")
    f.write(str(print_network_cost(best_index, connections, 2)) + "\n")
    f.close()

if print_topology==5:
    analysis_filepath = "Files/Device_Connection_Analysis/"
    ##Format output is: Processing cost, Network Cost, Sub-permutations
    f = open(analysis_filepath + totalNodes, "w")
    f.write(str(print_network_cost(best_index, connections, 2)))
    f.close()
