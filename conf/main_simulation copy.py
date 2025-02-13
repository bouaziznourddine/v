import time, os, random
from math import floor
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------------------------
# PARAMÈTRES GLOBAUX
# ------------------------------------------------------------------

pas_tick = 1       # 1 tick = 1 unité de temps
speed_tik = 0.5    # Délai entre ticks (0.1 seconde)
EOS = 15           # Durée totale de la simulation (15 ticks)

# ------------------------------------------------------------------
# CLASSE profile
# ------------------------------------------------------------------

class profile():
    """
    Représente un profil d'ouvrier incluant une matrice 'punct' (chaîne de Markov)
    et d'autres paramètres (alf_exp, alf_ftig, etc.).
    """
    def __init__(self, fields={}):
        self.__dict__.update(fields)

# ------------------------------------------------------------------
# DÉFINITION DES DIFFÉRENTS PROFILS
# ------------------------------------------------------------------

# Dans cet exemple, nous allons utiliser 2 états (état 0 = machine, état 1 = zone NP).
# On donne des matrices de transition ponct = 2x2 par exemple.
# Ex: si ponct[0] = [0.8, 0.2], 80% de rester en machine, 20% d'aller en ZNP.

profile_0 = profile({
    "alf_exp": 0.0,
    "alf_ftig": 0.0,
    "punct": [
        [0.8, 0.2],  # si ouvrier en état 0 -> [p(stay0), p(go1)]
        [0.5, 0.5]   # si ouvrier en état 1 -> [p(go0), p(stay1)]
    ]
})

profile_1 = profile({
    "alf_exp": 0.1,
    "alf_ftig": 0.1,
    "punct": [
        [0.7, 0.3],
        [0.4, 0.6]
    ]
})

profile_2 = profile({
    "alf_exp": 0.1,
    "alf_ftig": 0.1,
    "punct": [
        [0.9, 0.1],
        [0.3, 0.7]
    ]
})

# ------------------------------------------------------------------
# FONCTIONS MATHÉMATIQUES
# ------------------------------------------------------------------

def fatigue(data):
    t, f = data[0], data[1]
    if f == 0:
        r = 0
    else:
        r = np.random.normal(0, 0.01)
    return 1 - ((t % 480) * f) + r

def experience(data):
    t, e = data[0], data[1]
    return floor(t / 480) * e

def vit_Wkr(wrk=None, tem=0):
    """
    Exemple de vitesse calculée : experience + fatigue
    """
    if wrk is None:
        return 1
    p = wrk.profile
    return experience([tem, p.alf_exp]) + fatigue([tem, p.alf_ftig])

# ------------------------------------------------------------------
# ROUTAGE : 3 JOBS, 3 MACHINES
# ------------------------------------------------------------------

routing = {
    "J1": [("M1", 1), ("M3", 1), ("M2", 1)],
    "J2": [("M2", 1), ("M1", 1), ("M3", 1)],
    "J3": [("M3", 1), ("M2", 1), ("M1", 1)]
}

# ------------------------------------------------------------------
# IMPORTATION NETLOGO
# ------------------------------------------------------------------
from netlogopy2.netlogopy import netlogoshow, resize_world, set_background, NL_Street, PyTurtle

os.system('cls')

# ------------------------------------------------------------------
# CLASSES DU JOB SHOP
# ------------------------------------------------------------------

class Zone:
    """
    Représente une zone (productive ou non-productive).
    """
    def __init__(self, nl_interface, x, y, shape, size, color, name, labelcolor):
        self.obj = PyTurtle(nl_interface, x=x, y=y, shape=shape, size_shape=size,
                            color=color, name=name, labelcolor=labelcolor,
                            fields={"worker_encour": None, "free": True})
        self.name = name

class Machine:
    """
    Machine : ne traite des opérations que si l'ouvrier assigné est en état 0 (machine).
    """
    def __init__(self, nl_interface, name, x, y, shape="machine", size=4, color=15):
        self.name = name
        self.queue = []
        self.operation_in_progress = None
        self.operator = None
        self.obj = PyTurtle(nl_interface, x=x, y=y, shape=shape, size_shape=size,
                            color=color, name=name, labelcolor=color,
                            fields={"busy": False})
    
    def set_operator(self, worker):
        self.operator = worker

    def add_operation(self, operation):
        self.queue.append(operation)

    def process(self, tick):
        if self.operator is None:
            return None

        # La machine ne fonctionne que si l'ouvrier est en état 0 (machine)
        if getattr(self.operator, "current_state", 1) != 0:
            return None

        tick_time = tick * pas_tick

        # Commencer une opération si possible
        if self.operation_in_progress is None and self.queue:
            self.operation_in_progress = self.queue.pop(0)
            self.operation_in_progress.start_time = tick_time
            self.obj.fields["busy"] = True

        # Vérifier si l'opération en cours est terminée
        if self.operation_in_progress:
            w_speed = self.operator.def_vit(tick_time)
            duration = self.operation_in_progress.duration
            start_t = self.operation_in_progress.start_time
            if (tick_time - start_t) * w_speed >= duration:
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
    """
    Représente un job (liste d'opérations) + un marqueur graphique.
    """
    def __init__(self, nl_interface, job_name, routing_sequence):
        self.job_name = job_name
        self.routing_sequence = routing_sequence
        self.current_op_index = 0
        self.finished = False
        self.rep = PyTurtle(nl_interface, x=5, y=5, shape="p_robot0"+str(job_name[1:]), size_shape=5, color=15,
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

# ------------------------------------------------------------------
# CLASSE Worker avec chaîne de Markov 2 états
# ------------------------------------------------------------------

class Worker:
    """
    Worker disposant d'une matrice de transition 'punct' 2x2 :
      état 0 = machine, état 1 = zone non-productive
    """
    def __init__(self, nl_interface, name, profile, znp_obj, machine_obj):
        self.name = name
        self.profile = profile
        self.num_operations = 0
        self.nht = 0
        self.current_state = 0  # Commence sur la machine
        # Représentation
        self.rep = PyTurtle(nl_interface, x=0, y=0, shape="person_0", size_shape=5,
                            color=55, name=name, labelcolor=55, fields={})
        # On place le worker sur la machine (état 0)
        self.rep.move_to(machine_obj)
        self.rep.fd(5)

        # On stocke la zone NP et la machine
        self.znp_obj = znp_obj        # PyTurtle zone NP
        self.machine_obj = machine_obj  # PyTurtle machine
        self.def_vit = lambda t: vit_Wkr(self, t)

    def step_markov(self):
        """
        Évalue la transition Markov : p_line = profile.punct[current_state].
        new_state = 0 ou 1 choisi aléatoirement.
        Puis on déplace le worker en conséquence.
        """
        # p_line : ex. [0.8, 0.2]
        p_line = self.profile.punct[self.current_state]
        new_state = np.random.choice([0, 1], p=p_line)
        if new_state != self.current_state:
            self.current_state = new_state
            if new_state == 0:
                # Va sur la machine
                self.rep.move_to(self.machine_obj)
                self.rep.fd(5)
            else:
                # Va en zone NP
                self.rep.move_to(self.znp_obj)

# ------------------------------------------------------------------
# CLASSE DE SIMULATION
# ------------------------------------------------------------------

class JobShopSimulation:
    """
    Gère le job shop + Markov 2 états par ouvrier (machine / ZNP).
    """
    def __init__(self, nl_interface):
        from netlogopy2.netlogopy import resize_world, set_background
        resize_world(nl_interface, 0, 60, 0, 60)
        set_background(nl_interface, "D:/cphs2024/netlogopy.png")

        self.nl_interface = nl_interface

        # Création de 3 zones non-productive
        self.znp1 = Zone(nl_interface, x=5,  y=50, shape="house", size=3, color=25, name="ZNP1", labelcolor=25)
        self.znp2 = Zone(nl_interface, x=15, y=50, shape="house", size=3, color=35, name="ZNP2", labelcolor=35)
        self.znp3 = Zone(nl_interface, x=25, y=50, shape="house", size=3, color=45, name="ZNP3", labelcolor=45)

        # Machines
        self.machines = {
            "M1": Machine(nl_interface, "M1", x=10, y=30, shape="machine",  size=4, color=15),
            "M2": Machine(nl_interface, "M2", x=30, y=30, shape="machine2", size=4, color=55),
            "M3": Machine(nl_interface, "M3", x=50, y=30, shape="machine3", size=4, color=55)
        }

        # Création des workers
        # each worker a Markov 2 états (profile_0, profile_1, profile_2)
        # on associe W1->ZNP1, M1 ; W2->ZNP2, M2 ; W3->ZNP3, M3
        self.workers = {
            "W1": Worker(nl_interface, "worker_1", profile_0, self.znp1.obj, self.machines["M1"].obj),
            "W2": Worker(nl_interface, "worker_2", profile_1, self.znp2.obj, self.machines["M2"].obj),
            "W3": Worker(nl_interface, "worker_3", profile_2, self.znp3.obj, self.machines["M3"].obj),
        }
  # solver 
        # On affecte la machine à un worker
        self.machines["M1"].set_operator(self.workers["W1"])
        self.machines["M2"].set_operator(self.workers["W2"])
        self.machines["M3"].set_operator(self.workers["W3"])
  # solver 
        # Création des jobs
        self.jobs = []
        for j in ["J1", "J2", "J3"]:
            self.jobs.append(Job(nl_interface, j, routing[j]))

        # Ajout de la première opération de chaque job
        for job in self.jobs:
            op = job.get_next_operation()
            if op:
                self.machines[op.machine_name].add_operation(op)
                job.update_representation(self.machines[op.machine_name].obj)

    def run(self, total_ticks):
        finished_jobs_count = 0

        for tick in range(total_ticks):
    # solver ?
           # On affecte la machine à un worker
        # self.machines["M1"].set_operator(self.workers["W1"])
        # self.machines["M2"].set_operator(self.workers["W2"])
        # self.machines["M3"].set_operator(self.workers["W3"])
            time.sleep(speed_tik)
            # 1) Mise à jour Markov (machine <-> ZNP) pour chaque worker
            for w in self.workers.values():
                w.step_markov()

            # 2) Avancement du job shop : process sur chaque machine
            for machine in self.machines.values():
                finished_op = machine.process(tick)
                if finished_op:
                    job = self.find_job_by_name(finished_op.job_name)
                    if job:
                        job.advance()
                        if job.finished:
                            finished_jobs_count += 1
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
# MAIN
# ------------------------------------------------------------------

if __name__ == "__main__":
    from netlogopy2.netlogopy import run_netlogo
    nl_interface = run_netlogo("C:/Program Files/NetLogo 6.2.2")

    sim = JobShopSimulation(nl_interface)
    sim.run(EOS)

    nl_interface.close_model()
