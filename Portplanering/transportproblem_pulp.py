
# Import PuLP modeler functions
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, value, PULP_CBC_CMD, LpStatus
import numpy as np
import pandas as pd
this_path = 'Portplanering/'


def greedy_tent_heuristic(tent_orders, y_index, w, a, d, I, T, order_step_length, time_step_length, vehicle_step_length, Kl, Ks):
 
    for order in tent_orders:
        tmp_idx = np.where( y_index // 160 == order)
        ports_of_tent_order = y_index[tmp_idx] % 40 # ports used for this order, either just one port (one vehicle) or two
        if len(ports_of_tent_order) < 2: # just one vehicle, assign it to pick up stuff at tent
            w[ports_of_tent_order[0], order] = 1
        else: # greedily assign the vehicle

           # ALTERNATIVE 1
           port = ports_of_tent_order[0]
           greedy_cost_of_alternative_1 = sum(a[i,port]*d[i,order] for i in I)
          
           # ALTERNATIVE 2
           port = ports_of_tent_order[1]
           greedy_cost_of_alternative_2 = sum(a[i,port]*d[i,order] for i in I)
           
           if (greedy_cost_of_alternative_1 <= greedy_cost_of_alternative_2) and (d[0,order] <= 18):
               w[ports_of_tent_order[0], order] = 1
           else:
               w[ports_of_tent_order[1], order] = 1
    return w


def solve_transportproblem(y, w, a, d, I, P, J, T, Kl, Ks, order_step_length, time_step_length, vehicle_step_length, a_real):

    indicies_of_placed_vehicles, = np.where(y!=0)

    def check_if_vehicle(p,j,t,v):
        #checks if vehicle of type v (0=truck, 1=trailer) has been placed at port p for order j in time slot t
        temp_idx = j*order_step_length + t*time_step_length + \
                   v*vehicle_step_length + p
        return temp_idx in indicies_of_placed_vehicles

    # Creates the 'prob' variable to contain the problem data
    prob = LpProblem("Transportation_problem", LpMinimize)

    # Creates a list of tuples containing all the possible routes for transport
    Routes = [(i, p, j) for i in I for p in P for j in J]

    # A dictionary called 'x' is created to contain the variables
    x = LpVariable.dicts("x", (I, P, J), lowBound=0, upBound = None, cat= "Continuous")
    
    # The objective function is added to 'prob' first
    prob += (lpSum([x[i][p][j] * a[i,p] for (i, p, j) in Routes]), "Objective function")
    
    # The supply constraints
    for i in I:
        for j in J:
            prob += (lpSum([x[i][p][j] for p in P]) == d[i,j], None)
    
    # The demand constraints
    for p in P:
        for j in J:
            prob += (lpSum([x[i][p][j] for i in I]) <= sum(Kl*check_if_vehicle(p,j,t,0) + Ks*check_if_vehicle(p,j,t,1) for t in T), None)
    
    for p in P:
        for j in J:
            prob += (x[0][p][j] == w[p,j]*d[0,j], None)
    
    prob.solve(PULP_CBC_CMD(msg=False)) # argument stops printing stuff in the terminal
    #print("Status:", LpStatus[prob.status])
    #print(LpStatus[prob.status])
    #vars_list = prob.variables()
    #vars_list.sort(key=lambda x:x.name)
    #print(vars_list)
    x_values = np.array([[v.name,v.varValue] for v in prob.variables()])
    #x_values = [[v.name, v.varValue] for v in prob.variables()]
    
    obj_value = value(prob.objective)
    
    return obj_value, x_values

def transportproblem(y, y_original=None, current_cost=0):
    """
    :param: y solution, an np.array, if y_original is not None then this is a neigbour of y_original
    :param: y_original, y solution from which the neighbours were generated
    :param: current_cost, cost from y_original
    """

    # Parameters and data
    d = pd.read_csv(this_path+"dij.csv")
    d = d.to_numpy()
    a_real = pd.read_csv(this_path+"aip.csv")
    a_real = a_real.to_numpy()
    a_real = a_real.T
    #a = pd.read_csv(this_path+"aip_penalty.csv")
    a = pd.read_csv(this_path+"aip_penalty2.csv")
    a = a.to_numpy()
    a = a.T # Transpose the "a" matrix

    NUMBER_OF_PORTS = 40 #fixed number
    NUMBER_OF_TIMES = 2
    NUMBER_OF_VEHICLES = 2
    NUMBER_OF_ORDERS = d.shape[1]
    NUMBER_OF_ZONES = d.shape[0]
    I = list(range(NUMBER_OF_ZONES))
    P = list(range(NUMBER_OF_PORTS))
    J = list(range(NUMBER_OF_ORDERS))
    T = list(range(NUMBER_OF_TIMES))
    order_step_length = NUMBER_OF_PORTS*NUMBER_OF_VEHICLES*NUMBER_OF_TIMES
    time_step_length = NUMBER_OF_PORTS*NUMBER_OF_VEHICLES
    vehicle_step_length = NUMBER_OF_PORTS
    Kl = 18
    Ks = 30

    # Tent
    w = np.zeros(shape=(len(P), len(J)))
    tent_orders, = np.where(d[0] > 0) # which orders have stuff at the tent

    if y_original is None: # solve problem for the first time

        y_index, = np.where(y != 0) # positions of placed vehicles in this solution (or neigbour)

        # TENT STUFF
        w = greedy_tent_heuristic(tent_orders, y_index, w, a, d, I, T, order_step_length, time_step_length, vehicle_step_length, Kl, Ks)

        obj_val, x= solve_transportproblem(y, w, a, d, I, P, J, T, Kl, Ks, order_step_length, time_step_length, vehicle_step_length, a_real)

    else: # solve 2 partial problems
        x = 0
        indicies_of_placed_vehicles_neighbour, = np.where(y!=0)  # positions of placed vechicles for the neighbour
        indicies_of_placed_vehicles_original, = np.where(y_original != 0 ) # positions of placed vehicles for current solution
        changed_positions, = np.where(indicies_of_placed_vehicles_neighbour - indicies_of_placed_vehicles_original != 0) # find which positions are different
        changed_orders = set(indicies_of_placed_vehicles_original[changed_positions] // 160) # finds for which orders (//160) the positions are different, arbitrary if use original or neigbour

        ports_used_before = np.array([]) # empty array
        ports_used_after = np.array([])
        for order in changed_orders:
            ports_used_before = np.append( ports_used_before, indicies_of_placed_vehicles_original[np.where( indicies_of_placed_vehicles_original // 160 == order)] % 40)
            # for the orders that have been altered with, which ports were used before the permutation ( in the original solution)
            ports_used_after = np.append( ports_used_after, indicies_of_placed_vehicles_neighbour[np.where( indicies_of_placed_vehicles_neighbour // 160 == order)] % 40)
            # same but for the neighbour, so the ports to be used after the permutation
        ports_used_before = [int(p) for p in set(ports_used_before)] # remove possible duplicates and convert to integer
        ports_used_after = [int(p) for p in set(ports_used_after)]

        # Here we can try all combinations for the tent (if necessary)
        # or use greedy heuristic like below
        subset_tent_orders = list(set.intersection(set(tent_orders), set(changed_orders)))
        w_before = np.zeros(shape=(len(P), len(J)))
        w_after = np.zeros(shape=(len(P), len(J)))

        w_before = greedy_tent_heuristic(subset_tent_orders, indicies_of_placed_vehicles_original, w_before, a, d, I, T, order_step_length, time_step_length, vehicle_step_length, Kl, Ks)
        w_after = greedy_tent_heuristic(subset_tent_orders, indicies_of_placed_vehicles_neighbour, w_after, a, d, I, T, order_step_length, time_step_length, vehicle_step_length, Kl, Ks)

        obj_val_before = solve_transportproblem(y_original, w_before, a, d, I, ports_used_before, changed_orders, T, Kl, Ks, order_step_length, time_step_length, vehicle_step_length, a_real)[0]
        obj_val_after = solve_transportproblem(y, w_after, a, d, I, ports_used_after, changed_orders, T, Kl, Ks, order_step_length, time_step_length, vehicle_step_length, a_real)[0]

        obj_val = current_cost - obj_val_before + obj_val_after

    return obj_val, x

