# Jobs with their operations (machine, processing_time)
jobs = {
    'J1': [
        {'machine': 'M1', 'processing_time': 20},
        {'machine': 'M3', 'processing_time': 37},
        {'machine': 'M2', 'processing_time': 25}
    ],
    'J50': [
        {'machine': 'M1', 'processing_time': 1},
        {'machine': 'M3', 'processing_time': 1},
        {'machine': 'M2', 'processing_time': 1}
    ],
    'J2': [
        {'machine': 'M2', 'processing_time': 15},
        {'machine': 'M1', 'processing_time': 4}
    ],'J3': [
        {'machine': 'M2', 'processing_time': 11},
        {'machine': 'M3', 'processing_time': 30},
        {'machine': 'M3', 'processing_time': 25}
    ],
    'J4': [
        {'machine': 'M3', 'processing_time': 5},
        {'machine': 'M1', 'processing_time': 30},
        {'machine': 'M2', 'processing_time': 4}
    ],
    'J5': [
        {'machine': 'M1', 'processing_time': 6},
        {'machine': 'M3', 'processing_time': 30},
        {'machine': 'M2', 'processing_time': 7}
    ],
    'J6': [
        {'machine': 'M1', 'processing_time': 9},
        {'machine': 'M3', 'processing_time': 30},
        {'machine': 'M2', 'processing_time': 9}
    ],
    'J7': [
        {'machine': 'M1', 'processing_time': 20},
        {'machine': 'M3', 'processing_time': 30},
        {'machine': 'M2', 'processing_time': 25}
    ],
    'J8': [
        {'machine': 'M2', 'processing_time': 20},
        {'machine': 'M3', 'processing_time': 30},
        {'machine': 'M1', 'processing_time': 25}
    ],
    'J9': [
        {'machine': 'M1', 'processing_time': 20},
        {'machine': 'M2', 'processing_time': 30},
        {'machine': 'M3', 'processing_time': 25}
    ],
    'J10': [
        {'machine': 'M1', 'processing_time': 20},
        {'machine': 'M3', 'processing_time': 30},
        {'machine': 'M2', 'processing_time': 25}
    ],
        'J11': [
        {'machine': 'M1', 'processing_time': 20},
        {'machine': 'M3', 'processing_time': 30},
        {'machine': 'M2', 'processing_time': 25}
    ],
    'J12': [
        {'machine': 'M2', 'processing_time': 15},
        {'machine': 'M1', 'processing_time': 25}
    ],'J13': [
        {'machine': 'M3', 'processing_time': 20},
        {'machine': 'M1', 'processing_time': 30},
        {'machine': 'M2', 'processing_time': 25}
    ],
    'J14': [
        {'machine': 'M1', 'processing_time': 20},
        {'machine': 'M3', 'processing_time': 30},
        {'machine': 'M2', 'processing_time': 25}
    ],
    'J15': [
        {'machine': 'M2', 'processing_time': 20},
        {'machine': 'M1', 'processing_time': 30},
        {'machine': 'M3', 'processing_time': 25}
    ],
    'J16': [
        {'machine': 'M1', 'processing_time': 20},
        {'machine': 'M3', 'processing_time': 30},
        {'machine': 'M2', 'processing_time': 25}
    ],
    'J17': [
        {'machine': 'M1', 'processing_time': 20},
        {'machine': 'M3', 'processing_time': 10},
        {'machine': 'M2', 'processing_time': 25}
    ],
    'J18': [
        {'machine': 'M1', 'processing_time': 20},
        {'machine': 'M3', 'processing_time': 20},
        {'machine': 'M2', 'processing_time': 25}
    ],
    'J19': [
        {'machine': 'M2', 'processing_time': 20},
        {'machine': 'M1', 'processing_time': 15},
        {'machine': 'M3', 'processing_time': 25}
    ],
    'J20': [
        {'machine': 'M1', 'processing_time': 20},
        {'machine': 'M3', 'processing_time': 30},
        {'machine': 'M2', 'processing_time': 25}
    ],
        'J21': [
        {'machine': 'M1', 'processing_time': 20},
        {'machine': 'M3', 'processing_time': 30},
        {'machine': 'M2', 'processing_time': 25}
    ],
    'J22': [
        {'machine': 'M2', 'processing_time': 15},
        {'machine': 'M1', 'processing_time': 25}
    ],'J23': [
        {'machine': 'M3', 'processing_time': 20},
        {'machine': 'M1', 'processing_time': 30},
        {'machine': 'M2', 'processing_time': 25}
    ],
    'J24': [
        {'machine': 'M1', 'processing_time': 20},
        {'machine': 'M3', 'processing_time': 30},
        {'machine': 'M2', 'processing_time': 25}
    ],
    'J25': [
        {'machine': 'M2', 'processing_time': 20},
        {'machine': 'M1', 'processing_time': 30},
        {'machine': 'M3', 'processing_time': 25}
    ],
    'J26': [
        {'machine': 'M1', 'processing_time': 20},
        {'machine': 'M3', 'processing_time': 30},
        {'machine': 'M2', 'processing_time': 25}
    ],
    'J27': [
        {'machine': 'M1', 'processing_time': 20},
        {'machine': 'M3', 'processing_time': 10},
        {'machine': 'M2', 'processing_time': 25}
    ],
    'J28': [
        {'machine': 'M1', 'processing_time': 20},
        {'machine': 'M3', 'processing_time': 20},
        {'machine': 'M2', 'processing_time': 25}
    ],
    'J29': [
        {'machine': 'M2', 'processing_time': 20},
        {'machine': 'M1', 'processing_time': 15},
        {'machine': 'M3', 'processing_time': 25}
    ]
}
 
import gurobipy as gp
from gurobipy import GRB
import itertools
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
 
# Sample Data
machines = ['M1', 'M2', 'M3']
operators = ['K1', 'K2', 'K3']
T = 70  # 8 hours in minutes
 
speed = {
    'K1': {'M1': 1.2, 'M2': 1.0, 'M3': 0.8},
    'K2': {'M1': 1.0, 'M2': 1.5, 'M3': 1.0},
    'K3': {'M1': 0.9, 'M2': 0.9, 'M3': 1.2}
}
 

model = gp.Model("JobShopScheduling")
 
# Decision Variables
x = model.addVars(operators, machines, vtype=GRB.BINARY, name="x")
y = model.addVars(jobs.keys(), vtype=GRB.BINARY, name="y")
S = {}
C = {}
 
for job in jobs:
    for op_idx in range(len(jobs[job])):
        S[(job, op_idx)] = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name=f"S_{job}_{op_idx}")
        C[(job, op_idx)] = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name=f"C_{job}_{op_idx}")
        # S[(job, op_idx)] = model.addVar(lb=0, vtype=GRB.INTEGER, name=f"S_{job}_{op_idx}")
        # C[(job, op_idx)] = model.addVar(lb=0, vtype=GRB.INTEGER, name=f"C_{job}_{op_idx}")
 
BigM = T * 20
 
# 1. Operator assignment
model.addConstrs((x.sum('*', m) == 1 for m in machines), "MachineOperator")
model.addConstrs((x.sum(k, '*') <= 1 for k in operators), "OperatorLimit")
 
# 2. Operation activation constraints
for job in jobs:
    for op_idx in range(len(jobs[job])):
        # Link start/end times to job completion
        model.addConstr(S[job, op_idx] <= T * y[job], f"Activate_S_{job}_{op_idx}")
        model.addConstr(C[job, op_idx] <= T * y[job], f"Activate_C_{job}_{op_idx}")
 
# 3. Processing time calculation with Big-M
for job in jobs:
    for op_idx in range(len(jobs[job])):
        machine = jobs[job][op_idx]['machine']
        pt = jobs[job][op_idx]['processing_time']
        expr = gp.quicksum((pt / speed[k][machine]) * x[k, machine] for k in operators)
        model.addConstr(
            C[job, op_idx] >= S[job, op_idx] + expr - BigM * (1 - y[job]),
            f"Process_LB_{job}_{op_idx}"
        )
        model.addConstr(
            C[job, op_idx] <= S[job, op_idx] + expr + BigM * (1 - y[job]),
            f"Process_UB_{job}_{op_idx}"
        )
 
# 4. Operation precedence (only for activated jobs)
for job in jobs:
    for op_idx in range(len(jobs[job]) - 1):
        model.addConstr(
            S[job, op_idx + 1] >= C[job, op_idx] - BigM * (1 - y[job]),
            f"Precedence_{job}_{op_idx}"
        )
 
# 5. Machine disjunctive constraints (only between active jobs)
machine_operations = {m: [] for m in machines}
for job in jobs:
    for op_idx in range(len(jobs[job])):
        machine = jobs[job][op_idx]['machine']
        machine_operations[machine].append((job, op_idx))
 
for m in machines:
    ops = machine_operations[m]
    for (j1, o1), (j2, o2) in itertools.combinations(ops, 2):
        z = model.addVar(vtype=GRB.BINARY, name=f"z_{j1}_{o1}_{j2}_{o2}")
        # Only enforce if both jobs are selected
        model.addConstr(
            S[j1, o1] >= C[j2, o2] - BigM * (1 - z) - BigM * (2 - y[j1] - y[j2]),
            f"Disj1_{j1}_{o1}_{j2}_{o2}"
        )
        model.addConstr(
            S[j2, o2] >= C[j1, o1] - BigM * z - BigM * (2 - y[j1] - y[j2]),
            f"Disj2_{j1}_{o1}_{j2}_{o2}"
        )
 
model.setObjective(y.sum(), GRB.MAXIMIZE)
model.optimize()
 
def plot_gantt(gantt_data):
    if not gantt_data:
        print("No operations to plot")
        return
    fig, ax = plt.subplots(figsize=(12, 6))
    # Get unique jobs and machines
    jobs = list(set(entry['Job'] for entry in gantt_data))
    machines = list(set(entry['Machine'] for entry in gantt_data))
    # Sort machines by their numeric value
    machines.sort(key=lambda x: int(x.split()[0][1:]))
    # Create color mapping
    import numpy as np
    from matplotlib.colors import ListedColormap
 
    # Combine tab20, tab20b, tab20c color lists (each has 20 distinct colors)
    all_tab_colors = np.vstack([
        plt.cm.tab20.colors,
        plt.cm.tab20b.colors,
        plt.cm.tab20c.colors
    ])
 
    # If you just need 40, slice the first 40 from the combined 60
    colors_40 = all_tab_colors[:40]
    my_tab40 = ListedColormap(colors_40)
 
    # Then you can do:
    job_color = {job: colors_40[i] for i, job in enumerate(jobs)}
    # Plot each operation
    for entry in gantt_data:
        job = entry['Job']
        start = entry['Start']
        end = entry['Finish']
        duration = end - start
        machine = entry['Machine']
        y_pos = machines.index(machine)
        ax.barh(y_pos, duration, left=start,
                color=job_color[job], edgecolor='black', alpha=0.8)
        # Add text label
        ax.text(start + duration/2, y_pos,
                f"{job}\n{entry['Operation']}",
                va='center', ha='center', color='white')
    # Customize plot
    ax.set_yticks(range(len(machines)))
    ax.set_yticklabels(machines)
    ax.set_xlabel('Time (minutes)')
    ax.set_title('Job Shop Schedule Gantt Chart')
    ax.invert_yaxis()  # Show M1 at the top
    # Create legend
    legend_elements = [Patch(facecolor=job_color[job], label=job) for job in jobs]
    ax.legend(handles=legend_elements, title='Jobs',
             bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()
 
if model.status == GRB.OPTIMAL:
    # Collect data for Gantt chart
    gantt_data = []
    for m in machines:
        # Find assigned operator
        assigned_op = next((k for k in operators if x[k, m].X > 0.5), None)
        if assigned_op:
            machine_label = f"{m} ({assigned_op})"
            # Get operations for this machine
            for (job, op_idx) in machine_operations[m]:
                if y[job].X > 0.5:  # Only plot completed jobs
                    start = S[job, op_idx].X
                    end = C[job, op_idx].X
                    if end - start > 0:  # Only plot actual operations
                        gantt_data.append({
                            'Job': job,
                            'Operation': op_idx,
                            'Machine': machine_label,
                            'Start': start,
                            'Finish': end
                        })
    # Plot Gantt chart
    plot_gantt(gantt_data)
    # Print other results (operator assignments, etc.)
    print(f"\nOptimal solution: {model.objVal} jobs completed")
    print("\nOperator assignments:")
    for m in machines:
        for k in operators:
            if x[k, m].X > 0.5:
                print(f"{m} -> {k}")
else:
    print("No optimal solution found")
    