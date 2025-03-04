import time, os, random
import math
from math import floor
import numpy as np
import matplotlib.pyplot as plt

###################################################
# 1) FIGURES MATPLOTLIB
###################################################
plt.ion()

fig_jobs, ax_jobs = plt.subplots()
ax_jobs.set_title("Figure 1 : Progression cumulée par Job")
ax_jobs.set_xlabel("Temps (ticks)")
ax_jobs.set_ylabel("Temps cumulé (avec vitesse)")

fig_workers, ax_workers = plt.subplots(1, 3, figsize=(12, 4))
fig_workers.suptitle("Figure 2 : Fatigue / Expérience / Vitesse par ouvrier", fontsize=14)

fig_states, ax_states = plt.subplots(1, 3, figsize=(12, 4))
fig_states.suptitle("Figure 3 : État Markov (0..3) par ouvrier", fontsize=14)

###################################################
# 2) PARAMÈTRES GLOBAUX
###################################################
pas_tick = 1       # 1 tick = 1 unité de temps
speed_tik = 0.3    # Intervalle (s) entre ticks (peut être mis à 0)
EOS = 480          # Nombre total de ticks

# Pas de réoptimisation dynamique
pas_reoptimisation = 9999999999  

###################################################
# 3) FONCTIONS UTILES
###################################################
def update_fatigue(
    current_fatigue: float,
    is_working: bool,
    alpha_inc: float = 0.01,
    alpha_dec: float = 0.02
) -> float:
    """
    Met à jour la fatigue :
      - current_fatigue : niveau de fatigue actuel [0..1]
      - is_working      : True si l'ouvrier est au poste (état 0), False si en repos (états 1..3)
      - alpha_inc       : taux d'augmentation (lorsque l'ouvrier travaille)
      - alpha_dec       : taux de récupération (lorsqu'il est en repos)
    Retourne la fatigue mise à jour (bornée [0..1]).
    """
    if is_working:
        new_f = current_fatigue + alpha_inc
    else:
        new_f = current_fatigue - alpha_dec

    # Borne [0, 1]
    if new_f < 0:
        new_f = 0
    elif new_f > 1:
        new_f = 1
    return new_f

def new_experience_s(t, e_min, e_max, k, t0):
    """
    Courbe logistique (en S) pour modéliser l'apprentissage.

    E(t) = e_min + (e_max - e_min) / (1 + exp(-k*(t - t0)))

    - t    : le temps (tick)
    - e_min: expérience de départ
    - e_max: expérience de maîtrise
    - k    : vitesse de croissance (raideur de la courbe)
    - t0   : point d'inflexion
    """
    return e_min + (e_max - e_min) / (1.0 + math.exp(-k * (t - t0)))

###################################################
# 4) CLASSE profile
###################################################
class profile:
    """
    Exemple d'attributs dans un profil :
      - fatigue_init : fatigue initiale
      - alpha_inc    : taux d'augmentation de fatigue au travail
      - alpha_dec    : taux de récupération en repos
      - e_min, e_max, k, t0 : paramètres de la courbe logistique (expérience)
      - punct        : matrice de transition Markov 4x4
    """
    def __init__(self, fields={}):
        self.__dict__.update(fields)

###################################################
# 5) EXEMPLES DE PROFILS
###################################################
profile_0 = profile({
    "fatigue_init": 0.0,
    "alpha_inc": 0.01,
    "alpha_dec": 0.02,
    # Paramètres de la courbe logistique d'expérience
    "e_min": 0.5,
    "e_max": 3.0,
    "k": 0.01,
    "t0": 240,  
    "punct": [
        [1,   0,   0,   0],
        [0.5, 0.5, 0,   0],
        [0.4, 0.3, 0.2, 0.1],
        [1,   0,   0,   0]
    ]
})

profile_1 = profile({
    "fatigue_init": 0.0,
    "alpha_inc": 0.02,
    "alpha_dec": 0.01,
    "e_min": 0.3,
    "e_max": 5.0,
    "k": 0.02,
    "t0": 240,
    "punct": [
        [0.9, 0.1, 0,   0],
        [0.6, 0.2, 0.1, 0.1],
        [0,   0.3, 0.4, 0.3],
        [0,   0.3, 0.4, 0.3]
    ]
})

profile_2 = profile({
    "fatigue_init": 0.0,
    "alpha_inc": 0.03,
    "alpha_dec": 0.02,
    "e_min": 0.0,
    "e_max": 6.0,
    "k": 0.015,
    "t0": 200,
    "punct": [
        [0.8, 0.2, 0,   0],
        [0.3, 0.3, 0.2, 0.2],
        [0,   0.4, 0.3, 0.3],
        [0,   0.3, 0.4, 0.3]
    ]
})

###################################################
# 6) ROUTING + job_counts
###################################################
job_counts = {
    "J1": 1,
    "J2": 1,
    "J3": 1,
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
# 7) IMPORT NETLOGOPY
###################################################
from netlogopy2.netlogopy import netlogoshow, resize_world, set_background, PyTurtle
os.system('cls')

###################################################
# 8) CLASSES ENTITÉS
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
        shape_name = "p_robot0" + str(min(int(job_name[1:]) if job_name[1:].isdigit() else 1, 5))
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
    """
    Markov 4 états : 0=machine, 1,2,3=zones NP
    - fatigue_level mis à jour via update_fatigue
    - def_vit = (logistic experience) - (fatigue)
    """
    def __init__(self, nl_interface, name, profile,
                 znp1_obj, znp2_obj, znp3_obj, machine_obj, color=55):
        self.name = name
        self.profile = profile
        self.num_operations = 0
        self.nht = 0
        self.current_state = 0  # commence sur la machine
        self.fatigue_level = profile.fatigue_init
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
        # Expérience via la courbe logistique
        exp_val = new_experience_s(
            t,
            e_min=self.profile.e_min,
            e_max=self.profile.e_max,
            k=self.profile.k,
            t0=self.profile.t0
        )
        # Vitesse = exp_val - fatigue_level (borné à min=0)
        return max(0.0, exp_val - self.fatigue_level)

    def step_markov(self, t):
        # Markov
        p_line = self.profile.punct[self.current_state]
        new_state = np.random.choice([0,1,2,3], p=p_line)
        if new_state != self.current_state:
            self.current_state = new_state
            self.rep.move_to(self.zone_by_state[new_state])
            # Avancer un peu pour l'animation
            if self.current_state == 1:
                self.rep.fd(5)
            elif self.current_state == 2:
                self.rep.fd(7)
            elif self.current_state == 3:
                self.rep.fd(9)

        # Mise à jour fatigue
        is_working = (self.current_state == 0)
        self.fatigue_level = update_fatigue(
            current_fatigue=self.fatigue_level,
            is_working=is_working,
            alpha_inc=self.profile.alpha_inc,
            alpha_dec=self.profile.alpha_dec
        )

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
        # On ne traite que si un opérateur est présent et en état 0
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
# 9) SIMULATION
###################################################
class JobShopSimulation:
    def __init__(self, nl_interface):
        from netlogopy2.netlogopy import resize_world, set_background
        resize_world(nl_interface, 0, 60, 0, 60)
        set_background(nl_interface, "D:/cphs2024/netlogopy.png")
        self.nl_interface = nl_interface

        # Zones
        self.znp1 = Zone(nl_interface, 5, 50,  "house", 3, 25, "ZNP1", 25)
        self.znp2 = Zone(nl_interface, 15,50, "house", 3, 35, "ZNP2", 35)
        self.znp3 = Zone(nl_interface, 25,50, "house", 3, 45, "ZNP3", 45)

        # Machines
        self.machines = {
            "M1": Machine(nl_interface, "M1", 10, 30, "machine",  4, 15),
            "M2": Machine(nl_interface, "M2", 30, 30, "machine2", 4, 55),
            "M3": Machine(nl_interface, "M3", 50, 30, "machine3", 4, 55)
        }

        # Workers
        self.workers = {
            "W1": Worker(nl_interface, "worker_1", profile_0,
                         self.znp1.obj, self.znp2.obj, self.znp3.obj, self.machines["M1"].obj, 14),
            "W2": Worker(nl_interface, "worker_2", profile_1,
                         self.znp1.obj, self.znp2.obj, self.znp3.obj, self.machines["M2"].obj, 55),
            "W3": Worker(nl_interface, "worker_3", profile_2,
                         self.znp1.obj, self.znp2.obj, self.znp3.obj, self.machines["M3"].obj, 95),
        }
        self.machines["M1"].set_operator(self.workers["W1"])
        self.machines["M2"].set_operator(self.workers["W2"])
        self.machines["M3"].set_operator(self.workers["W3"])

        # Stock final
        self.stockfinal = Zone(nl_interface, 40,50, "house", 3, 25, "StockFinal", 15)

        # Création des jobs (selon job_counts)
        self.jobs = []
        for jname, nb in job_counts.items():
            for i in range(nb):
                # ex. "J1_1" si >1 exemplaire
                job_id = jname if nb == 1 else f"{jname}_{i+1}"
                self.jobs.append(Job(nl_interface, job_id, routing[jname]))

        # Durée cumulée
        self.totalDuration_job = {}
        for job in self.jobs:
            self.totalDuration_job[job.job_name] = sum(d for (_, d) in job.routing_sequence)
        self.cumulTime_job = {job.job_name: 0.0 for job in self.jobs}
        self.finished_jobs_count = 0

        # Ajout 1ère opération
        for job in self.jobs:
            op = job.get_next_operation()
            if op:
                self.machines[op.machine_name].add_operation(op)
                job.update_representation(self.machines[op.machine_name].obj)

        # Figure 1 : progression cumulée
        global fig_jobs, ax_jobs
        self.fig_jobs = fig_jobs
        self.ax_jobs = ax_jobs
        self.lines_by_job = {}
        self.xdata = []
        self.ax_jobs.set_autoscaley_on(True)

        self.cumulTime_by_job = {}
        color_map = [
            "red", "green", "blue", "orange", "purple",
            "brown", "cyan", "magenta", "lime", "pink",
            "olive", "gray", "black"
        ]
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
        self.ax_jobs.set_ylabel("Temps cumulé (job)")

        # Figure 2 : fatigue / exp / vitesse
        global fig_workers, ax_workers
        self.fig_workers = fig_workers
        self.ax_workers = ax_workers
        self.worker_timeline = {}
        self.worker_lines = {}
        wList = ["W1","W2","W3"]
        for i, wName in enumerate(wList):
            self.worker_timeline[wName] = {
                "t": [],
                "fatigue": [],
                "experience": [],
                "speed": []
            }
            axw = self.ax_workers[i]
            axw.set_autoscaley_on(True)
            axw.set_title(wName)
            (lfat,) = axw.plot([], [], 'r-', label="fatigue")
            (lexp,) = axw.plot([], [], 'g-', label="experience")
            (lspd,) = axw.plot([], [], 'b-', label="speed")
            axw.legend()
            self.worker_lines[wName] = {
                "fatigue": lfat,
                "experience": lexp,
                "speed": lspd
            }

        # Figure 3 : état Markov
        global fig_states, ax_states
        self.fig_states = fig_states
        self.ax_states = ax_states
        self.state_timeline = {}
        self.state_lines = {}
        for i, wName in enumerate(wList):
            self.state_timeline[wName] = {"t": [], "state": []}
            axst = self.ax_states[i]
            axst.set_autoscaley_on(True)
            axst.set_yticks([0,1,2,3])
            axst.set_title(wName)
            (lsta,) = axst.plot([], [], 'k-', label="état")
            axst.legend()
            self.state_lines[wName] = lsta

    def run(self, total_ticks):
        for tick in range(total_ticks):
            time.sleep(speed_tik)

            # (1) Mise à jour Markov + fatigue
            for w in self.workers.values():
                w.step_markov(tick)

            # (2) Avancement cumul
            for machine in self.machines.values():
                op_in_progress = machine.operation_in_progress
                if op_in_progress and machine.operator:
                    w_speed = machine.operator.def_vit(tick)
                    self.cumulTime_job[op_in_progress.job_name] += pas_tick * w_speed

                # process
                result = machine.process(tick)
                if result:
                    job = self.find_job_by_name(result.job_name)
                    if job:
                        job.advance()
                        if job.finished:
                            self.finished_jobs_count += 1
                            job.update_representation(self.stockfinal.obj)
                            print(f"{job.job_name} terminé => {self.finished_jobs_count} jobs finis | tick={tick}")
                        else:
                            nxt_op = job.get_next_operation()
                            nmach = self.machines[nxt_op.machine_name]
                            nmach.add_operation(nxt_op)
                            job.update_representation(nmach.obj)

            # (3) Mises à jour de l'affichage
            self.update_plot_jobs(tick)
            self.update_plot_workers(tick)
            self.update_plot_states(tick)

            if self.finished_jobs_count == len(self.jobs):
                print(f"Tous les jobs terminés au tick={tick}")
                break

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
        wList = ["W1","W2","W3"]
        for wName in wList:
            wObj = self.workers[wName]
            self.worker_timeline[wName]["t"].append(tick)

            # fatigue
            ftg = wObj.fatigue_level
            # expérience (logistique)
            exp_val = new_experience_s(
                t=tick,
                e_min=wObj.profile.e_min,
                e_max=wObj.profile.e_max,
                k=wObj.profile.k,
                t0=wObj.profile.t0
            )
            # vitesse
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
        wList = ["W1","W2","W3"]
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
    from netlogopy2.netlogopy import run_netlogo
    nl_interface = run_netlogo("C:/Program Files/NetLogo 6.2.2")

    sim = JobShopSimulation(nl_interface)
    sim.run(EOS)

    nl_interface.close_model()
