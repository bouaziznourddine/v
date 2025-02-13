import time, os, random
import math
from math import floor
import numpy as np
import matplotlib.pyplot as plt

###################################################
#               1) FIGURES MATPLOTLIB
###################################################
# Mode interactif
plt.ion()

# === Figure 1 : progression cumulée par job ===
fig_jobs, ax_jobs = plt.subplots()
ax_jobs.set_title("Figure 1 : Progression cumulée par Job")
ax_jobs.set_xlabel("Temps (ticks)")
ax_jobs.set_ylabel("Temps cumulé (avec vitesse)")

# === Figure 2 : fatigue / exp / vitesse par ouvrier ===
fig_workers, ax_workers = plt.subplots(1, 3, figsize=(12, 4))
fig_workers.suptitle("Figure 2 : Fatigue / Expérience / Vitesse par ouvrier", fontsize=14)

# === Figure 3 : états Markov par ouvrier ===
fig_states, ax_states = plt.subplots(1, 3, figsize=(12, 4))
fig_states.suptitle("Figure 3 : État Markov (0..3) par ouvrier", fontsize=14)

###################################################
#               2) PARAMÈTRES GLOBAUX
###################################################
pas_tick = 1       # 1 tick = 1 unité de temps
speed_tik = 0.3    # Délai (en secondes) entre deux ticks
EOS = 50           # Nombre total de ticks

# Période L pour la fatigue/exp
L_period = 30
f_init = 1.0
e_init = 1.0

###################################################
#               3) FONCTIONS MATHÉMATIQUES
###################################################
def new_fatigue(t, f_init, lamF, L):
    """
    F(t) = f_init * exp( - lamF * ( t mod L ) )
    """
    mod_part = t % L
    return f_init * math.exp(- lamF * mod_part)

def new_experience(t, e_init, lamE, L):
    """
    E(t) = e_init + lamE * floor( t / L )
    """
    nb_segments = floor(t / L)
    return e_init + lamE * nb_segments

def new_speed(t, f_init, lamF, e_init, lamE, L):
    """
    S(t) = F(t) + E(t).
    """
    f_val = new_fatigue(t, f_init, lamF, L)
    e_val = new_experience(t, e_init, lamE, L)
    return f_val + e_val

###################################################
#               4) CLASSE profile
###################################################
class profile:
    """
    Contient :
      - f_init (float)
      - lamF   (float) (coefficient d'exponentiel pour fatigue)
      - e_init (float)
      - lamE   (float) (coefficient paliers pour expérience)
      - L      (int)   = période
      - punct  (4x4)   = matrice de transition Markov 4 états
    """
    def __init__(self, fields={}):
        self.__dict__.update(fields)

###################################################
#               5) PROFILS EXEMPLE
###################################################
profile_0 = profile({
    "f_init": f_init,
    "lamF": 0.0,
    "e_init": e_init,
    "lamE": 0.0,
    "L": L_period,
    "punct": [
        [1,   0,   0,   0],
        [0.5, 0.5, 0,   0],
        [0.4, 0.3, 0.2, 0.1],
        [1,   0,   0,   0]
    ]
})

profile_1 = profile({
    "f_init": f_init,
    "lamF": 0.1,
    "e_init": e_init,
    "lamE": 0.1,
    "L": L_period,
    "punct": [
        [0.9, 0.1, 0,   0],
        [0.6, 0.2, 0.1, 0.1],
        [0,   0.3, 0.4, 0.3],
        [0,   0.3, 0.4, 0.3]
    ]
})

profile_2 = profile({
    "f_init": f_init,
    "lamF": 0.05,
    "e_init": e_init,
    "lamE": 0.2,
    "L": L_period,
    "punct": [
        [0.8, 0.2, 0,   0],
        [0.3, 0.3, 0.2, 0.2],
        [0,   0.4, 0.3, 0.3],
        [0,   0.3, 0.4, 0.3]
    ]
})

###################################################
#               6) ROUTING JOBS
###################################################
routing = {
    "J1": [("M1", 20), ("M3", 15), ("M2", 10)],
    "J2": [("M2", 22), ("M1", 12), ("M3", 15)],
    "J3": [("M3", 14), ("M2", 12), ("M1", 15)],
    "J4": [("M1", 14), ("M3", 12), ("M2", 15)],
    "J5": [("M1", 14), ("M2", 12), ("M3", 15)],
    "J6": [("M2", 14), ("M1", 12), ("M3", 15)],
    "J7": [("M2", 14), ("M3", 12), ("M1", 15)],
    "J8": [("M3", 14), ("M2", 12), ("M1", 15)],
}

###################################################
#               7) IMPORT NETLOGOPY
###################################################
from netlogopy2.netlogopy import netlogoshow, resize_world, set_background, PyTurtle
os.system('cls')

###################################################
#               8) CLASSES
###################################################
class Zone:
    """
    Représente une zone non-productive (ou finale).
    """
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
        # Représentation NetLogo
        self.rep = PyTurtle(nl_interface, x=5, y=5,
                            shape="p_robot0"+str(job_name[1:]), size_shape=5,
                            color=15, name=job_name, labelcolor=15, fields={})
        self.total_duration = sum(d for (_,d) in routing_sequence)

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
    Markov 4 états : 0=machine, 1=ZNP1, 2=ZNP2, 3=ZNP3
    """
    def __init__(self, nl_interface, name, profile,
                 znp1_obj, znp2_obj, znp3_obj, machine_obj):
        self.name = name
        self.profile = profile
        self.num_operations = 0
        self.nht = 0
        self.current_state = 0  # commence sur la machine
        self.rep = PyTurtle(nl_interface, x=0, y=0, shape="person_0", size_shape=5,
                            color=55, name=name, labelcolor=55, fields={})
        self.rep.move_to(machine_obj)
        self.rep.fd(5)

        # On associe chaque état à un PyTurtle (machine ou zone NP)
        self.zone_by_state = {
            0: machine_obj,    # l'opérateur se trouve sur sa "machine assignée"
            1: znp1_obj,
            2: znp2_obj,
            3: znp3_obj
        }

    def def_vit(self, t):
        """
        S(t) = F(t) + E(t)
        """
        p = self.profile
        return new_speed(
            t,
            p.f_init,
            p.lamF,
            p.e_init,
            p.lamE,
            p.L
        )

    def step_markov(self):
        """
        Markov => transition ponct
        """
        p_line = self.profile.punct[self.current_state]
        new_state = np.random.choice([0,1,2,3], p=p_line)
        if new_state != self.current_state:
            self.current_state = new_state
            self.rep.move_to(self.zone_by_state[new_state])

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
            label_str = f"Q={q_size+1}"
        else:
            label_str = f"Q={q_size}"
        self.obj.set_label(label_str)

    def set_operator(self, worker):
        self.operator = worker

    def add_operation(self, operation):
        self.queue.append(operation)
        self._update_label_queue()

    def process(self, tick):
        if self.operator is None:
            return None
        # On ne traite que si l'état = 0
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
#   9) SIMULATION (avec 3 Figures)
###################################################
class JobShopSimulation:
    def __init__(self, nl_interface):
        from netlogopy2.netlogopy import resize_world, set_background
        resize_world(nl_interface, 0, 60, 0, 60)
        set_background(nl_interface, "D:/cphs2024/netlogopy.png")

        self.nl_interface = nl_interface

        # === Création de 3 zones NP ===
        self.znp1 = Zone(nl_interface, x=5,  y=50, shape="house", size=3, color=25, name="ZNP1", labelcolor=25)
        self.znp2 = Zone(nl_interface, x=15, y=50, shape="house", size=3, color=35, name="ZNP2", labelcolor=35)
        self.znp3 = Zone(nl_interface, x=25, y=50, shape="house", size=3, color=45, name="ZNP3", labelcolor=45)

        # === Machines ===
        self.machines = {
            "M1": Machine(nl_interface, "M1", x=10, y=30, shape="machine",  size=4, color=15),
            "M2": Machine(nl_interface, "M2", x=30, y=30, shape="machine2", size=4, color=55),
            "M3": Machine(nl_interface, "M3", x=50, y=30, shape="machine3", size=4, color=55)
        }

        # === Workers (Markov 4 états) ===
        self.workers = {
            "W1": Worker(nl_interface, "worker_1", profile_0,
                         self.znp1.obj, self.znp2.obj, self.znp3.obj,
                         self.machines["M1"].obj),
            "W2": Worker(nl_interface, "worker_2", profile_1,
                         self.znp1.obj, self.znp2.obj, self.znp3.obj,
                         self.machines["M2"].obj),
            "W3": Worker(nl_interface, "worker_3", profile_2,
                         self.znp1.obj, self.znp2.obj, self.znp3.obj,
                         self.machines["M3"].obj),
        }
        self.machines["M1"].set_operator(self.workers["W1"])
        self.machines["M2"].set_operator(self.workers["W2"])
        self.machines["M3"].set_operator(self.workers["W3"])

        # === Zone finale ===
        self.stockfinal = Zone(nl_interface, x=40, y=50, shape="house", size=3, color=25,
                               name="StockFinal", labelcolor=15)

        # === Création des jobs ===
        self.jobs = []
        for j in [ "J1" , "J2" , "J3" , "J4" , "J5" , "J6" , "J7" , "J8"]:
            self.jobs.append(Job(nl_interface, j, routing[j]))

        # On calcule la durée totale pour chaque job
        self.totalDuration_job = {}
        for job in self.jobs:
            self.totalDuration_job[job.job_name] = sum(d for (_,d) in job.routing_sequence)
        self.cumulTime_job = {job.job_name: 0.0 for job in self.jobs}
        self.finished_jobs_count = 0

        # Première opération
        for job in self.jobs:
            op = job.get_next_operation()
            if op:
                self.machines[op.machine_name].add_operation(op)
                job.update_representation(self.machines[op.machine_name].obj)

        # ==================== FIGURE 1 : cumul par job ====================
        global fig_jobs, ax_jobs
        self.fig_jobs = fig_jobs
        self.ax_jobs = ax_jobs
        self.lines_by_job = {}
        self.xdata = []
        # On stocke les data cumul dans 'cumulTime_by_job'
        self.cumulTime_by_job = {}
        colors = {"J1":"red","J2":"green","J3":"blue"}

        # On ne fixe pas de ylim, pour laisser autoscale
        self.ax_jobs.set_autoscaley_on(True)

        for job in self.jobs:
            jname = job.job_name
            (line,) = self.ax_jobs.plot([], [], color=colors[jname], label=jname)
            self.lines_by_job[jname] = line
            self.cumulTime_by_job[jname] = []  # liste d'ordonnées

        self.ax_jobs.legend()
        self.ax_jobs.set_xlabel("Temps (tick)")
        self.ax_jobs.set_ylabel("Temps cumulé du job (valeur)")

        # ==================== FIGURE 2 : fatigue / exp / vitesse ====================
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
            axw.set_title(f"{wName}")

            (line_fat,) = axw.plot([], [], 'r-', label="fatigue")
            (line_exp,) = axw.plot([], [], 'g-', label="experience")
            (line_spd,) = axw.plot([], [], 'b-', label="speed")

            axw.legend()
            self.worker_lines[wName] = {
                "fatigue": line_fat,
                "experience": line_exp,
                "speed": line_spd
            }

        # ==================== FIGURE 3 : état Markov (0..3) ====================
        global fig_states, ax_states
        self.fig_states = fig_states
        self.ax_states = ax_states
        self.state_timeline = {}
        self.state_lines = {}

        for i, wName in enumerate(wList):
            self.state_timeline[wName] = {
                "t": [],
                "state": []
            }
            axst = self.ax_states[i]
            axst.set_autoscaley_on(True)
            axst.set_yticks([0,1,2,3])
            axst.set_title(f"{wName}")

            (line_sta,) = axst.plot([], [], 'k-', label="état")
            axst.legend()
            self.state_lines[wName] = line_sta

    def run(self, total_ticks):
        for tick in range(total_ticks):
            time.sleep(speed_tik)

            # (1) Markov
            for w in self.workers.values():
                w.step_markov()

            # (2) cumul temps
            for machine in self.machines.values():
                op_in_progress = machine.operation_in_progress
                if op_in_progress:
                    w_speed = machine.operator.def_vit(tick)
                    self.cumulTime_job[op_in_progress.job_name] += pas_tick * w_speed

                # process => fin d'op => suite
                result = machine.process(tick)
                if result:
                    job = self.find_job_by_name(result.job_name)
                    if job:
                        job.advance()
                        if job.finished:
                            self.finished_jobs_count += 1
                            job.update_representation(self.stockfinal.obj)
                            print(f"{job.job_name} terminé => {self.finished_jobs_count} jobs finis")
                        else:
                            nxt_op = job.get_next_operation()
                            next_machine = self.machines[nxt_op.machine_name]
                            next_machine.add_operation(nxt_op)
                            job.update_representation(next_machine.obj)

            # (3) Mise à jour Figures
            self.update_plot_jobs(tick)
            self.update_plot_workers(tick)
            self.update_plot_states(tick)

            # condition d'arrêt
            if self.finished_jobs_count == len(self.jobs):
                print(f"Tous les jobs terminés au tick={tick}")
                break

        print(f"Simulation terminée. jobs finis = {self.finished_jobs_count}")
        plt.ioff()
        plt.show()

    def update_plot_jobs(self, tick):
        """
        Figure 1 : progression cumulée (valeur absolue)
        """
        self.xdata.append(tick)
        for job in self.jobs:
            jn = job.job_name
            val = self.cumulTime_job[jn]
            # On ajoute la nouvelle valeur dans cumulTime_by_job
            self.cumulTime_by_job[jn].append(val)

            line = self.lines_by_job[jn]
            line.set_xdata(self.xdata)
            line.set_ydata(self.cumulTime_by_job[jn])

        self.ax_jobs.relim()
        self.ax_jobs.autoscale_view()

        # Forcer le rafraîchissement de la figure jobs
        self.fig_jobs.canvas.draw_idle()
        self.fig_jobs.canvas.flush_events()

        time.sleep(0.01)

    def update_plot_workers(self, tick):
        """
        Figure 2 : fatigue / experience / vitesse
        """
        wList = ["W1","W2","W3"]
        for wName in wList:
            wObj = self.workers[wName]
            p = wObj.profile
            self.worker_timeline[wName]["t"].append(tick)

            # calcul fatigue / exp / speed
            ftg = new_fatigue(tick, p.f_init, p.lamF, p.L)
            exp = new_experience(tick, p.e_init, p.lamE, p.L)
            spd = wObj.def_vit(tick)  # = ftg + exp

            self.worker_timeline[wName]["fatigue"].append(ftg)
            self.worker_timeline[wName]["experience"].append(exp)
            self.worker_timeline[wName]["speed"].append(spd)

        # Mise à jour plot
        for i, wName in enumerate(wList):
            axw = self.ax_workers[i]
            line_f = self.worker_lines[wName]["fatigue"]
            line_e = self.worker_lines[wName]["experience"]
            line_s = self.worker_lines[wName]["speed"]

            tvals = self.worker_timeline[wName]["t"]
            fvals = self.worker_timeline[wName]["fatigue"]
            evals = self.worker_timeline[wName]["experience"]
            svals = self.worker_timeline[wName]["speed"]

            line_f.set_xdata(tvals)
            line_f.set_ydata(fvals)
            line_e.set_xdata(tvals)
            line_e.set_ydata(evals)
            line_s.set_xdata(tvals)
            line_s.set_ydata(svals)

            axw.relim()
            axw.autoscale_view()

        self.fig_workers.canvas.draw_idle()
        self.fig_workers.canvas.flush_events()

        time.sleep(0.01)

    def update_plot_states(self, tick):
        """
        Figure 3 : état Markov (0..3) par ouvrier
        """
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

        time.sleep(0.01)

    def find_job_by_name(self, name):
        for j in self.jobs:
            if j.job_name == name:
                return j
        return None

###################################################
#           10) MAIN
###################################################
if __name__=="__main__":
    from netlogopy2.netlogopy import run_netlogo
    nl_interface = run_netlogo("C:/Program Files/NetLogo 6.2.2")

    sim = JobShopSimulation(nl_interface)
    sim.run(EOS)

    nl_interface.close_model()
