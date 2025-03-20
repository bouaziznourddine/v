import time, os, random
import math
from math import floor
import numpy as np
import matplotlib.pyplot as plt

# Gurobi for scheduling
import gurobipy as gp
from gurobipy import GRB
import itertools

# Plotly and Pandas for the Gantt chart
import pandas as pd
import plotly.express as px


###################################################
# 9) DYNAMIC OPT FUNCTION
###################################################

def dynamic_opt(self, iteration_num):
    """
    Final version of dynamic re-optimization:
      1) Update real-time speed for each worker-machine pair.
      2) Build a Gurobi model that schedules leftover times.
      3) Write a single HTML Gantt chart with <meta refresh> so you
         can see updates in one browser window.

    self: JobShopSimulation object
    iteration_num: integer identifier for logging
    """

    import math
    import itertools
    import time
    import gurobipy as gp
    from gurobipy import GRB
    import pandas as pd
    import plotly.express as px

    ##############################################
    # 1) Update real-time speeds in self.speed
    ##############################################
    current_tick = self.current_tick  # e.g. from your simulation loop
    workers_list = list(self.workers.keys())  # e.g. ["W1","W2","W3"]
    machines_list = list(self.machines.keys()) # e.g. ["M1","M2","M3"]

    for wName, wObj in self.workers.items():
        # def_vit(tick) returns that worker's real-time speed
        real_speed = wObj.def_vit(current_tick)
        # For simplicity, same speed on each machine, or adapt if your logic is machine-specific
        for mName in machines_list:
            self.speed[wName][mName] = real_speed

    ##############################################
    # 2) Build leftover-times dictionary
    ##############################################
    jobs_dict = {}
    for job_obj in self.jobs:
        if job_obj.finished:
            continue
        partial_ops = []
        for op_index, (machine_name, total_pt) in enumerate(job_obj.routing_sequence):
            elapsed = job_obj.elapsed_time_by_op[op_index]
            remaining = total_pt - elapsed
            if remaining > 0:
                partial_ops.append({'Ws': machine_name, 'Pt': remaining})
        if partial_ops:
            jobs_dict[job_obj.job_name] = partial_ops

    if not jobs_dict:
        print(f"[dynamic_opt {iteration_num}] No unfinished ops – nothing to schedule.")
        return

    ##############################################
    # 3) Gurobi model
    ##############################################
    model = gp.Model("Dynamic_Opt")

    # Time horizon
    T = 400
    BigM = 2 * T

    # Precompute effective times => leftover / speed
    myProcTime = {}
    for jName, ops in jobs_dict.items():
        for o, op_data in enumerate(ops):
            mach = op_data['Ws']
            leftover_pt = op_data['Pt']
            for w in workers_list:
                raw = leftover_pt * self.speed[w][mach]
                myProcTime[(jName, o, w)] = math.ceil(raw)

    # Variables
    S = model.addVars(
        [(jName, o) for jName in jobs_dict for o in range(len(jobs_dict[jName]))],
        vtype=GRB.CONTINUOUS, name="S"
    )
    C = model.addVars(
        [(jName, o) for jName in jobs_dict for o in range(len(jobs_dict[jName]))],
        vtype=GRB.CONTINUOUS, name="C"
    )
    x = model.addVars(workers_list, machines_list, vtype=GRB.BINARY, name="x")
    y = model.addVars(jobs_dict.keys(), vtype=GRB.BINARY, name="y")

    # 3.1 Assign each machine exactly one worker
    model.addConstrs((x.sum('*', m) == 1 for m in machines_list),
                     name="MachineAssignment")
    # 3.2 Each worker can run at most one machine
    model.addConstrs((x.sum(w, '*') <= 1 for w in workers_list),
                     name="WorkerOneMachine")

    # 3.3 Link S, C with effective times
    for jName in jobs_dict:
        for o in range(len(jobs_dict[jName])):
            mach = jobs_dict[jName][o]['Ws']
            expr_time = gp.quicksum(myProcTime[(jName, o, w)] * x[w, mach]
                                    for w in workers_list)
            model.addConstr(
                C[jName, o] >= S[jName, o] + expr_time - BigM*(1 - y[jName]),
                name=f"time_{jName}_{o}"
            )

    # 3.4 Activation constraints
    for jName in jobs_dict:
        for o in range(len(jobs_dict[jName])):
            model.addConstr(S[jName, o] <= T * y[jName])
            model.addConstr(C[jName, o] <= T * y[jName])

    # 3.5 Precedence
    for jName in jobs_dict:
        for o in range(len(jobs_dict[jName]) - 1):
            model.addConstr(
                S[jName, o+1] >= C[jName, o] - BigM*(1 - y[jName])
            )

    # 3.6 Disjunctive constraints
    machine_ops = {m: [] for m in machines_list}
    for jName in jobs_dict:
        for o in range(len(jobs_dict[jName])):
            m = jobs_dict[jName][o]['Ws']
            machine_ops[m].append((jName, o))

    for mm in machines_list:
        ops_list = machine_ops[mm]
        for (j1, o1), (j2, o2) in itertools.combinations(ops_list, 2):
            z = model.addVar(vtype=GRB.BINARY, name=f"z_{j1}_{o1}_{j2}_{o2}")
            model.addConstr(
                S[j1, o1] >= C[j2, o2] - BigM*(1 - z) - BigM*(2 - y[j1] - y[j2])
            )
            model.addConstr(
                S[j2, o2] >= C[j1, o1] - BigM*z - BigM*(2 - y[j1] - y[j2])
            )

    # 3.7 Deadline
    for jName in jobs_dict:
        last_op = len(jobs_dict[jName]) - 1
        model.addConstr(C[jName, last_op] <= T, name=f"deadline_{jName}")

    # Objective: maximize # of completed jobs
    model.setObjective(gp.quicksum(y[jName] for jName in jobs_dict), GRB.MAXIMIZE)

    # Solve
    start_time = time.time()
    model.optimize()
    exec_time = time.time() - start_time

    ##############################################
    # 4) Build a Gantt chart -> single HTML
    ##############################################
    gantt_data = []
    if model.status == GRB.OPTIMAL:
        for mm in machines_list:
            # which worker is assigned?
            assigned_w = None
            for w in workers_list:
                if x[w, mm].X > 0.5:
                    assigned_w = w
                    break
            machine_label = f"{mm} ({assigned_w})" if assigned_w else mm

            for (jName, o) in machine_ops[mm]:
                if y[jName].X > 0.5:
                    st = S[jName, o].X
                    ft = C[jName, o].X
                    if ft > st:
                        gantt_data.append({
                            'Job': jName,
                            'Operation': f"Op{o}",
                            'Machine': machine_label,
                            'Start': st,
                            'Finish': ft
                        })

    if gantt_data:
        df_rows = []
        for item in gantt_data:
            st = item['Start']
            ft = item['Finish']
            df_rows.append({
                'Task':     item['Job'],
                'Resource': item['Machine'],
                'Start':    st,
                'Finish':   ft,
                'Duration': ft - st
            })
        df = pd.DataFrame(df_rows)
        fig = px.bar(
            df,
            base="Start",
            x="Duration",
            y="Resource",
            text="Task",
            color="Task",
            orientation='h',
            title=f"Gantt chart (dynamic_opt {iteration_num})"
        )
        fig.update_yaxes(autorange="reversed")

        # Auto-refresh
        plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
        meta_refresh = "<meta http-equiv='refresh' content='4' />"
        html_content = f"""
        <html>
        <head>
          <title>Gantt chart dynamic_opt {iteration_num}</title>
          {meta_refresh}
          <meta charset="UTF-8">
        </head>
        <body>
          <h2>Dynamic Gantt iteration {iteration_num}</h2>
          {plot_html}
        </body>
        </html>
        """
        with open("gantt_chart.html", "w", encoding="utf-8") as f:
            f.write(html_content)

        print("Updated 'gantt_chart.html' (auto-refresh in 5s).")
    else:
        print("No tasks to plot (maybe no operations scheduled).")

    ##############################################
    # 5) Print results
    ##############################################
    if model.status == GRB.OPTIMAL:
        nb_completed = sum(y[jName].X for jName in jobs_dict)
        print(f"[dynamic_opt {iteration_num}] Completed {nb_completed}/{len(jobs_dict)} jobs.")
        print(f"Gurobi solve time = {exec_time:.2f} sec")
        for mm in machines_list:
            for w in workers_list:
                if x[w, mm].X > 0.5:
                    print(f"   {mm} → {w}")
    else:
        print(f"[dynamic_opt {iteration_num}] No optimal solution found (status={model.status}).")
