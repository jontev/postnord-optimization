import numpy as np
import math
import random

from generate_neighbour import generate_neighbours
from transportproblem_pulp import transportproblem

def prob_func(current_cost, cost_neighbour, T): #Used to determine if simulated annealing should take on a worse solution
    if random.uniform(0,1) <= math.exp(-(cost_neighbour-current_cost)/T):
        return 1
    else:
        return 0

SOLUTIONS = []

def run_heuristics(y, current_cost, heuristic, neighbourhood, local_opt, best_cost, best_solution, T, COSTS1, COSTS2, tabu_list, tabu_list_max_len):

    y_neighbours = generate_neighbours(y, neighbourhood)
    current_solution = np.copy(y)
  
    while y_neighbours is None:
        print(y_neighbours)
        NEIGHBOURHOODS = ['swap_port', 'move_port', 'swap_time', 'move_time']
        neighbourhood = NEIGHBOURHOODS[random.randrange(4)]
        y_neighbours = generate_neighbours(y, neighbourhood)
        current_solution = np.copy(y)
        print('Detta vart ju knas')

    if (heuristic == 'local_search'):
        cost_vector = []

        for neighbour in y_neighbours: #Calculate costs for each neighbour
            cost = transportproblem(neighbour, current_solution, current_cost)[0]
            cost_vector.append(cost)

        #Sort neighbours w.r.t cost and find cheapest neighbour and its cost
        sorted_index_vector = np.argsort(cost_vector)
        index_of_cheapest_neighbour = sorted_index_vector[0]
        cheapest_neighbour_cost = cost_vector[index_of_cheapest_neighbour]
        cheapest_neighbour = y_neighbours[index_of_cheapest_neighbour]

        if cheapest_neighbour_cost < current_cost: #Updates best solution to the current if its cheaper
            current_cost = cheapest_neighbour_cost
            current_solution = np.copy(cheapest_neighbour)
            best_cost, best_solution = current_cost, np.copy(current_solution)
            #print(all(current_solution == cheapest_neighbour))
            print('new best found = ' + str(current_cost))
            #print('new best found2 = ' + str(transportproblem(current_solution)[0]))
        else:
            print('Local optimum found, Z = ' + str(current_cost))
            local_opt = False
        COSTS1.append(current_cost)

    elif (heuristic == 'simulated_annealing'):
        cost_vector = []
        number_of_neighbours = y_neighbours.shape[0]

        ctr = 0
        #Goes through every neighbour until a cheaper solution is found or until a worse solution is accepted with
        #the probability function
        for neighbour in y_neighbours:
            cost_neighbour = transportproblem(neighbour, current_solution, current_cost)[0]
            ctr += 1

            if cost_neighbour < current_cost:
                current_cost, current_solution = cost_neighbour, np.copy(neighbour)
                print('new best found = ' + str(current_cost))
                break
            elif prob_func(current_cost, cost_neighbour, T):
                current_cost, current_solution = cost_neighbour, np.copy(neighbour)
                T -= 50
                if T <= 0:
                    T = 1
                print('Worse solution Accepted')
                print('Best Cost = ' + str(best_cost))
                print('Current cost = ' + str(current_cost))
                break     
        # If local optimum found, could be for a current solution that is worse than the best found.
        # Sets current solution to best solution found and change neighbourhood
        if current_cost <= best_cost:
            best_cost, best_solution = current_cost, np.copy(current_solution)
        if ctr == number_of_neighbours:
            local_opt = True
            print('Local optimum found, Z = ' + str(current_cost))
        
        COSTS1.append(best_cost)
        COSTS2.append(current_cost)

    elif (heuristic == 'tabu_search'):
        cost_vector = []
        not_in_tabu = True

        for neighbour in y_neighbours: #Calculate cost of each neighbour
            cost = transportproblem(neighbour, current_solution, current_cost)[0]
            cost_vector.append(cost)
        
        sorted_index_vector = np.argsort(cost_vector)

        for index in range(len(y_neighbours)): #Goes through every neighbour, starting with the cheapest. If it's not in tabu list
            #it gets acceped. If not accepted the next one is checked.
            
            cheapest_neighbour_cost = cost_vector[index]
            cheapest_neighbour = y_neighbours[index]

            for tabu in tabu_list:
                if all(cheapest_neighbour == tabu): #If any row in tabu list is identical with current neighbour then its tabu
                    not_in_tabu = False
                    print('This solution is tabu')
                
            if (cheapest_neighbour_cost < current_cost): #If better solution add to tabu list and accept
                current_cost = cheapest_neighbour_cost
                current_solution = np.copy(cheapest_neighbour)
                tabu_list.append(current_solution)
                print('new best found = ' + str(current_cost))
                print('best ever found = '+str(best_cost))
                if current_cost <= best_cost:
                    best_cost, best_solution = current_cost, np.copy(current_solution)
      
                break
        
            elif not_in_tabu: #If not cheaper but not in tabu then accept and add to tabu list. If its in tabu list and not cheaper then continue with the next
                #neighbou
                current_cost = cheapest_neighbour_cost
                current_solution = np.copy(cheapest_neighbour)
                tabu_list.append(current_solution)
                print('new best found = ' + str(current_cost))
                print('best ever found = '+str(best_cost))
                break
            else:   
                #print('Local optimum found, Z = ' + str(current_cost))
                local_opt = True
                #tabu_list.append(current_solution)
                COSTS1.append(best_cost)
                COSTS2.append(current_cost)
            
        if len(tabu_list) > tabu_list_max_len: #Clear tabu list first in first out if its full
            tabu_list.pop(-1)
            print('Tabu list is full')

    elif (heuristic == 'variable_neighbourhood_search'): 
        cost_vector = []

        for neighbour in y_neighbours:
            cost = transportproblem(neighbour, current_solution, current_cost)[0]
            cost_vector.append(cost)
        
        sorted_index_vector = np.argsort(cost_vector)
        index_of_cheapest_neighbour = sorted_index_vector[0]
        cheapest_neighbour_cost = cost_vector[index_of_cheapest_neighbour]
        cheapest_neighbour = y_neighbours[index_of_cheapest_neighbour]

        if cheapest_neighbour_cost < current_cost:
            current_cost = cheapest_neighbour_cost
            current_solution = np.copy(cheapest_neighbour)
            best_cost, best_solution = current_cost, np.copy(current_solution)
            print('new best found = ' + str(current_cost))
        else:
            print('Local optimum found, Z = ' + str(current_cost)) #If no better solution can be found swap neighbourhood
            local_opt = True
        COSTS1.append(current_cost)

    return current_cost, current_solution, local_opt, best_cost, best_solution, T, COSTS1, COSTS2, tabu_list, tabu_list_max_len, neighbourhood
