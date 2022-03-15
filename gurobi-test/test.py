import gurobipy as gp

from gurobipy import GRB
import pandas as pd
import os


S = pd.read_csv('Sj.csv')
L = pd.read_csv('Lj.csv')
m = pd.read_csv('mj.csv')
dij = pd.read_csv('dij.csv')
aip = pd.read_csv('aip.csv')
S = S.to_numpy()
L = L.to_numpy()
m = m.to_numpy()
dij = dij.to_numpy()
aip = aip.to_numpy()

P = list(range(40))
I = list(range(9))
J = list(range(dij.shape[1]))
T = list(range(2))

aip = aip.T

Kl = 18
Ks = 30

m = [m[j][0] + 1 for j in J]
S = [S[j][0] for j in J]
L = [L[j][0] for j in J]

# create model instance
model = gp.Model()

# define variables in optimization problem
x = model.addVars(I, P, J, vtype=GRB.INTEGER, name="x", lb = 0)
yl = model.addVars(P, J, T, vtype=GRB.BINARY, name="yl")
ys = model.addVars(P, J, T, vtype=GRB.BINARY, name="ys")
u = model.addVars(J, T, vtype=GRB.BINARY, name="u")
w = model.addVars(P, J, vtype=GRB.BINARY, name="w")

# Objective function

obj = sum(aip[i,p]*x[i,p,j] for p in P for i in I for j in J)

# Constraints
A = model.addConstrs(sum( yl[p,j,t] + ys[p,j,t] for j in J) <= 1 for p in P for t in T ) 
B = model.addConstrs(sum( x[i,p,j] for p in P) == dij[i,j] for i in I for j in J )
C = model.addConstrs(sum( yl[p,j,t] for p in P) <= u[j,t]*L[j] for j in J for t in T)
D = model.addConstrs(sum( ys[p,j,t] for p in P) <= u[j,t]*S[j] for j in J for t in T)
E = model.addConstrs(sum( x[i,p,j] for i in I) <= sum(Kl*yl[p,j,t] + Ks*ys[p,j,t] for t in T) for p in P for j in J )
F = model.addConstrs(sum( u[j,t] for t in T) == 1 for j in J )
G = model.addConstrs(sum( (t+1)*u[j,t] for t in T) <= m[j] for j in J )
H = model.addConstrs(sum( w[p,j] for p in P ) <= 1 for j in J )
Q = model.addConstrs(w[p,j]*dij[0,j] == x[0,p,j] for p in P for j in J )
R = model.addConstrs(sum( x[friplock,p,j] for p in P[20:] ) == 0 for j in J)  
AA = model.addConstrs(sum( x[helpall, p, j] for p in P[0:19]) == 0 for j in J )

# Min-problem
model.setObjective(obj, GRB.MINIMIZE)
# time limit
#model.Params.TimeLimit = 300
model.update()
# call for solver
model.optimize()
# optimal objective value
model.objVal
# optimal solution (variables)
model.printAttr('x')
