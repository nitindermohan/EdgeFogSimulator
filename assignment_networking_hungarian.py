### Assigning Jobs to Edge and Fog nodes#####
###Nitinder Mohan####
import time
from munkres import Munkres
from collections import defaultdict
import sys

#############################
#INPUT

filepath = "Files/"+ sys.argv[1]

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
        print("Total networking cost: %d" % net_cost)
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

####create network connection matrix
for i in range(len(job_conn)):
    l=[]
    for j in range(len(device_conn)):
        l.append(job_conn[i][j]*device_conn[i][j])
    netw_conn.append(list(l))

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
# if len(job_conn)>17:
#     time.sleep(1200)
connections = [ list(x) for x in b_set ]

n = Munkres();
netw_index = n.compute(netw_conn)
netw_index = [list(elem) for elem in netw_index]

# print("Best case network cost assignment")
# print("")
print("Processing cost: "+str(print_assignment(netw_index, 2)))
print_network_cost(netw_index, connections, 1)