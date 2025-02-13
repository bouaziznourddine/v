import time, os, random
from math import floor
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------------------------
# PARAMÈTRES GLOBAUX DE LA SIMULATION
# ------------------------------------------------------------------

# Durée d'un tick et délai entre ticks
pas_tick = 1          # 1 tick = 1 unité de temps
speed_tik = 0.1       # 0.1 seconde entre chaque tick
EOS = 15              # Simulation de 15 ticks

# ------------------------------------------------------------------
# CONFIGURATION DES PROFILS D'OUVRIERS
# ------------------------------------------------------------------

class profile():
    def __init__(self, fields={}):
        self.__dict__.update(fields)

if True:
    profile_0 = profile(fields={
        "punct": [[1, 0, 0, 0]] * 4,  # Pour ce profil, distribution simple
        "vitesse": 1,
        "alf_exp": 0,      # Pas d'expérience
        "alf_ftig": 0,     # Pas de fatigue
        "qualit": 1
    })
    profile_1 = profile(fields={
        "punct": [[0.9, 0.1, 0, 0],
                  [0.95, 0.05, 0, 0],
                  [1, 0, 0, 0],
                  [1, 0, 0, 0]],
        "vitesse": 1,
        "alf_exp": 0.1,
        "alf_ftig": 0.1,
        "qualit": 1
    })
    profile_2 = profile(fields={
        "punct": [[0.8, 0.2, 0, 0],
                  [0.6, 0.2, 0.1, 0.1],
                  [0, 0.3, 0.4, 0.3],
                  [0, 0.3, 0.4, 0.3]],
        "vitesse": 1,
        "alf_exp": 0.1,
        "alf_ftig": 0.1,
        "qualit": 1
    })

# ------------------------------------------------------------------
# CONFIGURATION DU MODÈLE POUR LE JOB SHOP
# ------------------------------------------------------------------

# Définition des machines et des jobs
M = ["M1", "M2", "M3"]
jobs_names = ["J1", "J2", "J3"]

# Routage pour chaque job
# J1 aura des opérations de courte durée : 3, 2, 4 (total = 9 ticks)
# J2 et J3 auront des durées de 10 ticks par opération (total = 30 ticks)
routing = {
    "J1": [("M1", 3), ("M3", 2), ("M2", 4)],
    "J2": [("M2", 10), ("M1", 10), ("M3", 10)],
    "J3": [("M3", 10), ("M2", 10), ("M1", 10)]
}

# ------------------------------------------------------------------
# FONCTIONS MATHÉMATIQUES
# ------------------------------------------------------------------

def fatigue(data):
    t, f = data[0], data[1]
    r = 0 if f == 0 else np.random.normal(0, 0.01)
    return 1 - ((t % 480) * f) + r

def experience(data):
    t, e = data[0], data[1]
    return floor(t / 480) * e

# ------------------------------------------------------------------
# FONCTIONS POUR LA VITESSE DES OUVRIERS
# ------------------------------------------------------------------

def vit_Wkr0(wrk=None, tem=0, numprd=0):
    wrprofile = wrk.profile
    return experience([tem, wrprofile.alf_exp]) + fatigue([tem, wrprofile.alf_ftig])
def vit_Wkr1(wrk=None, tem=0, numprd=0):
    return vit_Wkr0(wrk, tem, numprd)
def vit_Wkr2(wrk=None, tem=0, numprd=0):
    return vit_Wkr0(wrk, tem, numprd)
def vit_Wkr3(wrk=None, tem=0, numprd=0):
    return vit_Wkr0(wrk, tem, numprd)
def vit_Wkr4(wrk=None, tem=0, numprd=0):
    return vit_Wkr0(wrk, tem, numprd)
def vit_Wkr5(wrk=None, tem=0, numprd=0):
    return vit_Wkr0(wrk, tem, numprd)

def update_wk(wrk, lzone):
    if wrk.zon_now not in lzone:
        v = 0
    else:
        v = lzone.index(wrk.zon_now) + 1
    M_arr = np.array(wrk.profile.punct)
    next_zone = np.random.choice(np.arange(0, 4), p=M_arr[v])
    return next_zone

# ------------------------------------------------------------------
# IMPORTATION DES MODULES NETLOGO
# ------------------------------------------------------------------
from netlogopy2.netlogopy import netlogoshow, resize_world, set_background, NL_Street, PyTurtle

os.system('cls')

# ------------------------------------------------------------------
# CLASSES POUR LES ENTITÉS DU JOB SHOP
# ------------------------------------------------------------------

class Zone:
    def __init__(self, nl_interface, x, y, shape, size, color, name, labelcolor):
        self.obj = PyTurtle(nl_interface, x=x, y=y, shape=shape, size_shape=size, color=color,
                            name=name, labelcolor=labelcolor,
                            fields={"worker_encour": None, "free": True})
        self.name = name

class Stock:
    def __init__(self, nl_interface, x, y, shape, size, color, name):
        self.obj = PyTurtle(nl_interface, x=x, y=y, shape=shape, size_shape=size, color=color,
                            name=name, fields={})
        self.name = name

class Machine:
    def __init__(self, nl_interface, name, x, y, shape="machine", size=4, color=15):
        self.name = name
        self.queue = []  # File d'attente des opérations
        self.operation_in_progress = None
        self.operator = None  # L'opérateur est obligatoire pour que la machine fonctionne
        self.obj = PyTurtle(nl_interface, x=x, y=y, shape=shape,
                            size_shape=size, color=color, name=name, labelcolor=color,
                            fields={"busy": False})
    
    def set_operator(self, worker):
        self.operator = worker

    def add_operation(self, operation):
        self.queue.append(operation)

    def process(self, tick):
        # La machine ne peut fonctionner que si un opérateur est assigné
        if self.operator is None:
            return None

        tick_time = tick * pas_tick

        if self.operation_in_progress is None and self.queue:
            self.operation_in_progress = self.queue.pop(0)
            self.operation_in_progress.start_time = tick_time
            self.obj.fields["busy"] = True

        if self.operation_in_progress:
            worker_speed = self.operator.def_vit(tick_time)
            if (tick_time - self.operation_in_progress.start_time) * worker_speed >= self.operation_in_progress.duration:
                finished_op = self.operation_in_progress
                self.operation_in_progress = None
                self.obj.fields["busy"] = False
                self.operator.num_operations += 1
                return finished_op
        return None

class Operation:
    def __init__(self, job_name, machine_name, duration):
        self.job_name = job_name
        self.machine_name = machine_name
        self.duration = duration
        self.start_time = None

class Job:
    def __init__(self, nl_interface, job_name, routing_sequence):
        self.job_name = job_name
        self.routing_sequence = routing_sequence  # Liste de tuples (machine_name, duration)
        self.current_op_index = 0
        self.finished = False
        # Pour la représentation graphique, on utilise la forme "circle"
        self.rep = PyTurtle(nl_interface, x=5, y=5, shape="circle", size_shape=2, color=15,
                             name=job_name, labelcolor=15, fields={})

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

# Classe Worker avec représentation graphique et profil
class Worker:
    def __init__(self, nl_interface, name, profile):
        self.name = name
        self.profile = profile
        self.num_operations = 0  # Nombre d'opérations traitées
        self.nht = 0             # Nombre de ticks travaillés
        # Pour l'affichage, on utilise la forme "person_0"
        self.rep = PyTurtle(nl_interface, x=0, y=0, shape="person_0", size_shape=3, color=55,
                            name=name, labelcolor=55, fields={})
        self.def_vit = lambda t: experience([t, profile.alf_exp]) + fatigue([t, profile.alf_ftig])
        # Initialisation de la zone actuelle (peut être mise à jour par update_wk)
        self.zon_now = None

# ------------------------------------------------------------------
# CLASSE DE SIMULATION DU JOB SHOP
# ------------------------------------------------------------------

class JobShopSimulation:
    def __init__(self, nl_interface):
        self.nl_interface = nl_interface
        from netlogopy2.netlogopy import resize_world, set_background

        # Configuration de l'environnement NetLogo
        resize_world(nl_interface, 0, 60, 0, 60)
        set_background(nl_interface, "D:/cphs2024/netlogopy.png")

        # Création des machines
        self.machines = {
            "M1": Machine(nl_interface, "M1", x=10, y=30, shape="machine", size=4, color=15),
            "M2": Machine(nl_interface, "M2", x=30, y=30, shape="machine2", size=4, color=55),
            "M3": Machine(nl_interface, "M3", x=50, y=30, shape="machine3", size=4, color=55)
        }

        # Création des ouvriers et affectation aux machines
        self.workers = {
            "W1": Worker(nl_interface, "worker_1", profile_0),
            "W2": Worker(nl_interface, "worker_2", profile_1),
            "W3": Worker(nl_interface, "worker_3", profile_2)
        }
        self.machines["M1"].set_operator(self.workers["W1"])
        self.machines["M2"].set_operator(self.workers["W2"])
        self.machines["M3"].set_operator(self.workers["W3"])
        # Pour update_wk, initialiser la zone de chaque worker à celle de la machine à laquelle il est assigné
        self.workers["W1"].zon_now = self.machines["M1"].obj
        self.workers["W2"].zon_now = self.machines["M2"].obj
        self.workers["W3"].zon_now = self.machines["M3"].obj

        # Création des jobs avec leur séquence d'opérations (routage)
        self.jobs = []
        for j in ["J1", "J2", "J3"]:
            self.jobs.append(Job(self.nl_interface, j, routing[j]))

        # Pour démarrer, ajouter la première opération de chaque job à la machine correspondante
        for job in self.jobs:
            op = job.get_next_operation()
            if op:
                self.machines[op.machine_name].add_operation(op)
                job.update_representation(self.machines[op.machine_name].obj)

    def run(self, total_ticks):
        finished_jobs_count = 0

        for tick in range(total_ticks):
            time.sleep(speed_tik)
            # Traitement des machines
            for machine in self.machines.values():
                finished_op = machine.process(tick)
                if finished_op:
                    job = self.find_job_by_name(finished_op.job_name)
                    if job:
                        job.advance()
                        if job.finished:
                            finished_jobs_count += 1
                            print(f"Job {job.job_name} terminé au tick {tick}")
                        else:
                            next_op = job.get_next_operation()
                            self.machines[next_op.machine_name].add_operation(next_op)
                            job.update_representation(self.machines[next_op.machine_name].obj)
            if finished_jobs_count == len(self.jobs):
                print(f"Tous les jobs ({finished_jobs_count}) sont terminés au tick {tick}.")
                break

        print(f"Simulation terminée. Jobs finis : {finished_jobs_count}/{len(self.jobs)}")

    def find_job_by_name(self, job_name):
        for j in self.jobs:
            if j.job_name == job_name:
                return j
        return None

# ------------------------------------------------------------------
# POINT D'ENTRÉE DU SCRIPT
# ------------------------------------------------------------------

if __name__ == "__main__":
    from netlogopy2.netlogopy import run_netlogo
    nl_interface = run_netlogo("C:/Program Files/NetLogo 6.2.2")

    sim = JobShopSimulation(nl_interface)
    total_ticks = EOS  # EOS est 15, donc avec les durées choisies, seul J1 se termine.
    sim.run(total_ticks)

    nl_interface.close_model()
