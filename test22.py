import time, os, random 
import math
from math import floor
import numpy as np
import matplotlib.pyplot as plt

# Import du solver PuLP pour la partie optimisation
from pulp import LpProblem, LpMinimize, LpVariable, lpSum

# Import de netlogoshow et autres fonctions depuis netlogopy2
from netlogopy2.netlogopy import netlogoshow, resize_world, set_background, PyTurtle, run_netlogo

plt.ion()

###################################################
# 1) FIGURES MATPLOTLIB (INTERACTIF)
###################################################
# Figure 1: Progression cumulée par job
fig_jobs, ax_jobs = plt.subplots()
ax_jobs.set_title("Figure 1 : Progression cumulée par Job")
ax_jobs.set_xlabel("Temps (ticks)")
ax_jobs.set_ylabel("Temps cumulé (avec vitesse)")

# Figure 2: Worker metrics (Fatigue, Expérience, Vitesse)
fig_workers, ax_workers = plt.subplots(1, 3, figsize=(12, 4))
fig_workers.suptitle("Figure 2 : Fatigue / Expérience / Vitesse par ouvrier", fontsize=14)

# Figure 3: Markov state per worker
fig_states, ax_states = plt.subplots(1, 3, figsize=(12, 4))
fig_states.suptitle("Figure 3 : État Markov (0..3) par ouvrier", fontsize=14)

###################################################
# 2) PARAMÈTRES GLOBAUX
###################################################
pas_tick = 1          
speed_tik = 0.3       
EOS = 480             
deta_group = 10       # Délai pour changer de groupe de profils
pas_reoptimisation = 50  # Réaffectation dynamique toutes les 50 itérations

L_period = 480        
f_init = 0.0          
e_init = 0.0          

###################################################
# 3) FONCTIONS MATHÉMATIQUES
###################################################
def update_fatigue(current_fatigue: float, is_working: bool, lam: float = 0.01,
                   beta: float = 1.0, gamma: float = 0.02, dt: float = 1.0) -> float:
    if is_working:
        new_f = 1.0 - (1.0 - current_fatigue) * math.exp(-lam * beta * dt)
    else:
        new_f = current_fatigue * math.exp(-gamma * dt)
    return new_f

def new_experience(t, current_e, e_min, e_max, k, t0, is_working):
    """
    Calcule la nouvelle expérience d'un ouvrier.
    Si is_working est True, l'expérience augmente selon une courbe logistique,
    sinon elle reste inchangée.
    """
    if is_working:
        new_e =  e_min + (e_max - e_min) / (1.0 + math.exp(-k * (t - t0)))
    else:
        new_e = current_e
    return new_e

def new_speed(t, f_init, lamF, e_init, lamE, L):
    nb_segments = floor(t / L)
    e_val = e_init + lamE * nb_segments
    f_val = f_init * math.exp(-lamF * (t % L))
    return max(0.0, e_val - f_val)

###################################################
# 4) CLASSE profile
###################################################
class profile:
    def __init__(self, fields={}):
        self.__dict__.update(fields)

###################################################
# 5) PROFILS EXEMPLE
###################################################
profile_0 = profile({
    "name": "prf0",
    "f_init": f_init,
    "lamF": 0.0,
    "e_init": e_init,
    "lamE": 0.0,
    "L": L_period,
    "lam": 0.01,
    "beta": 1.0,
    "gamma": 0.02,
    "e_min": 0.1,   # valeur ajoutée si travail
    "e_max": 6.0,
    "k": 0.015,
    "t0": 200,
    "punct": [
        [1, 0, 0, 0],
        [0.5, 0.5, 0, 0],
        [0.4, 0.3, 0.2, 0.1],
        [1, 0, 0, 0]
    ]
})

profile_1 = profile({
    "name": "prf1",
    "f_init": f_init,
    "lamF": 0.1,
    "e_init": e_init,
    "lamE": 0.1,
    "L": L_period,
    "lam": 0.02,
    "beta": 1.2,
    "gamma": 0.01,
    "e_min": 0.1,
    "e_max": 6.0,
    "k": 0.015,
    "t0": 200,
    "punct": [
        [0.9, 0.1, 0, 0],
        [0.6, 0.2, 0.1, 0.1],
        [0, 0.3, 0.4, 0.3],
        [0, 0.3, 0.4, 0.3]
    ]
})

profile_2 = profile({
    "name": "prf2",
    "f_init": f_init,
    "lamF": 0.05,
    "e_init": e_init,
    "lamE": 0.2,
    "L": L_period,
    "lam": 0.03,
    "beta": 1.5,
    "gamma": 0.02,
    "e_min": 0.1,
    "e_max": 6.0,
    "k": 0.015,
    "t0": 200,
    "punct": [
        [0.8, 0.2, 0, 0],
        [0.3, 0.3, 0.2, 0.2],
        [0, 0.4, 0.3, 0.3],
        [0, 0.3, 0.4, 0.3]
    ]
})

###################################################
# 6) ROUTING JOBS ET JOB_COUNTS
###################################################
job_counts = {
    "J1": 10,
    "J2": 10,
    "J3": 10,
    "J4": 0,
    "J5": 0,
    "J6": 0,
    "J7": 0,
    "J8": 0,
}

routing = {
    "J1": [("M1", 5), ("M3", 2), ("M2", 4)],
    "J2": [("M2", 3), ("M1", 4), ("M3", 9)],
    "J3": [("M3", 2), ("M2", 2), ("M1", 1)],
    "J4": [("M1", 14), ("M3", 12), ("M2", 15)],
    "J5": [("M1", 14), ("M2", 12), ("M3", 15)],
    "J6": [("M2", 14), ("M1", 12), ("M3", 15)],
    "J7": [("M2", 14), ("M3", 12), ("M1", 15)],
    "J8": [("M3", 14), ("M2", 12), ("M1", 15)]
}

###################################################
# 7) IMPORT NETLOGOPY ET EFFACEMENT DE L'ECRAN
###################################################
os.system('cls')

###################################################
# 8) CLASSES ENTITÉS DU JOB SHOP
###################################################
class Zone:
    def __init__(self, nl_interface, x, y, shape, size, color, name, labelcolor):
        self.obj = PyTurtle(nl_interface, x=x, y=y, shape=shape, size_shape=size,
                             color=color, name=name, labelcolor=labelcolor,
                             fields={"worker_encour": None, "free": True})
        self.name = name

class Operation:
    def __init__(self, job_name, machine_name, duration):
        self.job_name = job_name
        self.machine_name = machine_name
        self.duration = duration
        self.start_time = None

class Job:
    def __init__(self, nl_interface, job_name, routing_sequence):
        self.job_name = job_name
        self.routing_sequence = routing_sequence
        self.current_op_index = 0
        self.finished = False
        index_str = str(min(int(job_name[1:]), 5))
        shape_name = "p_robot0" + index_str
        self.rep = PyTurtle(nl_interface, x=5, y=5,
                             shape=shape_name, size_shape=5,
                             color=15, name=job_name, labelcolor=15, fields={})
        self.total_duration = sum(d for (_, d) in routing_sequence)

    def get_next_operation(self):
        if self.current_op_index < len(self.routing_sequence):
            machine_name, duration = self.routing_sequence[self.current_op_index]
            return Operation(self.job_name, machine_name, duration)
        return None

    def advance(self):
        self.current_op_index += 1
        if self.current_op_index >= len(self.routing_sequence):
            self.finished = True

    def update_representation(self, new_target):
        self.rep.move_to(new_target)

class Worker:
    def __init__(self, nl_interface, name, profile, znp1_obj, znp2_obj, znp3_obj, machine_obj, color=55):
        self.name = name
        self.profile = profile
        self.num_operations = 0
        self.nht = 0
        self.current_state = 0  # commence sur la machine assignée
        self.fatigue_level = profile.f_init
        self.experience = profile.e_init  # Initialisation de l'expérience
        
        self.rep = PyTurtle(nl_interface, x=0, y=0, shape="person_0", size_shape=5,
                             color=color, name=name, labelcolor=color, fields={})
        self.rep.move_to(machine_obj)
        self.rep.fd(5)
        self.zone_by_state = {
            0: machine_obj,
            1: znp1_obj,
            2: znp2_obj,
            3: znp3_obj
        }

    def def_vit(self, t):
        is_working = (self.current_state == 0)
        # Mise à jour de l'expérience en fonction de si l'ouvrier travaille
        exp_val = new_experience(
            t,
            current_e=self.experience,
            e_min=self.profile.e_min,
            e_max=self.profile.e_max,
            k=self.profile.k,
            t0=self.profile.t0,
            is_working=is_working
        )
        self.experience = exp_val
        speed_val = max(0.0, exp_val - self.fatigue_level)
        return speed_val

    def update_profile(self, new_profile, reset_fatigue=False):
        self.profile = new_profile
        if reset_fatigue:
            self.fatigue_level = new_profile.f_init

    def step_markov(self, t):
        p_line = self.profile.punct[self.current_state]
        new_state = np.random.choice([0, 1, 2, 3], p=p_line)
        if new_state != self.current_state:
            self.current_state = new_state
            self.rep.move_to(self.zone_by_state[new_state])
            self.rep.fd(5)
        is_working = (self.current_state == 0)
        self.fatigue_level = update_fatigue(
            current_fatigue=self.fatigue_level,
            is_working=is_working,
            lam=self.profile.lam,
            beta=self.profile.beta,
            gamma=self.profile.gamma,
            dt=1.0
        )

    def update_label(self, text):
        self.rep.set_label(text)

class Machine:
    def __init__(self, nl_interface, name, x, y, shape="machine", size=4, color=15):
        self.name = name
        self.queue = []
        self.operation_in_progress = None
        self.operator = None
        self.obj = PyTurtle(nl_interface, x=x, y=y, shape=shape, size_shape=size,
                             color=color, name=name, labelcolor=color,
                             fields={"busy": False})
        self._update_label_queue()

    def _update_label_queue(self):
        q_size = len(self.queue)
        if self.operation_in_progress:
            q_size += 1
        self.obj.set_label(f"Q={q_size}")

    def set_operator(self, worker):
        self.operator = worker

    def add_operation(self, operation):
        self.queue.append(operation)
        self._update_label_queue()

    def process(self, tick):
        if not self.operator:
            return None
        if self.operator.current_state != 0:
            return None

        tick_time = tick
        if self.operation_in_progress is None and self.queue:
            self.operation_in_progress = self.queue.pop(0)
            self.operation_in_progress.start_time = tick_time
            self.obj.fields["busy"] = True
            self._update_label_queue()

        if self.operation_in_progress:
            w_speed = self.operator.def_vit(tick_time)
            elapsed = (tick_time - self.operation_in_progress.start_time) * w_speed
            if elapsed >= self.operation_in_progress.duration:
                finished_op = self.operation_in_progress
                self.operation_in_progress = None
                self.obj.fields["busy"] = False
                self.operator.num_operations += 1
                self._update_label_queue()
                return finished_op
        return None

###################################################
# 9) SIMULATION AVEC FIGURES ET OPTIMISATION
###################################################
class JobShopSimulation:
    def __init__(self, nl_interface):
        resize_world(nl_interface, 0, 60, 0, 60)
        set_background(nl_interface, "D:/cphs2024/netlogopy.png")
        self.nl_interface = nl_interface

        # Zones non-productives
        self.znp1 = Zone(nl_interface, 5, 50, "house", 3, 25, "ZNP1", 25)
        self.znp2 = Zone(nl_interface, 15, 50, "house", 3, 35, "ZNP2", 35)
        self.znp3 = Zone(nl_interface, 25, 50, "house", 3, 45, "ZNP3", 45)

        # Machines
        self.machines = {
            "M1": Machine(nl_interface, "M1", 10, 30, "machine", 4, 15),
            "M2": Machine(nl_interface, "M2", 30, 30, "machine2", 4, 55),
            "M3": Machine(nl_interface, "M3", 50, 30, "machine3", 4, 55)
        }

        # Définition de groupes de profils
        self.profils_d = [
            [profile_0, profile_0, profile_0],
            # [profile_0, profile_0, profile_0],
            # [profile_0, profile_1, profile_2],
            # [profile_2, profile_2, profile_2],
            # [profile_0, profile_1, profile_2],
            # [profile_1, profile_1, profile_1],
            # [profile_0, profile_1, profile_2],
            # [profile_2, profile_2, profile_2],
            # [profile_0, profile_1, profile_2],
            # [profile_1, profile_1, profile_1],
        ]

        # Création des workers initiaux (groupe 0)
        self.workers = {
            "W1": Worker(nl_interface, "worker_1_" + self.profils_d[0][0].name,
                         self.profils_d[0][0],
                         self.znp1.obj, self.znp2.obj, self.znp3.obj,
                         self.machines["M1"].obj, color=14),
            "W2": Worker(nl_interface, "worker_2_" + self.profils_d[0][1].name,
                         self.profils_d[0][1],
                         self.znp1.obj, self.znp2.obj, self.znp3.obj,
                         self.machines["M2"].obj, color=55),
            "W3": Worker(nl_interface, "worker_3_" + self.profils_d[0][2].name,
                         self.profils_d[0][2],
                         self.znp1.obj, self.znp2.obj, self.znp3.obj,
                         self.machines["M3"].obj, color=95),
        }

        self.machines["M1"].set_operator(self.workers["W1"])
        self.machines["M2"].set_operator(self.workers["W2"])
        self.machines["M3"].set_operator(self.workers["W3"])

        # Zone finale (stock final)
        self.stockfinal = Zone(nl_interface, 40, 50, "house", 3, 25, "StockFinal", 15)

        # Création des jobs
        self.jobs = []
        for jname, nb in job_counts.items():
            for i in range(nb):
                job_id = jname if nb == 1 else f"{jname}_{i+1}"
                self.jobs.append(Job(nl_interface, job_id, routing[jname]))

        self.totalDuration_job = {job.job_name: sum(d for (_, d) in job.routing_sequence)
                                  for job in self.jobs}
        self.cumulTime_job = {job.job_name: 0.0 for job in self.jobs}
        self.finished_jobs_count = 0

        # Affectation de la première opération de chaque job
        for job in self.jobs:
            op = job.get_next_operation()
            if op:
                self.machines[op.machine_name].add_operation(op)
                job.update_representation(self.machines[op.machine_name].obj)

        # Configuration des figures
        global fig_jobs, ax_jobs
        self.fig_jobs = fig_jobs
        self.ax_jobs = ax_jobs
        self.lines_by_job = {}
        self.xdata = []
        self.cumulTime_by_job = {}
        color_map = ["red", "green", "blue", "orange", "purple", "brown", "cyan", "magenta", "lime", "pink"]
        cidx = 0
        for job in self.jobs:
            jn = job.job_name
            col = color_map[cidx % len(color_map)]
            cidx += 1
            (line,) = self.ax_jobs.plot([], [], color=col, label=jn)
            self.lines_by_job[jn] = line
            self.cumulTime_by_job[jn] = []
        self.ax_jobs.legend()
        self.ax_jobs.set_xlabel("Temps (tick)")
        self.ax_jobs.set_ylabel("Temps cumulé du job (valeur)")

        global fig_workers, ax_workers
        self.fig_workers = fig_workers
        self.ax_workers = ax_workers
        self.worker_timeline = {}
        self.worker_lines = {}
        wList = ["W1", "W2", "W3"]
        for i, wName in enumerate(wList):
            self.worker_timeline[wName] = {"t": [], "fatigue": [], "experience": [], "speed": []}
            axw = self.ax_workers[i]
            axw.set_autoscaley_on(True)
            axw.set_title(wName)
            (lfat,) = axw.plot([], [], 'r-', label="fatigue")
            (lexp,) = axw.plot([], [], 'g-', label="experience")
            (lspd,) = axw.plot([], [], 'b-', label="speed")
            axw.legend()
            self.worker_lines[wName] = {"fatigue": lfat, "experience": lexp, "speed": lspd}

        global fig_states, ax_states
        self.fig_states = fig_states
        self.ax_states = ax_states
        self.state_timeline = {}
        self.state_lines = {}
        for i, wName in enumerate(wList):
            self.state_timeline[wName] = {"t": [], "state": []}
            axst = self.ax_states[i]
            axst.set_autoscaley_on(True)
            axst.set_yticks([0, 1, 2, 3])
            axst.set_title(wName)
            (lsta,) = axst.plot([], [], 'k-', label="état")
            axst.legend()
            self.state_lines[wName] = lsta

    def dynamic_opt(self, i):
        """
        Réaffectation dynamique via PuLP.
        - Mise à jour des profils des ouvriers en fonction de l'indice de groupe i.
        - Construction d'une matrice de coûts : coût = (taille de queue) / (vitesse + epsilon).
        - Résolution d'un problème d'affectation 1-1.
        - Affichage ligne par ligne de l'affectation dans NetLogo.
        """
        tick_courant = self.current_tick
        netlogoshow(self.nl_interface, f"Début réaffectation dynamique, tick={tick_courant}, groupe={i}")

        machines_list = list(self.machines.keys())
        workers_list = list(self.workers.keys())

        # Mise à jour des profils et labels
        self.workers["W1"].update_profile(self.profils_d[i][0])
        self.workers["W1"].update_label(f"W1 -> {self.profils_d[i][0].name}")

        self.workers["W2"].update_profile(self.profils_d[i][1])
        self.workers["W2"].update_label(f"W2 -> {self.profils_d[i][1].name}")

        self.workers["W3"].update_profile(self.profils_d[i][2])
        self.workers["W3"].update_label(f"W3 -> {self.profils_d[i][2].name}")

        # Construction de la matrice de coûts
        cost = {}
        epsilon = 0.001
        for wName in workers_list:
            spd = self.workers[wName].def_vit(tick_courant)
            for mName in machines_list:
                queue_len = len(self.machines[mName].queue)
                if self.machines[mName].operation_in_progress:
                    queue_len += 1
                cost[(wName, mName)] = queue_len / (spd + epsilon)

        prob = LpProblem("AssignWorkersToMachines", LpMinimize)
        x = LpVariable.dicts('assign', (workers_list, machines_list), cat='Binary')

        prob += lpSum(cost[(w, m)] * x[w][m] for w in workers_list for m in machines_list)

        for w in workers_list:
            prob += lpSum(x[w][m] for m in machines_list) == 1
        for m in machines_list:
            prob += lpSum(x[w][m] for w in workers_list) == 1

        prob.solve()

        # Lecture de la solution et réassignation + construction d'un texte d'affectation
        affectation_text = "Meilleure affectation :"
        for wName in workers_list:
            for mName in machines_list:
                if x[wName][mName].varValue == 1:
                    old_machine = None
                    for mObj in self.machines.values():
                        if mObj.operator == self.workers[wName]:
                            old_machine = mObj
                            break
                    if old_machine and old_machine.name != mName:
                        old_machine.operator = None

                    self.machines[mName].operator = self.workers[wName]
                    wObj = self.workers[wName]
                    wObj.current_state = 0
                    wObj.zone_by_state[0] = self.machines[mName].obj
                    wObj.rep.move_to(self.machines[mName].obj)
                    wObj.rep.fd(5)
                    affectation_text += f"\n{wName} => {mName}"
        # Affichage ligne par ligne dans NetLogo
        for line in affectation_text.split('\n'):
            netlogoshow(self.nl_interface, line)
        netlogoshow(self.nl_interface, f"Réaffectation terminée (tick={tick_courant}, groupe={i})")

    def run(self, total_ticks):
        i_group = 0
        for tick in range(total_ticks):
            self.current_tick = tick
            time.sleep(speed_tik)

            if tick % deta_group == 0:
                i_group += 1
                try:
                    self.dynamic_opt(i_group)
                except Exception as e:
                    netlogoshow(self.nl_interface, f"Erreur en réaffectation: {e}")

            for w in self.workers.values():
                w.step_markov(tick)

            for machine in self.machines.values():
                op_in_progress = machine.operation_in_progress
                if op_in_progress and machine.operator:
                    w_speed = machine.operator.def_vit(tick)
                    self.cumulTime_job[op_in_progress.job_name] += pas_tick * w_speed

                result = machine.process(tick)
                if result:
                    job = self.find_job_by_name(result.job_name)
                    if job:
                        job.advance()
                        if job.finished:
                            self.finished_jobs_count += 1
                            job.update_representation(self.stockfinal.obj)
                            netlogoshow(self.nl_interface,
                                        f"{job.job_name} terminé => {self.finished_jobs_count} finis (tick={tick})")
                            print(f"{job.job_name} terminé => {self.finished_jobs_count} jobs finis | tick={tick}")
                        else:
                            nxt_op = job.get_next_operation()
                            next_machine = self.machines[nxt_op.machine_name]
                            next_machine.add_operation(nxt_op)
                            job.update_representation(next_machine.obj)

            self.update_plot_jobs(tick)
            self.update_plot_workers(tick)
            self.update_plot_states(tick)

            if self.finished_jobs_count == len(self.jobs):
                netlogoshow(self.nl_interface, f"Tous les jobs terminés au tick={tick}")
                print(f"Tous les jobs terminés au tick={tick}")
                break

        netlogoshow(self.nl_interface, f"Simulation terminée. Jobs finis = {self.finished_jobs_count}")
        print(f"Simulation terminée. Jobs finis = {self.finished_jobs_count}")
        plt.ioff()
        plt.show()

    def update_plot_jobs(self, tick):
        self.xdata.append(tick)
        for job in self.jobs:
            jn = job.job_name
            val = self.cumulTime_job[jn]
            self.cumulTime_by_job[jn].append(val)
            line = self.lines_by_job[jn]
            line.set_xdata(self.xdata)
            line.set_ydata(self.cumulTime_by_job[jn])
        self.ax_jobs.relim()
        self.ax_jobs.autoscale_view()
        self.fig_jobs.canvas.draw_idle()
        self.fig_jobs.canvas.flush_events()

    def update_plot_workers(self, tick):
        wList = ["W1", "W2", "W3"]
        for wName in wList:
            wObj = self.workers[wName]
            self.worker_timeline[wName]["t"].append(tick)
            ftg = wObj.fatigue_level
            p = wObj.profile
            exp_val = new_experience(tick, wObj.experience, p.e_min, p.e_max, p.k, p.t0, wObj.current_state==0)
            spd = wObj.def_vit(tick)
            self.worker_timeline[wName]["fatigue"].append(ftg)
            self.worker_timeline[wName]["experience"].append(exp_val)
            self.worker_timeline[wName]["speed"].append(spd)
        for i, wName in enumerate(wList):
            axw = self.ax_workers[i]
            lf = self.worker_lines[wName]["fatigue"]
            le = self.worker_lines[wName]["experience"]
            ls = self.worker_lines[wName]["speed"]
            tvals = self.worker_timeline[wName]["t"]
            fvals = self.worker_timeline[wName]["fatigue"]
            evals = self.worker_timeline[wName]["experience"]
            svals = self.worker_timeline[wName]["speed"]
            lf.set_xdata(tvals)
            lf.set_ydata(fvals)
            le.set_xdata(tvals)
            le.set_ydata(evals)
            ls.set_xdata(tvals)
            ls.set_ydata(svals)
            axw.relim()
            axw.autoscale_view()
        self.fig_workers.canvas.draw_idle()
        self.fig_workers.canvas.flush_events()

    def update_plot_states(self, tick):
        wList = ["W1", "W2", "W3"]
        for wName in wList:
            wObj = self.workers[wName]
            self.state_timeline[wName]["t"].append(tick)
            self.state_timeline[wName]["state"].append(wObj.current_state)
        for i, wName in enumerate(wList):
            axst = self.ax_states[i]
            line_sta = self.state_lines[wName]
            tvals = self.state_timeline[wName]["t"]
            svals = self.state_timeline[wName]["state"]
            line_sta.set_xdata(tvals)
            line_sta.set_ydata(svals)
            axst.relim()
            axst.autoscale_view()
        self.fig_states.canvas.draw_idle()
        self.fig_states.canvas.flush_events()

    def find_job_by_name(self, name):
        for j in self.jobs:
            if j.job_name == name:
                return j
        return None

###################################################
# 10) MAIN
###################################################
if __name__=="__main__":
    nl_interface = run_netlogo("C:/Program Files/NetLogo 6.2.2")
    sim = JobShopSimulation(nl_interface)
    sim.run(EOS)
    nl_interface.close_model()
