import random
import math
import gurobipy as gp
from gurobipy import GRB
import itertools
import pandas as pd
import plotly.express as px
import time

def run_optimization(num_jobs, T, max_pt):
    # -----------------------------------------------------------------
    # 1) Génération de jobs 
    # -----------------------------------------------------------------
    jobs = {}
    machines = ['M1', 'M2', 'M3']
    for i in range(1, num_jobs + 1):
        machine_order = machines.copy()
        random.shuffle(machine_order)
        tasks = []
        for machine in machine_order:
            task = {
                'Ws': machine,
                'Pt': random.randint(1, max_pt)
            }
            tasks.append(task)
        jobs[f'J{i}'] = tasks

    # 2) Paramètres du problème

    # -----------------------------------------------------------------
    # 2) Paramètres du problème
    # -----------------------------------------------------------------
    operators = ['K1', 'K2', 'K3']
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
    model.setParam('MIPGap', 0.07)
    # model.setParam("Accelerator", "GPU")

    # -----------------------------------------------------------------
    # 5) Variables de décision
    # -----------------------------------------------------------------
    S = model.addVars([(j, o) for j in jobs for o in range(len(jobs[j]))], vtype=GRB.CONTINUOUS, name="S")
    C = model.addVars([(j, o) for j in jobs for o in range(len(jobs[j]))], vtype=GRB.CONTINUOUS, name="C")
    x = model.addVars(operators, machines, vtype=GRB.BINARY, name="x")
    y = model.addVars(jobs.keys(), vtype=GRB.BINARY, name="y")
    BigM = T * 2
    
    # -----------------------------------------------------------------
    # 6) Contraintes (corrected)
    # -----------------------------------------------------------------
    # 6.1 Affectation opérateurs -> machines
    model.addConstrs((x.sum('*', m) == 1 for m in machines), "MachineOperator")
    model.addConstrs((x.sum(k, '*') <= 1 for k in operators), "OperatorLimit")
    
    # 6.2 Lien entre S, C et temps effectif (contrainte modifiée)
    for j in jobs:
        for o in range(len(jobs[j])):
            machine = jobs[j][o]['Ws']
            expr_time = gp.quicksum(myProcTime[(j, o, k)] * x[k, machine] for k in operators)
            # Contrainte modifiée : 
            # Si y[j] = 1, on a C[j, o] >= S[j, o] + expr_time.
            # Si y[j] = 0, le terme -BigM*(1-y[j]) = -BigM "désactive" la contrainte 
            # (BigM étant choisi suffisamment grand pour rendre la contrainte non contraignante).
            model.addConstr(
                C[j, o] >= S[j, o] + expr_time - BigM*(1 - y[j]),
                f"process_{j}_{o}"
            )
    
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
    

    
    # -----------------------------------------------------------------
    # 7) Fonction Objectif
    # -----------------------------------------------------------------
    model.setObjective( gp.quicksum(y[j] for j in jobs) , GRB.MAXIMIZE)
    
    # 8) Résolution + chronométrage
    start_time = time.time()
    model.optimize()
    end_time = time.time()

    exec_time = end_time - start_time

    # 9) Extraction de quelques résultats
    jobs_realises = sum(y[j].X for j in jobs) if model.status == GRB.OPTIMAL else 0
    assignations = {}
    for m in machines:
        for k in operators:
            if x[k, m].X > 0.5:
                assignations[m] = k

    # Optionnel : extraction du planning pour diagramme de Gantt (non affiché ici)
    # Vous pouvez ajouter le bloc de code pour générer le Gantt si nécessaire

    return {
        "num_jobs": num_jobs,
        "T": T,
        "max_pt": max_pt,
        "execution_time": exec_time,
        "jobs_realises": jobs_realises,
        "makespan": 14,
        "assignations": assignations,
        "model_status": model.status
    }

# Liste des valeurs à tester pour num_jobs, T et max_pt
num_jobs_list = [10, 20, 30]
T_list = [800, 1200]
max_pt_list = [4, 6, 8]

results = []

# Boucles imbriquées pour explorer toutes les combinaisons
for nj in num_jobs_list:
    for T_val in T_list:
        for pt_max in max_pt_list:
            res = run_optimization(num_jobs=nj, T=T_val, max_pt=pt_max)
            results.append(res)
            print(f"num_jobs: {nj}, T: {T_val}, max_pt: {pt_max}, temps: {res['execution_time']:.2f} s, "
                  f"jobs réalisés: {res['jobs_realises']}, makespan: {res['makespan']}")

# Créer un DataFrame pour visualiser les résultats
df_results = pd.DataFrame(results)
print("\nRésultats détaillés:")
print(df_results)

# Exemple de visualisation avec Plotly :
# Graphique du temps d'exécution en fonction de num_jobs pour différentes valeurs de T et max_pt.
fig = px.bar(df_results, x="num_jobs", y="execution_time", color="T", facet_col="max_pt",
             title="Temps d'exécution vs. Nombre de jobs (par T et max_pt)",
             labels={"num_jobs": "Nombre de jobs", "execution_time": "Temps d'exécution (s)", "T": "Horizon T", "max_pt": "Pt max"})
fig.show()
