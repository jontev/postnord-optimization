

import gurobipy as gp
from gurobipy import GRB

import numpy as np
import pandas as pd

from generate_neighbour import *
from generate_solution import *

# Parameters and data
y = generate_random_solution()
indicies_of_placed_vehicles, = np.where(y!=0) 

NUMBER_OF_PORTS = 40
NUMBER_OF_TIMES = 2
NUMBER_OF_VEHICLES = 2
NUMBER_OF_ORDERS = 36
NUMBER_OF_ZONES = 9
I = list(range(NUMBER_OF_ZONES))
P = list(range(NUMBER_OF_PORTS))
J = list(range(NUMBER_OF_ORDERS))
T = list(range(NUMBER_OF_TIMES))
order_step_length = NUMBER_OF_PORTS*NUMBER_OF_VEHICLES*NUMBER_OF_TIMES
time_step_length = NUMBER_OF_PORTS*NUMBER_OF_VEHICLES
vehicle_step_length = NUMBER_OF_PORTS
Kl = 18
Ks = 30

d = pd.read_csv("dij.csv")
#d = d.append(pd.Series(0, index=d.columns), ignore_index=True)
a = pd.read_csv("aip.csv")
a = a.T # Transpose the "a" matrix
   
def check_if_vehicle(p,j,t,v):
    temp_idx = j*order_step_length + t*time_step_length + \
               v*vehicle_step_length + p
    return temp_idx in indicies_of_placed_vehicles

    
model = gp.Model()

# Variabaldefinitioner
x = model.addVars(I, P, J, vtype=GRB.CONTINUOUS, name="x", lb = 0)

# Målfunktion

obj = sum(a.iloc[i,p]*x[i,p,j] for p in P for i in I for j in J)

# Bivillkor
Demand = model.addConstrs(sum( x[i,p,j] for p in P) == d.iloc[i,j] for i in I for j in J )
Supply = model.addConstrs(sum( x[i,p,j] for i in I) <= \
                     sum(Kl*check_if_vehicle(p,j,t,0)+ \
                     Ks*check_if_vehicle(p,j,t,1) for t in T) for p in P for j in J )

# Min-problem
model.setObjective(obj, GRB.MINIMIZE)
# tidsgräns
#model.Params.TimeLimit = 300
model.update()
# anropar lösare
model.optimize()
# optimalt målfunktionsvärde
model.objVal
# optimala lösning (variabler)
model.printAttr('x')

