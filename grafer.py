#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  9 19:12:16 2022

@author: jonvi252
"""

#                      0.0         146.0     300.0     600.0     900.0
#(meter) \\\\\ (s)                                                    
#swap_port, lok1    192004.6  12870675.0  115830.9  110187.3  109935.8
#swap_port, lok2    186020.7    130721.3  119859.8  111818.5  111181.0
#VNS1               188704.8    126721.8  114053.6  109276.4  108601.4
#VNS2               181672.7    128669.8  116862.0  109346.3  107347.3
#SimAnn1            195944.0    122946.9  113891.6  109462.1  107974.5
#SimAnn2            196371.9    123210.1  113434.8  108677.3  107915.1
#tabu1              187181.1    128216.0   11307.0  112627.2  110421.1
#tabu2              185770.6    125415.0  116266.7  112201.1  110821.4
#gurobi             105111.8    105111.8  105111.8  105111.8  105111.8
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.pyplot import figure

sns.set_theme()

figure(figsize=(12, 12))
#plt.plot(df.columns, df.iloc[0,:], label= "swap port, lokalsökning 1" )
plt.plot(df.columns, df.iloc[1,:], label="swap port, lokalsökning 2")
#plt.plot(df.columns, df.iloc[2,:], label="VNS 1")
plt.plot(df.columns, df.iloc[3,:],label="VNS 2")
#plt.plot(df.columns, df.iloc[4,:],label="Sim anneal 1")
plt.plot(df.columns, df.iloc[5,:], label="Sim anneal 2")
#plt.plot(df.columns, df.iloc[6,:], label="Tabu 1")
plt.plot(df.columns, df.iloc[7,:], label ="Tabu 2")
plt.plot(df.columns, df.iloc[8,:], "--", label="Gurobi")





plt.legend(fontsize=18)
plt.title('Andra körningen', fontsize=18)

extraticks=[df.iloc[8,0]]


plt.yticks(list(plt.yticks()[0]) + extraticks)

plt.xlabel('[Sekunder]')
plt.ylabel("[meter]")


#plt.annotate(
#    '30.2',
#    xy=(3, y),
#    xycoords='data',
#    xytext=(3, y - 5),
#    textcoords='data',
#    horizontalalignment='center',
#    arrowprops=dict(facecolor='black', arrowstyle="->")
#)
plt.annotate("Gurobi optimum (146 sek)",  (df.columns[1], df.iloc[8,1]), xytext= (df.columns[1]-150, df.iloc[8,1]+7000), 
 arrowprops = dict(facecolor='red',
                        connectionstyle="angle3,angleA=0,angleB=-90"))
plt.annotate("10min (extrakrav)",  (df.columns[3], df.iloc[6,3]), xytext= (df.columns[3]-150, df.iloc[6,3]+7000), 
 arrowprops = dict(facecolor='red',
                        connectionstyle="angle3,angleA=0,angleB=-90"))
plt.annotate("VNS bäst",  (df.columns[-1], df.iloc[4,-1]), xytext= (df.columns[-1]-150, df.iloc[4,-1]+7000), 
 arrowprops = dict(facecolor='red',
                        connectionstyle="angle3,angleA=0,angleB=-90"))
plt.annotate("Simulated annealing bäst",  (df.columns[3], df.iloc[4,3]), xytext= (df.columns[3]-150, df.iloc[4,3]-8000), 
 arrowprops = dict(facecolor='red',
                        connectionstyle="angle3,angleA=0,angleB=-90"))
plt.annotate("Simulated annealing bäst",  (df.columns[1], df.iloc[4,1]), xytext= (df.columns[1]-300, df.iloc[4,1]-1000), 
 arrowprops = dict(facecolor='red',
                        connectionstyle="angle3,angleA=0,angleB=-90"))
plt.show()
