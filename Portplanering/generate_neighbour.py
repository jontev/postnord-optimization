import numpy as np
from numpy import random
import math
import pandas as pd
this_path = 'Portplanering/'

NUMBER_OF_PORTS = 40
NUMBER_OF_TIMES = 2
NUMBER_OF_VEHICLES = 2

m = pd.read_csv(this_path+'mj.csv')
m = m.to_numpy()

order_step_length = NUMBER_OF_PORTS*NUMBER_OF_VEHICLES*NUMBER_OF_TIMES
time_step_length = NUMBER_OF_PORTS*NUMBER_OF_VEHICLES
vehicle_step_length = NUMBER_OF_PORTS

P = list(range(NUMBER_OF_PORTS))

def generate_neighbours(y, neighbourhood):
    y_index = np.where(y == 1) #This does not have to be created all the time, find a way to optimize this
    y_index = np.copy(y_index[0])
    y_neighbours = np.zeros(len(y))

    #--------------------------------Swap port---------------------------------

    if(neighbourhood == "swap_port"):
        print("Swap_port ACTIVE")
        vehicle_to_swap = random.choice(y_index) #choose random vehicle to swap
        index_of_yindex = np.where(y_index == vehicle_to_swap)[0] #Find where in y_index its located
        
        #Find which time the chosen vehicle to swap is scheduled
        time_vehicle_to_swap = get_time(vehicle_to_swap)

        #Go through every vehicle and if it is scheduled to the same time
        #Swap port with the chosen vehicle and create a neighbour
        counter = 0
        for vehicles in y_index:
            #Create copy of y and y_index
            y_neighbour = np.copy(y)
            y_index_neighbour = np.copy(y_index)

            #Find which time the chosen vehicle to swap is scheduled
            time_vehicle = get_time(vehicles)

            if vehicles != vehicle_to_swap and time_vehicle == time_vehicle_to_swap:
                y_neighbour[vehicle_to_swap] = 0
                y_neighbour[vehicles] = 0

                port_vehicle_to_swap = get_port(vehicle_to_swap)
                port_vehicles = get_port(vehicles)

                new_vehicle_swapped = vehicle_to_swap + (port_vehicles - port_vehicle_to_swap) #New position in y list
                new_vehicles = vehicles + (port_vehicle_to_swap - port_vehicles)

                y_neighbour[new_vehicle_swapped] = 1
                y_neighbour[new_vehicles] = 1

                y_index_neighbour[index_of_yindex[0]] = new_vehicle_swapped
                y_index_neighbour[counter] = new_vehicles

                y_neighbours = np.vstack([y_neighbours, y_neighbour])

                counter += 1

            else:
                counter += 1

    #--------------------------------------------------------------------------


    #-------------------------------Move port----------------------------------

    elif(neighbourhood == "move_port"):
        print("move_port ACTIVE")
        vehicle_to_move = random.choice(y_index)
        index_of_yindex = np.where(y_index == vehicle_to_move)[0]
        time_vehicle_to_move = get_time(vehicle_to_move)
        port_vehicle_to_move = get_port(vehicle_to_move)
        forbidden_ports = []

        #Create list with the port that are occupied at this time
        for ports in y_index:
            port_time = get_time(ports)
            if port_time == time_vehicle_to_move:
                port = get_port(ports)
                forbidden_ports.append(port)

        #Go through every viable port and create a neighbour by moving to that port
        for port_number in P:
            if port_number not in forbidden_ports:
                y_neighbour = np.copy(y)
                y_index_neighbour = np.copy(y_index)

                new_vehicle_moved = vehicle_to_move + (port_number - port_vehicle_to_move)

                y_neighbour[vehicle_to_move] = 0
                y_neighbour[new_vehicle_moved] = 1

                y_index_neighbour[index_of_yindex[0]] = new_vehicle_moved
                y_neighbours = np.vstack([y_neighbours, y_neighbour])

    #--------------------------------------------------------------------------


    #-------------------------------Swap time----------------------------------

    elif(neighbourhood == "swap_time"):
        print("swap_time ACTIVE")
        # INIT: Take a random vehicle and calculate its order number
        vehicle_to_swap = random.choice(y_index)
        order_num = get_order(vehicle_to_swap)

        # Do not try to move a order which must be placed at time 0
        # Keep searching for vehicles which belongs to others that can
        # be moved to other times.
        while m[order_num]  == 0:
            vehicle_to_swap = random.choice(y_index)
            order_num = get_order(vehicle_to_swap)

        time_vehicle_to_swap = get_time(vehicle_to_swap)

        num_of_vehicles = 0

        # List of what orders that should be swapped
        vehicles_to_swap = []

        # List of all orders, duplicates are orders that are assigned to two ports.
        vehicles_per_order = [0] * len(m)

        # Calculate how many vehicles that should be swapped and determine
        # and add them to vehicles_to_swap
        for i in y_index:
            vehicles_per_order[get_order(i)] += 1
            if order_num == get_order(i):
                num_of_vehicles += 1
                vehicles_to_swap.append(i)

        vehicles_per_order = np.array(vehicles_per_order)

        # y_index_index = orders that have the same numbers of vehicles as swap
        y_index_index = np.where(vehicles_per_order == num_of_vehicles)[0]

        # Make y_index_index to y_index
        orders_to_swap_with = []
        for item in y_index_index:
            tmp = []
            for i in y_index:
                if item == get_order(i) and time_vehicle_to_swap != get_time(i) and time_vehicle_to_swap <= m[get_order(i)]:
                    tmp.append(i)
            orders_to_swap_with.append(tmp)
        
        # Delete empty lists
        orders_to_swap_with = [x for x in orders_to_swap_with if x]
        # Orders that are OK to swap with

        for order in orders_to_swap_with:
            new_vehicles_to_swap_to = []
            new_vehicles_to_swap_from = []
            y_neighbour = np.copy(y)
            i = 0
            for vehicle in order:
                # What time and port it swaps to
                time_to_swap_to = get_time(vehicle)
                port_to_swap_to = get_port(vehicle)

                # What time and port it swaps from
                time_to_swap_from = time_vehicle_to_swap
                port_to_swap_from = get_port(vehicles_to_swap[i])

                new_vehicles_to_swap_to.append(int(vehicles_to_swap[i] + (port_to_swap_to - port_to_swap_from) + time_step_length*(time_to_swap_to - time_to_swap_from)))
                new_vehicles_to_swap_from.append(int(vehicle + (port_to_swap_from - port_to_swap_to) + time_step_length*(time_to_swap_from - time_to_swap_to)))

                y_neighbour[new_vehicles_to_swap_to[i]] = 1
                y_neighbour[vehicles_to_swap[i]] = 0

                y_neighbour[new_vehicles_to_swap_from[i]] = 1
                y_neighbour[vehicle] = 0
                i += 1

            y_neighbours = np.vstack([y_neighbours, y_neighbour])

    #--------------------------------------------------------------------------


    #-------------------------------Move time----------------------------------

    elif(neighbourhood == "move_time"):
        print("move_time ACTIVE")
        vehicle_to_move = random.choice(y_index)
        order_num = get_order(vehicle_to_move)

        # Do not try to move a order which must be placed at time 0
        while m[order_num] == 0:
            vehicle_to_move = random.choice(y_index)
            order_num = get_order(vehicle_to_move)

        num_of_vehicles = 0
        vehicles_to_move = []

        # Take which cars that should be moved.
        for i in y_index:
            if order_num == get_order(i):
                num_of_vehicles += 1
                vehicles_to_move.append(i)

        # index_of_yindex = np.where(y_index == vehicles_to_move)[0]
        time_vehicle_to_move = get_time(vehicle_to_move)
        port_vehicle_to_move = np.zeros((len(vehicles_to_move)))
        vehicles = range(num_of_vehicles)

        # Add which portnumbers to vehicles to move
        for i in vehicles:
            port_vehicle_to_move[i] = get_port(vehicles_to_move[i])

        for t in range(NUMBER_OF_TIMES):
            forbidden_ports = []

            if t != time_vehicle_to_move and t <= m[order_num]:
                for i in y_index:
                    if t == get_time(i):
                        forbidden_ports.append(get_port(i))

                new_vehicles_to_move = []
                for port_number in P:
                    if port_number not in forbidden_ports:
                        new_vehicles_to_move.append(int(vehicles_to_move[0] + (port_number - port_vehicle_to_move[0]) + time_step_length*(t - time_vehicle_to_move)))
                        if num_of_vehicles == 2:
                            forbidden_ports.append(port_number)
                            for port_number2 in P:
                                if port_number2 not in forbidden_ports:
                                    new_vehicles_to_move.append(int(vehicles_to_move[1] + (port_number2 - port_vehicle_to_move[1]) + time_step_length*(t - time_vehicle_to_move)))
                                    y_neighbour = np.copy(y)
                                    y_index_neighbour = np.copy(y_index)
                                    y_neighbour[vehicles_to_move[0]] = 0
                                    y_neighbour[new_vehicles_to_move[0]] = 1
                                    y_neighbour[vehicles_to_move[1]] = 0
                                    y_neighbour[new_vehicles_to_move[1]] = 1
                                    y_neighbours = np.vstack([y_neighbours, y_neighbour])
                                    del new_vehicles_to_move[-1]
                            del forbidden_ports[-1]
                        else:
                            y_neighbour = np.copy(y)
                            y_index_neighbour = np.copy(y_index)
                            y_neighbour[vehicles_to_move[0]] = 0
                            y_neighbour[new_vehicles_to_move[0]] = 1
                            y_neighbours = np.vstack([y_neighbours, y_neighbour])
                        del new_vehicles_to_move[-1]

                        #Construct to send back neighbourhood

    #--------------------------------------------------------------------------

    y_neighbours = np.delete(y_neighbours, (0), axis = 0) #remove first row that is empty from initialization of variable
    
    #if (y_neighbours == np.zeros(len(y))).all():
    if not np.any(y_neighbours): #len(y_neighbours.shape)==1:
        y_neighbours = None

    return(y_neighbours)

def get_order(vehicle_index):
    order = math.floor(vehicle_index / order_step_length)
    return order

def get_time(vehicle_index):
    time = math.floor((vehicle_index % order_step_length) / time_step_length)
    return time

def get_port(vehicle_index):
    port = ((vehicle_index % order_step_length) % time_step_length) % vehicle_step_length
    return port
