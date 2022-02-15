import numpy as np
from data_handling import calculate_dij_mj
import pandas as pd

K_LASTBIL = 18
K_SLAPVAGN = 30
TOTAL_CAPACITY = K_LASTBIL + K_SLAPVAGN


#-------------------------------Booking Problem--------------------------------

def calculate_carriages(degree_of_filling=0.8, date='2021-03-16'):
    
    d_ij, m_j = calculate_dij_mj(degree_of_filling, date)
    d_j = np.sum(d_ij, axis=0) 
    n = len(d_j)
    L_j = [0] * n
    S_j = [0] * n
    
    for j in range(n):
        if d_j[j] <= K_LASTBIL:
            L_j[j] = 1
        elif d_j[j] <= K_SLAPVAGN:
            S_j[j] = 1
        elif d_j[j] > K_SLAPVAGN and d_j[j] <= TOTAL_CAPACITY:
            S_j[j] = 1
            L_j[j] = 1
        elif d_j[j] > TOTAL_CAPACITY:
            print("this order contains too many packages to fit in one carriage")
            
    S_j = np.array(S_j)
    L_j = np.array(L_j)
     
    df_Sj = pd.DataFrame(S_j)
    df_Lj = pd.DataFrame(L_j)
    df_mj = pd.DataFrame(m_j)
    df_dij = pd.DataFrame(d_ij)
    df_Sj.to_csv("Portplanering/Sj.csv", index=False)
    df_Lj.to_csv("Portplanering/Lj.csv", index=False)
    df_mj.to_csv("Portplanering/mj.csv", index=False)
    df_dij.to_csv("Portplanering/dij.csv", index=False)

#------------------------------------------------------------------------------
