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

# netlogopy for NetLogo embedding / turtle graphics
from netlogopy2.netlogopy import (
    nl_output_print,
    resize_world,
    set_background,
    PyTurtle,
    run_netlogo
)
from newf import dynamic_opt

plt.ion()  # Interactive plotting

###################################################
# 1) FIGURES MATPLOTLIB (INTERACTIF)
###################################################
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
pas_tick = 1
speed_tik = 0.3   # pause time between ticks in seconds
EOS = 7200        # max number of ticks in the simulation
cycle = 400
fintcycle = 90
deta_group = 10   # Delay (in ticks) between calls to dynamic re-optimization
pas_reoptimisation = 10

L_period = 4800
f_init = 0.0
e_init = 0.0

###################################################
# 3) FONCTIONS MATHÉMATIQUES
###################################################
def update_fatigue(current_fatigue: float, is_working: bool,
                   lam: float = 0.01, beta: float = 1.0, gamma: float = 0.02,
                   dt: float = 1.0) -> float:
    """
    Met à jour la fatigue en fonction de l'état (is_working).
    """
    if is_working:
        # L'ouvrier accumule de la fatigue
        new_f = 1.0 - (1.0 - current_fatigue) * math.exp(-lam * beta * dt)
    else:
        # L'ouvrier récupère, la fatigue diminue
        new_f = current_fatigue * math.exp(-gamma * dt)
    return new_f

def new_experience(t, current_e, experience_e, e_min, e_max, k, t0,
                   is_working, wrk):
    """
    Calcule la nouvelle expérience d'un ouvrier.
    Si is_working est True, on applique une courbe logistique,
    sinon on conserve current_e.
    """
    if is_working:
        # logistic growth from e_min to e_max
        return e_min + (e_max - e_min) / (1.0 + math.exp(-k * (t - t0 - wrk.cumul_pause)))
    else:
        return experience_e

def new_speed(t, f_init, lamF, e_init, lamE, L):
    nb_segments = floor(t / L)
    e_val = e_init + lamE * nb_segments
    f_val = f_init * math.exp(-lamF * (t % L))
    return max(0.0, e_val - f_val)

###################################################
# 4) CLASSE Worker (AVEC Profile INTÉGRÉE)
###################################################
class Worker:
    """
    Un ouvrier, avec un profil interne décrivant ses caractéristiques
    (fatigue, expérience, matrice Markov, etc.).
    """

    class CProfile:
        """
        Profil interne d'un ouvrier, incluant :
          - name : nom du profil
          - f_init, lamF, e_init, lamE, L : divers paramètres de vitesse/fatigue
          - lam, beta, gamma : paramètres de fatigue
          - e_min, e_max, k, t0 : courbe logistique pour expérience
          - punct : matrice de transition Markov (4x4)
        """
        def __init__(self, fields={}):
            self.__dict__.update(fields)

        def update_fields(self, fields):
            self.__dict__.update(fields)

    def __init__(self, nl_interface, name, dprofile,
                 znp1_obj, znp2_obj, znp3_obj, znp4_obj,
                 machine_obj, color=55):
        self.name = name
        self.profile = self.CProfile(dprofile)
        self.num_operations = 0
        self.nht = 0
        self.current_state = 0
        self.fatigue_level = self.profile.f_init
        self.experience = self.profile.e_init
        self.current_e = self.profile.e_init
        self.cumul_pause = 0

        self.rep = PyTurtle(nl_interface, x=0, y=0, shape="person_0",
                            size_shape=5, color=color, name=name,
                            labelcolor=color, fields={})
        self.rep.move_to(machine_obj)
        self.rep.fd(5)

        # 0..3 => machine or zone, 4 => "house"
        self.zone_by_state = {
            0: machine_obj,
            1: znp1_obj,
            2: znp2_obj,
            3: znp3_obj,
            4: znp4_obj
        }

    def def_vit(self, t):
        is_working = (self.current_state == 0)
        exp_val = new_experience(
            t,
            current_e=self.current_e,
            experience_e=self.experience,
            e_min=self.profile.e_min,
            e_max=self.profile.e_max,
            k=self.profile.k,
            t0=self.profile.t0,
            is_working=is_working,
            wrk=self
        )
        self.experience = exp_val
        # speed = experience - fatigue
        speed_val = max(0.0, exp_val - self.fatigue_level)
        return speed_val

    def update_profile(self, new_profile, reset_fatigue=False):
        self.profile = self.CProfile(new_profile)
        if reset_fatigue:
            self.fatigue_level = self.profile.f_init

    def step_markov(self, t):
        cycle_24 = t % cycle
        is_working = (self.current_state in [0])

        exp_val = new_experience(
            t,
            current_e=self.current_e,
            experience_e=self.experience,
            e_min=self.profile.e_min,
            e_max=self.profile.e_max,
            k=self.profile.k,
            t0=self.profile.t0,
            is_working=is_working,
            wrk=self
        )

        # Phase 1 (0..fintcycle): Markov normal states 0..3
        if 0 <= cycle_24 < fintcycle:
            if self.current_state == 4:
                self.current_state = 0
                self.current_e = exp_val - self.experience
                self.rep.move_to(self.zone_by_state[0])
                self.rep.fd(5)

            # Transition Markov: use the matrix 'punct'
            p_line = self.profile.punct[self.current_state]
            new_state = np.random.choice([0, 1, 2, 3], p=p_line)
            if new_state != self.current_state:
                self.current_state = new_state
                self.rep.move_to(self.zone_by_state[new_state])
                self.rep.fd(5)

        # Phase 2 (fintcycle..cycle): "house"
        elif fintcycle <= cycle_24:
            if self.current_state != 4:
                self.current_state = 4
                self.rep.move_to(self.zone_by_state[4])
                self.rep.fd(5)

        # update fatigue
        is_working = (self.current_state == 0)
        self.fatigue_level = update_fatigue(
            current_fatigue=self.fatigue_level,
            is_working=is_working,
            lam=self.profile.lam,
            beta=self.profile.beta,
            gamma=self.profile.gamma,
            dt=1.0
        )
        self.cumul_pause += (1 - int(is_working))

    def update_label(self, text):
        self.rep.set_label(text)

###################################################
# 6) ROUTING JOBS ET JOB_COUNTS
###################################################
job_counts = {
    "J1": 3 ,
    "J2": 1 ,
    "J3": 1 ,
}

routing = {
    "J1": [("M1", 23), ("M3", 26), ("M2", 33)],
    "J2": [("M2", 27), ("M1", 40), ("M3", 35)],
    "J3": [("M3", 35), ("M2", 28), ("M1", 51)],
}

###################################################
# 7) IMPORT ET EFFACEMENT
###################################################
os.system('cls' if os.name == 'nt' else 'clear')

###################################################
# 8) CLASSES ENTITÉS : Zone, Operation, Job, Machine
###################################################
class Zone:
    def __init__(self, nl_interface, x, y, shape, size, color, name, labelcolor):
        self.obj = PyTurtle(nl_interface, x=x, y=y, shape=shape,
                            size_shape=size, color=color, name=name,
                            labelcolor=labelcolor,
                            fields={"worker_encour": None, "free": True})
        self.name = name

class Operation:
    """
    Operation now stores a direct reference to the Job object
    (instead of just job_name), so we don't need find_job_by_name().
    """
    def __init__(self, job_obj, machine_name, duration, op_index):
        self.job_obj = job_obj           # direct reference to the job
        self.machine_name = machine_name
        self.duration = duration
        self.start_time = None
        self.op_index = op_index         # which operation index in the job

class Job:
    def __init__(self, nl_interface, job_name, routing_sequence):
        self.job_name = job_name
        self.routing_sequence = routing_sequence
        self.current_op_index = 0
        self.finished = False
        # For NetLogo representation:
        index_str = str(min(int(job_name[1:]), 5)) if job_name[1:].isdigit() else "1"
        shape_name = "p_robot0" + index_str
        self.rep = PyTurtle(nl_interface, x=5, y=5,
                            shape=shape_name, size_shape=5,
                            color=15, name=job_name, labelcolor=15, fields={})
        self.total_duration = sum(d for (_, d) in routing_sequence)

        # Track partial progress for each operation
        self.elapsed_time_by_op = [0.0] * len(routing_sequence)

    def get_next_operation(self):
        if self.current_op_index < len(self.routing_sequence):
            machine_name, duration = self.routing_sequence[self.current_op_index]
            return Operation(self, machine_name, duration, self.current_op_index)
        return None

    def advance(self):
        self.current_op_index += 1
        if self.current_op_index >= len(self.routing_sequence):
            self.finished = True

    def update_representation(self, new_target):
        self.rep.move_to(new_target)

class Machine:
    def __init__(self, nl_interface, name, x, y, shape="machine", size=4, color=15):
        self.name = name
        self.queue = []
        self.operation_in_progress = None
        self.operator = None
        self.obj = PyTurtle(nl_interface, x=x, y=y, shape=shape,
                            size_shape=size, color=color, name=name,
                            labelcolor=color, fields={"busy": False})
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
        """
        On each tick, if there's an operation in progress, we do partial processing
        until it's done, or keep going next tick. No 'find_job_by_name' needed because
        Operation has a direct reference to the Job.
        """
        if not self.operator:
            return None
        if self.operator.current_state != 0:
            return None

        tick_time = tick
        # If there's no operation_in_progress, start one from queue
        if self.operation_in_progress is None and self.queue:
            self.operation_in_progress = self.queue.pop(0)
            self.operation_in_progress.start_time = tick_time
            self.obj.fields["busy"] = True
            self._update_label_queue()

        # If we have an operation in progress, do partial progress
        if self.operation_in_progress:
            op = self.operation_in_progress
            job_obj = op.job_obj
            op_index = op.op_index

            # how much to process this step
            w_speed = self.operator.def_vit(tick_time)
            # partial progress for this single tick
            partial = pas_tick * w_speed

            # increment the operation's elapsed time
            job_obj.elapsed_time_by_op[op_index] += partial

            # if we've finished the total needed time, it's done
            if job_obj.elapsed_time_by_op[op_index] >= op.duration:
                # clamp to avoid going over
                job_obj.elapsed_time_by_op[op_index] = op.duration

                finished_op = self.operation_in_progress
                self.operation_in_progress = None
                self.obj.fields["busy"] = False
                self.operator.num_operations += 1
                self._update_label_queue()
                return finished_op

        return None

###################################################
# 10) LA CLASSE PRINCIPALE JobShopSimulation
###################################################
class JobShopSimulation:
    def __init__(self, nl_interface):
        resize_world(nl_interface, 0, 60, 0, 60)
        # Adjust path or remove if not needed
        set_background(nl_interface, "D:/cphs2024/netlogopy.png")

        self.nl_interface = nl_interface

        # Zones
        self.znp1 = Zone(nl_interface, 5, 50, "infirmary", 3, 25, "ZNP1", 25)
        self.znp2 = Zone(nl_interface, 15, 50, "calling", 3, 35, "ZNP2", 35)
        self.znp3 = Zone(nl_interface, 25, 50, "cantine", 3, 45, "ZNP3", 45)
        self.znp4 = Zone(nl_interface, 55, 50, "house", 3, 55, "house", 55)

        # Machines
        self.machines = {
            "M1": Machine(nl_interface, "M1", 10, 30, "machine", 4, 15),
            "M2": Machine(nl_interface, "M2", 30, 30, "machine2", 4, 55),
            "M3": Machine(nl_interface, "M3", 50, 30, "machine3", 4, 55)
        }

        # Example Worker Profiles
        profile_0 = {
            "name": "prf0",
            "f_init": f_init,
            "lamF": 0.0,
            "e_init": e_init,
            "lamE": 0.0,
            "L": L_period,
            "lam": 0.01,
            "beta": 1.0,
            "gamma": 0.02,
            "e_min": 0.1,
            "e_max": 6.0,
            "k": 0.015,
            "t0": 200,
            "punct": [
                [1, 0, 0, 0],
                [0.5, 0.5, 0, 0],
                [0.4, 0.3, 0.2, 0.1],
                [1, 0, 0, 0]
            ]
        }

        profile_1 = {
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
        }

        profile_2 = {
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
        }

        # Create Workers
        wrk1 = Worker(nl_interface, "worker_1_" + profile_0["name"],
                      profile_0,
                      self.znp1.obj, self.znp2.obj, self.znp3.obj, self.znp4.obj,
                      self.machines["M1"].obj, color=14)
        wrk2 = Worker(nl_interface, "worker_2_" + profile_1["name"],
                      profile_1,
                      self.znp1.obj, self.znp2.obj, self.znp3.obj, self.znp4.obj,
                      self.machines["M2"].obj, color=55)
        wrk3 = Worker(nl_interface, "worker_3_" + profile_2["name"],
                      profile_1,
                      self.znp1.obj, self.znp2.obj, self.znp3.obj, self.znp4.obj,
                      self.machines["M3"].obj, color=95)

        self.workers = {"W1": wrk1, "W2": wrk2, "W3": wrk3}

        self.machines["M1"].set_operator(self.workers["W1"])
        self.machines["M2"].set_operator(self.workers["W2"])
        self.machines["M3"].set_operator(self.workers["W3"])

        # Example "stock final" zone
        self.stockfinal = Zone(nl_interface, 40, 50, "house", 3, 25, "StockFinal", 15)

        # Build the list of jobs
        self.jobs = []
        for jname, nb in job_counts.items():
            for i in range(nb):
                # e.g. "J1_1" if there's more than 1
                job_id = jname if nb == 1 else f"{jname}_{i+1}"
                self.jobs.append(Job(nl_interface, job_id, routing[jname]))

        # Track each job's total & partial progress
        self.totalDuration_job = {
            job.job_name: sum(d for (_, d) in job.routing_sequence)
            for job in self.jobs
        }
        self.cumulTime_job = {job.job_name: 0.0 for job in self.jobs}
        self.finished_jobs_count = 0

        # Assign the first operation of each job
        for job in self.jobs:
            op = job.get_next_operation()
            if op:
                self.machines[op.machine_name].add_operation(op)
                job.update_representation(self.machines[op.machine_name].obj)

        # For plotting
        global fig_jobs, ax_jobs
        self.fig_jobs = fig_jobs
        self.ax_jobs = ax_jobs
        self.lines_by_job = {}
        self.xdata = []
        self.cumulTime_by_job = {}

        color_map = ["red", "green", "blue", "orange",
                     "purple", "brown", "cyan", "magenta",
                     "lime", "pink"]
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
            self.worker_timeline[wName] = {
                "t": [], "fatigue": [], "experience": [], "speed": []
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

        global fig_states, ax_states
        self.fig_states = fig_states
        self.ax_states = ax_states
        self.state_timeline = {}
        self.state_lines = {}
        self.speed = {
            "W1": {"M1": 1.0, "M2": 1.0, "M3": 1.0},
            "W2": {"M1": 1.0, "M2": 1.0, "M3": 1.0},
            "W3": {"M1": 1.0, "M2": 1.0, "M3": 1.0}
        }
        for i, wName in enumerate(wList):
            self.state_timeline[wName] = {"t": [], "state": []}
            axst = self.ax_states[i]
            axst.set_autoscaley_on(True)
            axst.set_yticks([0, 1, 2, 3, 4])
            axst.set_title(wName)
            (lsta,) = axst.plot([], [], 'k-', label="état")
            axst.legend()
            self.state_lines[wName] = lsta

        self.current_tick = 0

    def dynamic_opt2(self, i):
        """
        Call our Gurobi-based dynamic scheduling with partial progress
        """
        nl_output_print(self.nl_interface,
                        f"Début dynamic_opt2 => re-scheduling at tick={self.current_tick}, iteration={i}")
        dynamic_opt(self, i)
        nl_output_print(self.nl_interface,
                        f"Fin dynamic_opt2 => iteration={i}")

    def run(self, total_ticks):
        i_group = 0
        for tick in range(total_ticks):
            self.current_tick = tick
            # time.sleep(speed_tik)

            # 1) Markov step
            for w in self.workers.values():
                w.step_markov(tick)

            # 2) Re-optimization every 'deta_group' ticks
            if tick % deta_group == 0 and tick > 0:
                i_group += 1
                self.dynamic_opt2(i_group)

            # 3) Machines process
            for machine in self.machines.values():
                op_in_progress = machine.operation_in_progress
                if op_in_progress and machine.operator:
                    # accumulate time for the job in our aggregator
                    w_speed = machine.operator.def_vit(tick)
                    self.cumulTime_job[op_in_progress.job_obj.job_name] += pas_tick * w_speed

                result = machine.process(tick)  # might return a finished operation
                if result:
                    # we finished an operation -> advance job
                    job_obj = result.job_obj
                    job_obj.advance()

                    if job_obj.finished:
                        self.finished_jobs_count += 1
                        job_obj.update_representation(self.stockfinal.obj)
                        nl_output_print(self.nl_interface,
                                        f"{job_obj.job_name} terminé => {self.finished_jobs_count} finis (tick={tick})")
                        print(f"{job_obj.job_name} terminé => {self.finished_jobs_count} jobs finis | tick={tick}")
                    else:
                        # get the next op, if any, and add it to the machine queue
                        nxt_op = job_obj.get_next_operation()
                        if nxt_op:
                            next_machine = self.machines[nxt_op.machine_name]
                            next_machine.add_operation(nxt_op)
                            job_obj.update_representation(next_machine.obj)

            # 4) Update plots
            self.update_plot_jobs(tick)
            self.update_plot_workers(tick)
            self.update_plot_states(tick)

            # 5) Stop if all done
            if self.finished_jobs_count == len(self.jobs):
                nl_output_print(self.nl_interface, f"Tous les jobs terminés au tick={tick}")
                print(f"Tous les jobs terminés au tick={tick}")
                break

        nl_output_print(self.nl_interface,
                        f"Simulation terminée. Jobs finis = {self.finished_jobs_count}")
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
            exp_val = wObj.experience
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

###################################################
# 11) MAIN
###################################################
if __name__ == "__main__":
    nl_interface = run_netlogo("C:/Program Files/NetLogo 6.2.2")
    sim = JobShopSimulation(nl_interface)
    sim.run(EOS)
    nl_interface.close_model()
