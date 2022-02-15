import tkinter as tk
import sys
from tkinter import filedialog
import random
import numpy as np
import pandas as pd
import math
import seaborn as sns

sys.path.append('Portplanering')
sys.path.append('Bilbokning/src')

from bilbokning import calculate_carriages

HEURISTICS = ['local_search',
              'simulated_annealing',
              'variable_neighbourhood_search',
              'tabu_search']
NEIGHBOURHOODS = ['swap_port',
                  'swap_time',
                  'move_port',
                  'move_time']
zone_dict = {
    0: 'TÄLT   ',
    1: 'FRIST  ',
    2: 'MPFTG\t',
    3: 'MPBVV\t',
    4: 'MPJÄR\t',
    5: 'HPALL\t',
    6: 'ADR    ',
    7: 'ENTEB\t',
    8: 'ENTST\t'
}




# Function to change orderfile- Not to be used during testing
def browse_files():
    filename = filedialog.askopenfilename(title = "Select a File",
                                          filetypes = (("Text files",
                                                        "*.csv*"),
                                                       ("all files",
                                                        "*.*")))
    w.configure(text="File Opened: "+filename)

#----------------------------------FUNCTIONS-----------------------------------
# Global variables to be used for prints etc.
global running
global best_cost
global best_solution
global COSTS1
global COSTS2
running = False
# Function when portplanering() is running
def portplanering():
    global running
    global best_cost
    global best_solution
    global COSTS1
    global COSTS2
    COSTS1 = []
    COSTS2 = []
    from heuristic import run_heuristics
    from generate_solution import generate_random_solution
    from transportproblem_pulp import transportproblem
    # Generate a feasible solution
    y = generate_random_solution()
    # Calculate the current cost
    cost = transportproblem(y)[0]
    best_cost = cost
    best_solution = np.copy(y)
    # Initial constans for SA and Tabu search
    temp = 1000
    tabu_list_max_len = 10
    # Initial Tabu list for tabusearch
    tabu_list = []
    # Insert an initial word into the text
    T.insert(tk.END, 10)
    # Set neighbour to the chosen one through gui.
    neighbour = chosen_neighbour.get()
    local_opt = False
    # running == True whenever the search for a heuristic is on
    ctr = 0
    while running:
        ctr += 1
        # Start a heuristic iteration
        cost, y, local_opt, best_cost, best_solution, temp, COSTS1, COSTS2, tabu_list, tabu_list_max_len, neighbour  = \
        run_heuristics(y, cost, chosen_heuristic.get(), neighbour, local_opt, best_cost, best_solution, temp, COSTS1, COSTS2, tabu_list, tabu_list_max_len)
        # Remove the previous output and insert the current cost
        T.delete("1.0", "end")
        T.insert(tk.END, cost)
        # Generate a new random neighbourhood is condition is fulfilled.
        if local_opt:
            neighbour = NEIGHBOURHOODS[random.randrange(2)]
            local_opt = False
        m.update()
        if ctr == 200:
            running == False
            break
def save_pic(cos, colname, filename):
    df = pd.DataFrame([cos])
    df = df.T
    df.columns = colname
    a = sns.lineplot(data=df[0:199])
    figure = a.get_figure()
    figure.savefig(filename+'.pdf')
    figure.savefig(filename+'.png')
    


# function destroys window
def destroy_window():
    m.destroy()

# If both Bilbokning and Portplanering is marked then, bilbokning will run first
# and then run Portplanering after.
def run_program():
    # If Bilbokning is checked, it starts bilbokning
    if bilv.get() == 1:
        date=T.get("1.0", 'end-1c')
        calculate_carriages(slid.get(), date)
        d.configure(text="Date: "+date)
        
    # If Portplanering is checked, it starts portplanering
    if portv.get() == 1:
        global running
        # Sets global vaiable to True, means heuristic is running.
        running = True
        portplanering()

# Stop-button will not stop Bilbokning. Only heuristic search.
def stop_program():
    from transportproblem_pulp import transportproblem
    global running
    global best_solution
    
    if portv.get() == 1:
        running = False
        T.delete("1.0", "end")
        # Calculate the cost of the best_solution found so far.
        cost, x = transportproblem(best_solution)
        # Print it in window and run solution_to_txt
        T.insert(tk.END, 'Best solution found: ' + str(cost))
        solution_to_txt(cost, x)
        
#------------------------------------------------------------------------------


# -------------------------------Window----------------------------------------

# Creates a window with every orders assigned ports
def view_solution():
    L = pd.read_csv('Portplanering/Lj.csv')
    number_of_orders = len(L)
    J = range(number_of_orders)
    import csv
    def showSol():
        top2 = tk.Toplevel()
        with open('solution/'+str(chosen_order_list.get())+'.csv', newline='') as file:
            reader = csv.reader(file)
            r = 0
            for col in reader:
                c = 0
                for row in col:
                    label = tk.Label(top2,
                                     width = 10,
                                     height = 2,
                                     text = row,
                                     relief = tk.RIDGE)
                    label.grid(row = r, column = c)
                    c += 1
                r += 1
    # Define buttons
    top = tk.Toplevel()
    top.title('Solution window')
    chosen_order_list = tk.StringVar(top)
    chosen_order_list.set(J[0])
    op_menu_order = tk.OptionMenu(top, chosen_order_list, *J)
    op_menu_order.pack()
    
    button_open_solution = tk.Button(top,
                                     text='Show solution',
                                     command = showSol)
    button_open_solution.pack()

# function creates a txtfile to view the current output in a textfile
def solution_to_txt(cost, x):
    L = pd.read_csv('Portplanering/Lj.csv')
    S = pd.read_csv('Portplanering/Sj.csv')
    dij = pd.read_csv('Portplanering/dij.csv')
    mj = pd.read_csv('Portplanering/mj.csv')
    a = pd.read_csv('Portplanering/aip.csv')
    a = np.array(a)
    a = a.T
    NUMBER_OF_PORTS = 40
    list_of_vehicles = L+S
    list_of_vehicles = list_of_vehicles.values.tolist()
    list_of_vehicles = [val for sublist in list_of_vehicles for val in sublist]
    number_of_orders = len(L)
    # ------------------
    # Functions for the solution window
    # Sort x so its sorted for i(zone) -> p(port) -> j(order), from the LP-solver PuLP
    x_sorted=[]
    for i in range(9):
        for p in range(40):
            for j in range(number_of_orders):
                this_index = np.where(x == 'x_'+str(i)+'_'+str(p)+'_'+str(j))[0]
                x_sorted.append(int(float(x[this_index][0][1])))
    # Getters for x_index
    def get_zone(x_index):
        return math.floor(x_index/(number_of_orders*NUMBER_OF_PORTS))
    def get_port(x_index):
        return math.floor((x_index % (number_of_orders*NUMBER_OF_PORTS)) / number_of_orders)
    def get_order(x_index):
        return (x_index % (number_of_orders*NUMBER_OF_PORTS)) % number_of_orders
    x_sorted=np.array(x_sorted)
    ny=[]
    x_sorted_index = np.where(x_sorted != 0)[0]
    for i in x_sorted_index:
        ny.append([get_order(i), get_zone(i), get_port(i), x_sorted[i]])
    
    # Creates CSV-files for each order, with port and transportation data.
    for order in range(number_of_orders):
        d = pd.DataFrame(np.zeros((9,0)))
        for i in ny:
            if i[0] == order:
                d.at[i[1],i[2]] = i[3]
        d.to_csv('solution/'+str(order)+'.csv', index=False)
    # --------------------------TO TXT---------------------------
    # Constants 
    ORDER_STEP_LENGTH = 160
    TIME_STEP_LENGTH = 80
    VEHICLE_STEP_LENGTH = 40
    def get_order_yindex(vehicle_index):
        order = math.floor(vehicle_index / ORDER_STEP_LENGTH)
        return order
    def get_time_yindex(vehicle_index):
        time = math.floor((vehicle_index % ORDER_STEP_LENGTH) / TIME_STEP_LENGTH)
        return time
    def get_port_yindex(vehicle_index):
        port = ((vehicle_index % ORDER_STEP_LENGTH) % TIME_STEP_LENGTH) % VEHICLE_STEP_LENGTH
        return port
    def get_vehicle_type_yindex(vehicle_index):
        return math.floor(((vehicle_index % ORDER_STEP_LENGTH) % TIME_STEP_LENGTH) / VEHICLE_STEP_LENGTH)
    # Number of timeslot used for this order
    num_of_times = int(max(np.array(mj)))+1
    # Get y_index
    y_index = np.where(best_solution != 0)[0]
    # y_index split for each timeslot
    y_index_time = [[] for i in range(num_of_times)]
    time_order = [[] for i in range(num_of_times)]
    # time_order contains all the orders at a specific time.
    # y_index_time contains the y_index at a specific time.
    for i in y_index:
        for j in range(num_of_times):
            if get_time_yindex(i) == j:
                y_index_time[j].append(i)
                time_order[j].append(get_order_yindex(i))
    for i in range(len(time_order)):
        time_order[i] = list(set(time_order[i]))
        time_order[i] = [int(x) for x in time_order[i]]
        time_order[i].sort()
    
    # Make cost to real cost:
    cost = 0
    for j in range(number_of_orders):
        for p in range(NUMBER_OF_PORTS):
            for i in range(9):
                cost += a[i,p] * x_sorted[i*NUMBER_OF_PORTS*number_of_orders + p*number_of_orders + j]
                
    # Writes this data to a .txt
    with open('solution.txt', 'w') as file:
        # This 'Datum' has to be set if you create for a certain date
        file.write('------------------------------------------------------------\n')
        file.write('Datum: XXXX-XX-XX       Tidsintervall:  '+str(num_of_times)+'\n')
        file.write('----------------------------------------------------------\n')
        # cost = best_cost found so far
        file.write('Total sträcka: '+str(cost)+'\n')
        file.write('Ordrar\n')
        # Shows on what time slot the orders have been set
        for t in range(num_of_times):
            file.write(str(t)+':   ')
            for i in time_order[t]:
                file.write(str(i)+', ')
            file.write(' \n')
        file.write('------------------------------------------------------------\n\n')
        file.write('------------------------------------------------------------\n')
        file.write('Port\tT = 1\t\t\tT = 2\n')
        # Shows for each port where the orders are set for each timeslot
        for p in range(40):
            first_time='--------'
            second_time='--------'
            for i in y_index_time[0]:
                if get_time_yindex(i)==0 and get_port_yindex(i) == p:
                    if get_vehicle_type_yindex(i) == 0:
                        amount = '(18)'
                    else:
                        amount = '(30)'
                    first_time = str(get_order_yindex(i))+' '+amount
            for i in y_index_time[1]:
                if get_time_yindex(i)==1 and get_port_yindex(i) == p:
                    if get_vehicle_type_yindex(i) == 0:
                        amount = '(18)'
                    else:
                        amount = '(30)'
                    second_time = str(get_order_yindex(i))+' '+amount
            file.write(str(p+1)+'\t'+first_time+'\t\t'+ second_time+'\n')                                    
        
        # Shows for eachtime slot where the orders are set for each port
        for t in range(num_of_times):
            file.write('\n\nTidsintervall: ' + str(t) + '\n')
            file.write('------------------------------------------------------------\n')
            file.write('ORDER\t\t TOT\t BIL+SLÄP\t\t PORT (#PALL)\n')
            order = -1
            for j in y_index_time[t]:
                if order==get_order_yindex(j):
                    port = get_port_yindex(j)
                    num_of_pallets = 0
                    for i in range(9):
                        num_of_pallets += x_sorted[order + number_of_orders*port + i*(40*number_of_orders)]
                    file.write(' & '+str(port+1)+' ('+str(num_of_pallets)+')')
                else:
                    order = get_order_yindex(j)
                    tot = dij.sum(axis=0)[order]
                    fordon = str(L.at[order,'0'])+' + '+str(S.at[order,'0'])
                    port = get_port_yindex(j)
                    num_of_pallets = 0
                    for i in range(9):
                        num_of_pallets += x_sorted[order + number_of_orders * port + i*(40*number_of_orders)]
                    file.write('\n'+str(order)+'\t\t'+str(tot)+'\t\t'+str(fordon)+'\t\t'+str(port+1)+' ('+str(num_of_pallets)+')')
        
        # Creates specific data for each orders.
        for j in range(number_of_orders):
            file.write('\n------------------------------------------------------------\n\n')
            file.write('------------------------------------------------------------\n')
            vehicles =[]
            for j2 in y_index:
                if get_order_yindex(j2) == j:
                    vehicles.append(j2)
            #print(j)
            #print(y_index)            
            file.write('Order\t'+str(j)+' '+'\tTidsintervall:  '+str(get_time_yindex(vehicles[0]))+'\n\n')
            file.write('Bil')
            for v in vehicles:
                if get_vehicle_type_yindex(v) == 0:
                    file.write('\t\t18')
                elif get_vehicle_type_yindex(v) == 1:
                    if len(vehicles) == 2:
                        file.write('\t30')
                    else:
                        file.write('\t\t30')
            file.write('\nPort\t\t')
            for v in vehicles:
                file.write(str(get_port_yindex(v))+'\t')
            file.write('\n------------------------------------------------------------')
            for i in range(9):
                file.write('\n'+zone_dict[i]+'\t')
                for v in vehicles:
                    port = get_port_yindex(v)
                    order = get_order_yindex(v)
                    file.write(str(x_sorted[order + number_of_orders * port + i*(40*number_of_orders)])+'\t')

# ------------------------------------------------------------------------------
# Creates the gui window
m = tk.Tk()
m.geometry('600x400')
m.title('                     xXx Bilbokning | Portplanering xXx')

# Define frames
top_frame = tk.Frame(m)
top_frame.pack(side=tk.TOP)
left_frame = tk.Frame(m)
left_frame.pack(side=tk.LEFT)
right_frame = tk.Frame(m)
right_frame.pack(side=tk.RIGHT)
bottom_frame=tk.Frame(m)
bottom_frame.pack(side=tk.BOTTOM)

w = tk.Label(top_frame, text='No file chosen', font = '100')
d = tk.Label(top_frame, text='No date chosen', font = '100')

#------------------------------------------------------------------------------


#----------------------------------Slider--------------------------------------
#Define a slider to change packing factor, DEFAULT=0.8
slid = tk.Scale(left_frame, from_=0.20, to=1.0, orient=tk.HORIZONTAL, resolution=0.05)
slid.set(0.80)
slid.pack()

#------------------------------------------------------------------------------


#---------------------------Options Meny for heuristics------------------------
# Option menu for heuristcs
chosen_heuristic = tk.StringVar(m)
chosen_heuristic.set(HEURISTICS[0])
opmenu = tk.OptionMenu(right_frame, chosen_heuristic, *HEURISTICS)

# Option menu for starting neighbourhood
chosen_neighbour = tk.StringVar(m)
chosen_neighbour.set(NEIGHBOURHOODS[0])
opmenu_n = tk.OptionMenu(right_frame, chosen_neighbour, *NEIGHBOURHOODS)

#--------------------------------Buttons etc-----------------------------------
bilv=tk.IntVar()
portv=tk.IntVar()
stapling=tk.IntVar()
#Checkbuttons to choose which script should run. Bilbokning or Portplanering
check_bilbokning = tk.Checkbutton(left_frame, text = 'Bilbokning', 
                               variable=bilv,
                               onvalue=1,
                               offvalue=0,
                               height=2,
                               width=15,
                               state=tk.NORMAL)
check_bilbokning.pack(side=tk.TOP)

check_portplanering=tk.Checkbutton(left_frame, text = 'Portplanering',
                                  variable = portv,
                                  onvalue = 1,
                                  offvalue = 0,
                                  height = 2,
                                  width = 15,
                                  state = tk.NORMAL)
check_portplanering.pack(side=tk.BOTTOM)

# A check if stackability should be used
check_staplingsbarhet=tk.Checkbutton(right_frame,text='Staplingsbarhet',
                                       variable=stapling,
                                       onvalue=1,
                                       offvalue=0,
                                       height=2,
                                       width=15,
                                       state=tk.DISABLED)
check_staplingsbarhet.pack(side=tk.TOP)
#if bilv != 1:
#    check_staplingsbarhet.config(state=tk.DISABLED)
#else:
#    check_staplingsbarhet.config(state=tk.NORMAL)

# Pack the option menus
opmenu_n.pack()
opmenu.pack()
# Stop button to stop the heurstic search
button_stop = tk.Button(right_frame,
                        text = 'Stopp',
                        command = stop_program)
button_stop.pack(side=tk.RIGHT)
# Start button to run heurstic or bilbokning
button_run = tk.Button(right_frame,
                       text = 'Kör',
                       command = run_program)
button_run.pack(side=tk.RIGHT)
button_solution = tk.Button(top_frame,
                            text = 'Lösning',
                            command = view_solution)
button_solution.pack()
# Button to exit the window
button_exit = tk.Button(top_frame,
                        text = 'Avsluta',
                        command = destroy_window)
# Button to explore a file
button_explore = tk.Button(top_frame,
                           text = 'Bläddra',
                           command = browse_files)
button_explore.pack(side=tk.TOP)
button_exit.pack(side=tk.TOP)

w.pack()
d.pack()

# Text frame to show the current object value and to enter a valid date to test
T = tk.Text(bottom_frame, height = 1, width = 100)
T.pack()
T.insert(tk.END, '2021-03-16')

#------------------------------------------------------------------------------
# Loop the window
m.mainloop()
