import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
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
    
from conf.input import *
#---------------------------------------
# Build the Model
#---------------------------------------
def runmodel():
    model = gp.Model("Dual-Resource-Flow-Shop")

    # Decision variables
    X = model.addVars( T_set , J , vtype=GRB.BINARY, name="X")  # X_{j,t}: 1 if j-th job is product type t
    Y = model.addVars(J, vtype=GRB.BINARY, name="Y")  # Y_j: 1 if j-th job is launched
    N = model.addVars(J, M, vtype=GRB.INTEGER, lb=0, name="N")  # Interruptions N_{j,m}
    PiC = model.addVars(J, M, vtype=GRB.CONTINUOUS, lb=0, name="PiC")  # Processing times Π_{j,m}
    Pi= model.addVars(J, M, vtype=GRB.CONTINUOUS, lb=0, name="Pi")  # Processing times Π_{j,m}
    C = model.addVars(J, M, vtype=GRB.CONTINUOUS, lb=0, name="C")  # Completion times C_{j,m}


    # # Objective: Maximize total Y_j (jobs produced)
    model.setObjective(gp.quicksum(Y[j] for j in J)-0.0001*gp.quicksum(C[j, m] for j in J for m in M), GRB.MAXIMIZE)

    # Objective: Minimize the sum of C_{j,m} for specific jobs and machines
    # model.setObjective(gp.quicksum(C[j, m] for j in J for m in M), GRB.MINIMIZE)

    # Constraint: Y_j equals the sum of X_{t,j} over all product types t
    model.addConstrs( (Y[j] == gp.quicksum(X[t, j] for t in T_set) for j in J),    name="Y_definition" )

    model.addConstrs((gp.quicksum(X[t, j] for t in T_set) == Y[j] for j in J), name="product_type_per_job")
    model.addConstrs( (Pi[1, m] == N[1, m] * D[m] + gp.quicksum(X[t, 1] * adjusted_tau[(t, m)] for t in T_set) for m in M), name="PiC_first_job")
    model.addConstrs((Pi[j, m] == (N[j, m] - N[j-1, m]) * D[m] + gp.quicksum(X[t, j] * adjusted_tau[(t, m)] for t in T_set) for j in range(2, len(J)+1) for m in M), name="PiC_subsequent_jobs")
    model.addConstrs( (PiC[1, m] == gp.quicksum(X[t,1] * tau[(t, m)] for t in T_set) for m in M), name="PiC_first_job")
    model.addConstrs((PiC[j, m] == PiC[j-1, m] +gp.quicksum(X[t, j] * adjusted_tau[(t, m)] for t in T_set) for j in J[1:] for m in M), name="PiC_def")

    # Constraints

    model.addConstrs((gp.quicksum(W[(k, m)] for k in alpha.keys()) == 1 for m in M), name="worker_assignment_per_machine")  # C3
    model.addConstrs((gp.quicksum(W[(k, m)] for m in M) <= 1 for k in alpha.keys()), name="worker_assignment_per_worker")  # C4
    model.addConstrs((X[t, j] <= I[t] for j in J for t in T_set), name="product_type_limit")  # C5
    model.addConstrs((gp.quicksum(X[t, j] for j in J) >= I[t] for t in T_set), name="min_demand")  # C6
    model.addConstrs((Y[j] <= Y[j-1] for j in range(2, len(J)+1)), name="sequence_production")  # C7
    model.addConstrs((N[j, m] + 1 >= PiC[j, m] / U[m] for j in J for m in M), name="N_constraint_lower")  # C8
    model.addConstrs((N[j, m] + 0.001 <= PiC[j, m] / U[m] for j in J for m in M), name="N_constraint_upper")  # C9
    model.addConstr(C[1, 1] == Pi[1, 1], name="initial_completion_time")  # C10
    model.addConstrs((C[j, m] >= Y[j] * Pi[j, m] + C[j-1, m] for j in range(2, len(J)+1) for m in M), name="job_completion_dependency")  # C11
    model.addConstrs((C[j, m] >= Y[j] * Pi[j, m] + C[j, m-1] for j in J for m in M if m > 1), name="machine_flow_dependency")  # C12
    model.addConstrs((C[j, m] <= H for j in J for m in M), name="horizon")  # C13

    # Constraint for the first job (j = 1)




    # Optimize the model
    model.optimize()
    lPtc = var2list1d(PiC,'Ptc')
    X2=var2list2d(X,'Cjm')
    Cj=var2list2d(C,'Cjm')
    # print(X)
    # print(lPtc)
    # print(Cj)
    lMtbfm = list(U.values())
    lMtfm = list(D.values())
    Nfj=var2list2d(N,'Nfjm')
    # print(gp.quicksum(Y[j].X for j in J))
    # print(X2)
    sec=[]
    for j in range(len(X2[0])):
        for t in range(len(X2)):
            if X2[t][j]:
                sec.append(t)

    

    return sec
