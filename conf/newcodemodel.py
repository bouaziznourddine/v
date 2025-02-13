import gurobipy as gp
from gurobipy import GRB
import numpy as np
import pandas as pd
import plotly.express as px
from datetime import datetime
def planning2(Cjm='',Nfj="",lMtbfm="",lMtfm=""):
        cp=[]
        for rec in lMtbfm:
            cp.append(0)
        plt=[]
        i=0
        for tache in Cjm:
            ws=0
            Tâches="prd_"+str(i+1)
            # Tâches="prd_"+str(Nfj[i][ws])
            # print(Nfj[i][ws])
            for rec in tache:
                if i==0 and ws==0:
                    Début=0
                elif i==0 and ws!=0 :
                    Début=Cjm[0][ws-1]
                elif i!=0 and ws==0 :
                    Début=Cjm[i-1][0]
                else :
                    Début=max(Cjm[i-1][ws],Cjm[i][ws-1])

                v_num=i+1
                Ressource="ws_"+str(ws+1)
                Fin =rec
                v_pt=Fin - Début
                color22=str(v_num)
                if v_num == 0:
                    if v_pt !=0 :plt.append(dict(Tâches=Tâches , Début=Début, Fin= Fin, Ressource=Ressource, Aj=Début,Pt=v_pt,Cj=Fin,Time=v_pt))
                else :
                    if Nfj[i][ws]==0:
                        if v_pt !=0 :plt.append(dict(Tâches=Tâches , Début=Début, Fin= Fin, Ressource=Ressource, Aj=Début,Pt=v_pt,Cj=Fin,Time=v_pt))
                        cp[ws]=0
                    else:
                        d=Début
                        s=v_pt
                        for rec2 in range(int(Nfj[i][ws])):
                            v_num=0
                            color22=str(0)
                            pt=lMtfm[ws]
                            f=d+pt
                            s=s-pt
                            plt.append(dict(Tâches="fau" , Début=d, Fin= f, Ressource=Ressource, Aj=d,Pt=pt,Cj=f,Time=pt))
                            d=f
                            v_num=0
                            color22=str(0)
                            pt=min(lMtbfm[ws],s)
                            cp[ws]=0
                            s=s-pt
                            f=d+pt
                            plt.append(dict(Tâches=Tâches , Début=d, Fin= f, Ressource=Ressource, Aj=d,Pt=pt,Cj=f,Time=pt))
                            d=f
                            # v_num=0
                            # color22=str(0)
                            # pt=lMtfm[ws]
                            # f=d+pt
                            # s=s-pt
                            # plt.append(dict(Tâches="fau" , Début=d, Fin= f, Ressource=Ressource, Aj=d,Pt=pt,Cj=f,Time=pt))
                            # d=f
                        d=f
                        v_num=0
                        color22=str(0)
                        pt=s
                        f=d+pt
                        if pt !=0 :
                            plt.append(dict(Tâches=Tâches , Début=d, Fin= f, Ressource=Ressource, Aj=d,Pt=pt,Cj=f,Time=pt))
                        d=f
                        cp[ws]=s


                
                ws=ws+1
            i=i+1


        df = pd.DataFrame(plt)
        fo=' hjjhjh  '
        
        # fo+="  / La fatigue accumélée : "+str(round(self.fat,2)) 
        # fo+="  La moyenne pondérée: "+str(self.fo)

        title="***   ***              Le planning d'ordonnancement "
        fig = px.bar(df,base = "Aj",x = "Time",y = "Ressource", text="Tâches",color = "Tâches", orientation = 'h', title=title)
        fig.update_yaxes(autorange="reversed")
        fig.show()        
def var2list2d(var,st_var):
        l1 = []
        l2 = []
        s=''
    
        for rec in var.select():
            m=rec.getAttr("VarName").replace(st_var, "").replace("[", "").replace("]", "")
            val=rec.getAttr("x")
            m=m.split(',')
            if s==m[0]:
                l2.append(val)
                
            else:
                if s!='':
                    l1.append(l2)

                s=m[0]
                l2=[]
                l2.append(val)
        l1.append(l2)
        return(l1)
def var2list1d(var,st_var):
        l1=[]
        for rec in var.select():
            l1.append(rec.X)
        return l1
# Data Definitions
CPTP = [3, 94, 85, 43.5, 38, 80]
TAP = [1, 5, 5, 5, 5, 5]

PT = np.array([
    [1, 2, 3],
    [4, 1, 3],
    [2, 2, 3],
    [4, 1, 3],
    [1, 1, 3],
    [3, 4, 3]
])

HV = 999999999

sele = [
    [6, 0, 0, 0, 0, 0],  # Only the first selection is active
]

Mixprods = [
    [1, 1, 1],  # Only the first mix product is active
]

ivtprd = [1, 2, 3]
status = 1
colors = ['0', '1', '2', '3', '4']
mm = 6
dd = 3
kk = 6
pp = 6
jj = 7  # Be cautious with large jj values; consider testing with smaller values first
EOS = 27
impP = [6, 5, 4, 2, 1, 3]
impWS = [2, 6, 4, 5, 1, 3]

Namax = 3
EPTmax = 9
dDATA = TAP  # Assuming dDATA corresponds to TAP
dACWT = CPTP

def print_fo(X, AW, dd, jj, kk, mm, obmin, dMixprod, sin, time_int, iii):
    sy = sum(X[d, j].X for d in range(dd) for j in range(jj))
    l = [sum(X[d, j].X for j in range(jj)) for d in range(dd)]
    l2 = [sum(AW[k, m].X * m for m in range(mm)) for k in range(kk)]
    print("\n")
    a = f" sin {sin} ,dMixprod:{dMixprod} ,sy:{sy} ,l: {l} ,l2 : {l2} , obmin : {obmin} , time_int :{time_int} , iii : {iii}"
    print(a)
    with open("D:\\model_juil\\file.txt", "a") as file:
        file.write("\n" + a)

def modd(dMixprod="", sin="", obmin=1, iii=1):
    start_time = datetime.now()
    # Optimize the model
    model.optimize()
    end_time = datetime.now()
    time_int = (end_time - start_time).total_seconds() / 60  # Time in minutes
    print_fo(X, AW, dd, jj, kk, mm, obmin, dMixprod, sin, time_int, iii)

# Initialize the model
model = gp.Model("OptimizationModel")

# Indices
K = range(kk)    # 0 to kk-1
M = range(mm)    # 0 to mm-1
D = range(dd)    # 0 to dd-1
J = range(jj)    # 0 to jj-1

# Variables
AW = model.addVars(K, M, vtype=GRB.BINARY, name="AW")
X = model.addVars(D, J, vtype=GRB.BINARY, name="X")
APT = model.addVars(J, M, vtype=GRB.INTEGER, name="APT")
NA = model.addVars(J, M, vtype=GRB.INTEGER, name="NA")
EPT = model.addVars(J, M, vtype=GRB.INTEGER, name="EPT")
Cjm = model.addVars(J, M, vtype=GRB.INTEGER, name="Cjm")
Z = model.addVars(J, M, K, vtype=GRB.INTEGER, name="Z")

# Linearization Constraints for Z[j, m, k] = AW[k, m] * NA[j, m]
BIG_M = HV  # A sufficiently large number

for j in J:
    for m in M:
        for k in K:
            model.addConstr(Z[j, m, k] <= NA[j, m], name=f"Z1_{j}_{m}_{k}")
            model.addConstr(Z[j, m, k] <= AW[k, m], name=f"Z2_{j}_{m}_{k}")
            model.addConstr(Z[j, m, k] >= NA[j, m] - BIG_M * (1 - AW[k, m]), name=f"Z3_{j}_{m}_{k}")
            model.addConstr(Z[j, m, k] >= 0, name=f"Z4_{j}_{m}_{k}")

# Constraint 1: sum(AW[k,m] for k in K) == 1 for each m
for m in M:
    model.addConstr(gp.quicksum(AW[k, m] for k in K) == 1, name=f"Sum_AW_m_{m}")

# Constraint 2: sum(AW[k,m] for m in M) <=1 for each k
for k in K:
    model.addConstr(gp.quicksum(AW[k, m] for m in M) <= 1, name=f"Sum_AW_k_{k}")

# Constraint 3: sum(X[d,j] for d in D) <=1 for each j
for j in J:
    model.addConstr(gp.quicksum(X[d, j] for d in D) <= 1, name=f"Sum_X_j_{j}")

# Constraint 4: sum(X[d,j] for d in D) <= sum(X[d,j-1] for d in D) for j in 1..jj-1
for j in range(1, jj):
    model.addConstr(gp.quicksum(X[d, j] for d in D) <= gp.quicksum(X[d, j-1] for d in D), name=f"Monotonic_X_{j}")

# Constraint 5: EPT[0, m] = NA[0, m] * sum(AW[k, m]*dDATA[k] for k in K) + sum(X[d,0]*PT[m,d] for d in D)
for m in M:
    expr = gp.quicksum(dDATA[k] * Z[0, m, k] for k in K) + gp.quicksum(PT[m, d] * X[d, 0] for d in D)
    model.addConstr(EPT[0, m] == expr, name=f"EPT_initial_{m}")

# Constraint 6: EPT[j, m] = (NA[j, m] - NA[j-1, m]) * sum(AW[k, m]*dDATA[k] for k in K) + sum(X[d,j]*PT[m,d] for d in D) for j in 1..jj-1
for j in range(1, jj):
    for m in M:
        expr = gp.quicksum(dDATA[k] * Z[j, m, k] for k in K) - gp.quicksum(dDATA[k] * Z[j-1, m, k] for k in K) + gp.quicksum(PT[m, d] * X[d, j] for d in D)
        model.addConstr(EPT[j, m] == expr, name=f"EPT_{j}_{m}")

# Constraint 7: APT[0, m] = sum(X[d,0]*PT[m,d] for d in D)
for m in M:
    expr = gp.quicksum(PT[m, d] * X[d, 0] for d in D)
    model.addConstr(APT[0, m] == expr, name=f"APT_initial_{m}")

# Constraint 8: APT[j, m] = APT[j-1, m] + sum(X[d,j]*PT[m,d] for d in D) for j in 1..jj-1
for j in range(1, jj):
    for m in M:
        expr = APT[j-1, m] + gp.quicksum(PT[m, d] * X[d, j] for d in D)
        model.addConstr(APT[j, m] == expr, name=f"APT_{j}_{m}")

# Constraint 9: (NA[j,m] +1) * sum(AW[k,m]*dACWT[k] for k in K) >= APT[j,m] for all j, m
for j in J:
    for m in M:
        sum_AW_dACWT = gp.quicksum(dACWT[k] * AW[k, m] for k in K)
        model.addConstr((NA[j, m] + 1) * sum_AW_dACWT >= APT[j, m], name=f"NA_APT_{j}_{m}")

# Constraint 10: Cjm[0,0] >= EPT[0,0]
model.addConstr(Cjm[0, 0] >= EPT[0, 0], name="Cjm_initial")

# Constraint 11: Cjm[j, m] >= sum(X[d,j] for d in D) * EPT[j,m] + Cjm[j-1,m] for j in1..jj-1, m in M
# Linearization using Big-M
for j in range(1, jj):
    for m in M:
        sum_X = gp.quicksum(X[d, j] for d in D)
        model.addConstr(Cjm[j, m] >= EPT[j, m] + Cjm[j-1, m] - BIG_M * (1 - sum_X), name=f"Cjm_pos_{j}_{m}")
        model.addConstr(Cjm[j, m] >= Cjm[j-1, m], name=f"Cjm_neg_{j}_{m}")

# Constraint 12: Cjm[j, m] >= sum(X[d,j] for d in D) * EPT[j,m] + Cjm[j,m-1] for j in J, m in1..mm-1
for j in J:
    for m in range(1, mm):
        sum_X = gp.quicksum(X[d, j] for d in D)
        model.addConstr(Cjm[j, m] >= EPT[j, m] + Cjm[j, m-1] - BIG_M * (1 - sum_X), name=f"Cjm_cross_pos_{j}_{m}")
        model.addConstr(Cjm[j, m] >= Cjm[j, m-1], name=f"Cjm_cross_neg_{j}_{m}")

# Constraint 13: X[d,j] <= dMixprod[d] for all d, j
# Assuming dMixprod is provided per d
# From Mixprods, assuming it's the first mixprod
dMixprod = Mixprods[0]  # [1, 0, 0]
for d in D:
    for j in J:
        model.addConstr(X[d, j] <= dMixprod[d], name=f"Mixprod_{d}_{j}")

# Objective: Maximize sum of X[d,j] over all d and j
model.setObjective(gp.quicksum(X[d, j] for d in D for j in J), GRB.MAXIMIZE)

def print_fo(X, AW, dd, jj, kk, mm, obmin, dMixprod, sin, time_int, iii):
    sy = sum(X[d, j].X for d in range(dd) for j in range(jj))
    l = [sum(X[d, j].X for j in range(jj)) for d in range(dd)]
    l2 = [sum(AW[k, m].X * m for m in range(mm)) for k in range(kk)]
    print("\n")
    a = f" sin {sin} ,dMixprod:{dMixprod} ,sy:{sy} ,l: {l} ,l2 : {l2} , obmin : {obmin} , time_int :{time_int} , iii : {iii}"
    print(a)
    with open("file.txt", "a") as file:
        file.write("\n" + a)

def modd(dMixprod="", sin="", obmin=1, iii=1):
    start_time = datetime.now()
    # Optimize the model
    model.optimize()
    end_time = datetime.now()
    time_int = (end_time - start_time).total_seconds() / 60  # Time in minutes
    print_fo(X, AW, dd, jj, kk, mm, obmin, dMixprod, sin, time_int, iii)

# Running the model based on 'sele' and 'Mixprods'
iii = 1
for jjj in range(1):  # Only the first iteration as per your loop
    sin = sele[iii-1]  # Python is 0-indexed
    dMixprod = Mixprods[iii-1]
    print(sin)
    print(dMixprod)
    modd(dMixprod, sin, jjj+1, iii)
lPtc = var2list1d(APT,'Ptc')
# X=var2list2d(X,'Cjm')
Cj=var2list2d(Cjm,'Cjm')
# print(X)
# print(lPtc)
# print(Cj)

Nfj=var2list2d(NA,'Nfjm')
planning2(Cj ,Nfj ,CPTP ,TAP )