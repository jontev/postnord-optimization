import sys
import numpy as np
sys.path.append('../Bilbokning/src')
from generate_solution import generate_random_solution
from generate_neighbour import generate_neighbours, get_order, get_time, get_port

NUMBER_OF_PORTS = 40
NUMBER_OF_TIMES = 2
NUMBER_OF_VEHICLES = 2


NEIGHBOURHOODS = ['swap_port', 'move_port', 'swap_time', 'move_time']


order_step_length = NUMBER_OF_PORTS*NUMBER_OF_VEHICLES*NUMBER_OF_TIMES
time_step_length = NUMBER_OF_PORTS*NUMBER_OF_VEHICLES
vehicle_step_length = NUMBER_OF_PORTS


def show_everything(y_index,granne_index):
    #y = generate_random_solution()
    #y_neighbours = generate_neighbours(y, NEIGHBOURHOODS[3])
    
    #granne = y_neighbours[0]
    
    #y_index = np.where(y)[0]
    #granne_index = np.where(granne == 1)[0]
    
    l = len(y_index)
    
    order_y = [0]*l
    order_g = [0]*l
    
    time_y = [0]*l
    time_g = [0]*l
    
    port_y = [0]*l
    port_g = [0]*l
    
    print('order, tid, port')
    ctr = 0
    for i in y_index:
        order_y[ctr] = str(get_order(i))
        time_y[ctr] = str(get_time(i))
        port_y[ctr] = str(get_port(i))
        ctr += 1
    ctr = 0
    for i in granne_index:
        order_g[ctr] = str(get_order(i))
        time_g[ctr] = str(get_time(i))
        port_g[ctr] = str(get_port(i))
        ctr += 1
    for i in range(ctr):
        print(order_y[i]+' '+time_y[i]+' '+port_y[i]+'     '+order_g[i]+' '+time_g[i]+' '+port_g[i])
        
        
show_everything()