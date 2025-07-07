# -----------------------------------------------------------------
# 1) Génération de jobs aléatoires
# -----------------------------------------------------------------
import random
import math
import gurobipy as gp
from gurobipy import GRB
import itertools
import pandas as pd
import plotly.express as px
import time
import input
jobs = {}
machines = ['M1', 'M2', 'M3']
num_jobs = 50  # Reduced for testing
for i in range(1, num_jobs + 1):
    machine_order = machines.copy()
    random.shuffle(machine_order)
    tasks = []
    for machine in machine_order:
        task = {
            'Ws': machine,
            'Pt': random.randint(1, 6)
        }
        tasks.append(task)
    jobs[f'J{i}'] = tasks
jobs=input.jobs

print(jobs)
print("Jobs générés:")
for job_id, tasks in jobs.items():
    print(f"{job_id}: {tasks}")
print("\n--- Fin de la génération des jobs ---\n")
 
# -----------------------------------------------------------------
# 2) Paramètres du problème
# -----------------------------------------------------------------
operators = ['K1', 'K2', 'K3']
T = 48  # Adjusted time horizon
speed = {
    'K1': {'M1': 1.2, 'M2': 1.0, 'M3': 0.8},
    'K2': {'M1': 1.0, 'M2': 1.5, 'M3': 1.0},
    'K3': {'M1': 0.9, 'M2': 0.9, 'M3': 1.2}
}
 
# -----------------------------------------------------------------
# 3) Pré-calcul du temps effectif
# -----------------------------------------------------------------
myProcTime = {}
for j in jobs:
    for o, op_data in enumerate(jobs[j]):
        machine = op_data['Ws']
        pt = op_data['Pt']
        for k in operators:
            myProcTime[(j, o, k)] = math.ceil(pt / speed[k][machine])
 
# -----------------------------------------------------------------
# 4) Création du modèle Gurobi
# -----------------------------------------------------------------
model = gp.Model("JobShopScheduling")
model.setParam('MIPGap', 0.02)
model.setParam("Threads", 30)
# -----------------------------------------------------------------
# 5) Variables de décision
# -----------------------------------------------------------------
S = model.addVars([(j, o) for j in jobs for o in range(len(jobs[j]))], vtype=GRB.INTEGER, name="S")
C = model.addVars([(j, o) for j in jobs for o in range(len(jobs[j]))], vtype=GRB.INTEGER, name="C")
x = model.addVars(operators, machines, vtype=GRB.BINARY, name="x")
y = model.addVars(jobs.keys(), vtype=GRB.BINARY, name="y")
Cmax = model.addVar(lb=0, vtype=GRB.INTEGER, name="Cmax")
BigM = T * 2
 
# -----------------------------------------------------------------
# 6) Contraintes (corrected)
# -----------------------------------------------------------------
# 6.1 Affectation opérateurs -> machines
model.addConstrs((x.sum('*', m) == 1 for m in machines), "MachineOperator")
model.addConstrs((x.sum(k, '*') <= 1 for k in operators), "OperatorLimit")
 
# 6.2 Lien entre S, C et temps effectif
for j in jobs:
    for o in range(len(jobs[j])):
        machine = jobs[j][o]['Ws']
        expr_time = gp.quicksum(myProcTime[(j, o, k)] * x[k, machine] for k in operators)
        model.addConstr(C[j, o] == S[j, o] + expr_time, f"process_{j}_{o}")
 
# 6.3 Activation du job
for j in jobs:
    for o in range(len(jobs[j])):
        model.addConstr(S[j, o] <= T * y[j], f"start_act_{j}_{o}")
        model.addConstr(C[j, o] <= T * y[j], f"comp_act_{j}_{o}")
 
# 6.4 Précédence des opérations
for j in jobs:
    for o in range(len(jobs[j]) - 1):
        model.addConstr(S[j, o+1] >= C[j, o] - BigM * (1 - y[j]), f"precedence_{j}_{o}")
 
# 6.5 Contraintes disjonctives
machine_ops = {m: [] for m in machines}
for j in jobs:
    for o in range(len(jobs[j])):
        machine_ops[jobs[j][o]['Ws']].append((j, o))
 
for m in machines:
    ops = machine_ops[m]
    for (j1, o1), (j2, o2) in itertools.combinations(ops, 2):
        z = model.addVar(vtype=GRB.BINARY, name=f"z_{j1}_{o1}_{j2}_{o2}")
        model.addConstr(S[j1, o1] >= C[j2, o2] - BigM*(1 - z) - BigM*(2 - y[j1] - y[j2]))
        model.addConstr(S[j2, o2] >= C[j1, o1] - BigM*z - BigM*(2 - y[j1] - y[j2]))
 
# 6.6 Délai final
for j in jobs:
    last_op = len(jobs[j]) - 1
    model.addConstr(C[j, last_op] <= T, f"deadline_{j}")
 
# 6.7 Liaison avec Cmax
for j in jobs:
    last_op = len(jobs[j]) - 1
    model.addConstr(Cmax >= C[j, last_op] - BigM * (1 - y[j]), f"Cmax_{j}")
 
# -----------------------------------------------------------------
# 7) Fonction Objectif
# -----------------------------------------------------------------
model.setObjective(10000 * gp.quicksum(y[j] for j in jobs) - Cmax, GRB.MAXIMIZE)
 
# -----------------------------------------------------------------
# 8) Résolution
# -----------------------------------------------------------------
model.optimize()
 
# -----------------------------------------------------------------
# 9) Extraction du planning
# -----------------------------------------------------------------
gantt_data = []
if model.status == GRB.OPTIMAL:
    for m in machines:
        assigned_op = next((k for k in operators if x[k, m].X > 0.5), None)
        machine_label = f"{m} ({assigned_op})" if assigned_op else m
        for (j, o) in machine_ops[m]:
            if y[j].X > 0.5:
                start_t = S[j, o].X
                end_t = C[j, o].X
                if end_t > start_t:
                    gantt_data.append({
                        'Job': j,
                        'Operation': f"Op{o}",
                        'Ws': machine_label,
                        'Start': start_t,
                        'Finish': end_t
                    })
 
# -----------------------------------------------------------------
# 10) Diagramme de Gantt corrigé
# -----------------------------------------------------------------
if gantt_data:
       
       # Converting to individual task variables
       Tâches    = [item['Job'] for item in gantt_data]         # Task names taken from 'Job'
       d         = [item['Start'] for item in gantt_data]         # Starting times
       f         = [item['Finish'] for item in gantt_data]        # Finishing times
       Ressource = [item['Ws'] for item in gantt_data]            # Resources (workstations)
       pt        = [item['Finish'] - item['Start'] for item in gantt_data]  # Duration for each task
       title     = "Test Bar Timeline"
 
       # Build the list of dictionaries
       data_list = []
       for t, start, end, res, time in zip(Tâches, d, f, Ressource, pt):
              data_list.append({
                     "Tâches": t,
                     "Début": start,
                     "Fin": end,
                     "Ressource": res,
                     "Aj": start,  # Using the start as the base position for the bar
                     "Pt": time,
                     "Cj": end,    # This could be used for further customization if needed
                     "Time": time
              })
 
       # Create DataFrame
       df = pd.DataFrame(data_list)
 
       # Create a horizontal bar chart
       fig = px.bar(
       df,
       base="Aj",        # Base start value for each bar
       x="Time",         # Width of the bar
       y="Ressource",    # Categories on the y-axis
       text="Tâches",    # Task names displayed on the bars
       color="Tâches",   # Color bars based on tasks
       orientation='h',  # Horizontal orientation
       title=title
       )
 
       # Reverse the y-axis to have the first task at the top
       fig.update_yaxes(autorange="reversed")
       # fig.show()
       # Convert the Plotly figure to an HTML string (without full HTML wrapper)
       plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
 
       # Create an HTML document with a larger, centered refresh button
       html_content = f"""
       <html>
       <head>
       <title>{title}</title>
       <meta charset="UTF-8">
       <style>
              .refresh-button {{
              display: block;
              margin: 20px auto;
              padding: 15px 30px;
              font-size: 20px;
              cursor: pointer;
              }}
       </style>
       </head>
       <body>
       <!-- Refresh button to reload the page -->
       <button class="refresh-button" onclick="window.location.reload();">
              Refresh Page
       </button>
       {plot_html}
       </body>
       </html>
       """
 
       # Write the HTML content to a file
       with open("gantt_chart.html", "w", encoding="utf-8") as file:
              file.write(html_content)
 
       print("HTML file 'gantt_chart.html' has been created.")
 
else:
    print("No operations to plot.")
 
# -----------------------------------------------------------------
# 11) Résultats
# -----------------------------------------------------------------
if model.status == GRB.OPTIMAL:
    print(f"\nJobs réalisés: {sum(y[j].X for j in jobs)}/{num_jobs}")
    print("\nAssignations opérateurs-machines:")
    for m in machines:
        for k in operators:
            if x[k, m].X > 0.5:
                print(f"{m} → {k}")
    print(f"\nMakespan (Cmax): {Cmax.X} minutes")
else:
    print("No optimal solution found")
 
 
 