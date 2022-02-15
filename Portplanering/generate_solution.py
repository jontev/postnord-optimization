import numpy as np
from numpy import random
import pandas as pd

this_path = 'Portplanering/'

NUMBER_OF_PORTS = 40
NUMBER_OF_TIMES = 2
NUMBER_OF_VEHICLES = 2

order_step_length = NUMBER_OF_PORTS*NUMBER_OF_VEHICLES*NUMBER_OF_TIMES
time_step_length = NUMBER_OF_PORTS*NUMBER_OF_VEHICLES
vehicle_step_length = NUMBER_OF_PORTS

P = list(range(NUMBER_OF_PORTS))
T = list(range(NUMBER_OF_TIMES))
V = list(range(NUMBER_OF_VEHICLES)) # 0 = lastbil, 1 = släp


#Checks if a vehicle is ok to place at a given port at a given time for a given order.
#Divided into 3 parts, each creating a boolean and every boolean has to be true to place a vehicle.
def ok_to_place(y, order, time, vehicle, port, vehicle_counter, schedule, NUMBER_OF_ORDERS, vehicle_cap, L, S, m):

    # Can't use more vehicles than vehicle capacity for the order (At most 1 truck and 1 trailer)
    available_vehicles = (vehicle_counter[vehicle,order] < vehicle_cap[vehicle,order])[0]

    # Checks if there are enough slots for all the vehicles at the time
    # This is only checked when placing the first vehicle, if two the second will always be ok
    available_timeslot = False
    #Nothing scheduled
    if sum(schedule[order,:]) == 0:
        occupied_ports = 0
        for k in range(NUMBER_OF_ORDERS):
            occupied_ports += sum(y[(k*order_step_length + time*time_step_length) :
            ((k*order_step_length + (time + 1)*time_step_length))])
        num_available_ports = NUMBER_OF_PORTS - occupied_ports
        #Is the amount of vehicles in this order less than number of available ports
        if (L[order] + S[order]) <= num_available_ports and m[order] >= time:
            available_timeslot = True
            schedule[order,time] = 1
    #If first vehicle is already placed, the next vehicle must be ok to place at same time slot.
    elif schedule[order,time] == 1:
        available_timeslot = True

    # Port can't be occupied by any type of vehicle for any other order at the same time interval
    available_port = True
    for orders in range(NUMBER_OF_ORDERS):
        for vehicles in range(NUMBER_OF_VEHICLES):
            idx = orders*order_step_length + time*time_step_length + vehicles*vehicle_step_length + port
            if y[idx] != 0:
                available_port = False

    return available_port and available_timeslot and available_vehicles


def generate_random_solution():
    S = pd.read_csv(this_path+'Sj.csv')
    L = pd.read_csv(this_path+'Lj.csv')
    m = pd.read_csv(this_path+'mj.csv')
    dij = pd.read_csv(this_path+'dij.csv')
    S = S.to_numpy()
    L = L.to_numpy()
    m = m.to_numpy()
    dij = dij.to_numpy()

    NUMBER_OF_ORDERS = len(L)

    #timeslot 0, vehicle 1 and port 2
    J = list(range(NUMBER_OF_ORDERS))

    vehicle_cap = np.array((L,S)) #Matrix with first row L second row S
    vehicle_counter = np.zeros([NUMBER_OF_VEHICLES, NUMBER_OF_ORDERS])
    y = np.zeros(NUMBER_OF_ORDERS*NUMBER_OF_TIMES*NUMBER_OF_VEHICLES*NUMBER_OF_PORTS) #Vectorize y variable
    schedule = np.zeros([NUMBER_OF_ORDERS, NUMBER_OF_TIMES])

    # Fixing to prioritize morning orders
    m_n = np.array(m)
    m_n = [val for sublist in m_n for val in sublist]
    J = [x for _,x in sorted(zip(m_n,J))]

    # randomly order sets to avoid any bias
    random.shuffle(P); random.shuffle(V); random.shuffle(T)
    for order in J:
        random.shuffle(T) #shuffle again to avoid bias
        for time in T:
            random.shuffle(V)
            for vehicle in V: # randomly ordered vehichles
                random.shuffle(P)
                for port in P: # randomly ordered ports
                    index = order*order_step_length + time*time_step_length + vehicle*vehicle_step_length + port
                    if ok_to_place(y, order, time, vehicle, port, vehicle_counter, schedule, NUMBER_OF_ORDERS, vehicle_cap, L, S, m):
                        y[index] = 1 #place a vehicle
                        vehicle_counter[vehicle,order] += 1 #a vehicle of type vehicle has been used for order order
        
    return y
