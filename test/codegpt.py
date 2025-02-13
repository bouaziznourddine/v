import time, os, random
from math import floor
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------------------------
# PARAMÈTRES ET CONFIGURATION DE LA SIMULATION
# ------------------------------------------------------------------

# Classe permettant de créer un profil dynamique à partir d'un dictionnaire
class profile():
    def __init__(self, fields={}):
        # Mise à jour de l'espace de noms de l'objet avec les clés/valeurs fournies
        self.__dict__.update(fields)

# --- Données pour les profils d'ouvriers ---
if True:
    profile_0 = profile(fields={
        "punct": [[1, 0, 0, 0]] * 4,  # Probabilités de déplacement entre zones
        "vitesse": 1,
        "alf_exp": 0,
        "alf_ftig": 0,
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

# Paramètres temporels
pas_tick = 1        # Durée d'un tick
speed_tik = 0.1       # Délai entre ticks (0 = exécution rapide)
EOS = 480           # Durée totale de la simulation (480 ticks)

# --- Données du modèle pour le Job Shop ---
if True:
    # Ensemble des machines et jobs
    M = ["M1", "M2", "M3"]
    jobs_names = ["J1", "J2", "J3"]

    # Exemple de routage : chaque job suit une séquence d'opérations (machine, durée)
    routing = {
        "J1": [("M1", 3), ("M3", 2), ("M2", 4)],
        "J2": [("M2", 2), ("M1", 3), ("M3", 1)],
        "J3": [("M3", 2), ("M2", 4), ("M1", 3)]
    }

    H = 25  # Horizon temporel (non utilisé directement ici)

# ------------------------------------------------------------------
# FONCTIONS MATHÉMATIQUES
# ------------------------------------------------------------------

def fatigue(data):
    """
    Calcule la fatigue en fonction du temps et d'un coefficient.
    La fatigue décroît linéairement sur une période de 480 unités de temps avec un bruit aléatoire.
    """
    t, f = data[0], data[1]
    r = 0 if f == 0 else np.random.normal(0, 0.01)
    return 1 - ((t % 480) * f) + r

def experience(data):
    """
    Calcule l'expérience accumulée.
    L'expérience s'accumule par tranches de 480 unités de temps.
    """
    t, e = data[0], data[1]
    return floor(t / 480) * e

# ------------------------------------------------------------------
# FONCTIONS POUR LA VITESSE DES OUVRIERS
# ------------------------------------------------------------------
# Pour cet exemple, toutes les fonctions vit_WkrX utilisent la même logique.
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
    """
    Met à jour la zone de l'ouvrier selon le vecteur de probabilités défini dans son profil.
    Si l'ouvrier n'est pas dans l'une des zones, retourne 0.
    Sinon, choisit la prochaine zone en fonction du profil.
    """
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
# On utilise ici les fonctions et classes fournies par netlogopy2.netlogopy
from netlogopy2.netlogopy import netlogoshow, resize_world, set_background, NL_Street, PyTurtle

# Efface l'écran pour l'affichage (Windows)
os.system('cls')

# ------------------------------------------------------------------
# CLASSES DE BASE POUR LES ENTITÉS DU JOB SHOP
# ------------------------------------------------------------------

class Zone:
    """
    Représente une zone d'intervention dans le job shop.
    La PyTurtle associée est initialisée avec :
      - "worker_encour": ouvrier assigné (None par défaut)
      - "free": disponibilité (True par défaut)
    """
    def __init__(self, nl_interface, x, y, shape, size, color, name, labelcolor):
        self.obj = PyTurtle(nl_interface, x=x, y=y, shape=shape, size_shape=size, color=color,
                            name=name, labelcolor=labelcolor,
                            fields={"worker_encour": None, "free": True})
        self.name = name

class Stock:
    """
    Représente un point de stockage.
    """
    def __init__(self, nl_interface, x, y, shape, size, color, name):
        self.obj = PyTurtle(nl_interface, x=x, y=y, shape=shape, size_shape=size, color=color,
                            name=name, fields={})
        self.name = name

class Machine:
    """
    Représente une machine dans le job shop.
    Chaque machine possède :
      - Une file d'attente d'opérations (queue).
      - Une opération en cours de traitement.
      - Un opérateur (worker) optionnel pour influencer la vitesse de traitement.
    """
    def __init__(self, nl_interface, name, x, y, shape="machine", size=4, color=15):
        self.name = name
        self.queue = []                # File d'attente des opérations
        self.operation_in_progress = None
        self.operator = None           # Ouvrier assigné à cette machine
        self.obj = PyTurtle(nl_interface, x=x, y=y, shape=shape,
                            size_shape=size, color=color, name=name, labelcolor=color,
                            fields={"busy": False})
    
    def set_operator(self, worker):
        """Assigne un ouvrier à cette machine."""
        self.operator = worker

    def add_operation(self, operation):
        """Ajoute une opération à la file d'attente."""
        self.queue.append(operation)

    def process(self, tick):
        """
        Traite l'opération en cours.
        Si la machine est libre et qu'une opération est en attente, démarre l'opération.
        Si un opérateur est assigné, le temps effectif de traitement est ajusté par sa vitesse.
        Renvoie l'opération terminée, ou None.
        """
        tick_time = tick * pas_tick

        # Démarrer une nouvelle opération si la machine est libre
        if self.operation_in_progress is None and self.queue:
            self.operation_in_progress = self.queue.pop(0)
            self.operation_in_progress.start_time = tick_time
            self.obj.fields["busy"] = True

        # Calcul de la vitesse de traitement en fonction de l'opérateur
        if self.operation_in_progress:
            if self.operator:
                worker_speed = self.operator.def_vit(tick_time)
            else:
                worker_speed = 1

            # Vérification si l'opération est terminée
            if (tick_time - self.operation_in_progress.start_time) * worker_speed >= self.operation_in_progress.duration:
                finished_op = self.operation_in_progress
                self.operation_in_progress = None
                self.obj.fields["busy"] = False
                if self.operator:
                    self.operator.num_operations += 1
                return finished_op
        return None

class Operation:
    """
    Représente une opération d'un job sur une machine.
    """
    def __init__(self, job_name, machine_name, duration):
        self.job_name = job_name
        self.machine_name = machine_name
        self.duration = duration
        self.start_time = None

class Job:
    """
    Représente un job dans le job shop.
    Un job est défini par une séquence d'opérations (routage).
    Dispose également d'une représentation graphique (marqueur) qui se déplace.
    """
    def __init__(self, nl_interface, job_name, routing_sequence):
        self.job_name = job_name
        self.routing_sequence = routing_sequence  # Liste de tuples (machine_name, duration)
        self.current_op_index = 0
        self.finished = False
        # Pour représenter graphiquement le job, nous utilisons une forme "circle" (assurez-vous que cette forme est définie dans NetLogo)
        self.rep = PyTurtle(nl_interface, x=5, y=5, shape="circle", size_shape=2, color=15,
                             name=job_name, labelcolor=15, fields={})

    def get_next_operation(self):
        """Renvoie la prochaine opération ou None si le job est terminé."""
        if self.current_op_index < len(self.routing_sequence):
            machine_name, duration = self.routing_sequence[self.current_op_index]
            return Operation(self.job_name, machine_name, duration)
        return None

    def advance(self):
        """Passe à l'opération suivante et marque le job comme terminé si fini."""
        self.current_op_index += 1
        if self.current_op_index >= len(self.routing_sequence):
            self.finished = True

    def update_representation(self, new_target):
        """
        Met à jour la position du marqueur graphique du job vers la position de new_target.
        new_target est ici l'objet (par exemple, la PyTurtle) de la machine concernée.
        """
        self.rep.move_to(new_target)

# Nouvelle classe Worker pour le job shop (avec représentation graphique)
class Worker:
    """
    Représente un ouvrier dans le job shop.
    Chaque ouvrier dispose d'un profil qui détermine sa vitesse de traitement.
    """
    def __init__(self, nl_interface, name, profile):
        self.name = name
        self.profile = profile
        self.num_operations = 0   # Nombre d'opérations traitées
        self.nht = 0              # Nombre de ticks travaillés
        # Pour représenter graphiquement l'ouvrier, on utilise une forme déjà définie dans NetLogo, par exemple "person_0"
        self.rep = PyTurtle(nl_interface, x=0, y=0, shape="person_0", size_shape=3, color=55,
                            name=name, labelcolor=55, fields={})
        # Fonction de vitesse qui dépend du temps et du profil
        self.def_vit = lambda t: experience([t, profile.alf_exp]) + fatigue([t, profile.alf_ftig])

# ------------------------------------------------------------------
# CLASSE DE SIMULATION JOB SHOP
# ------------------------------------------------------------------

class JobShopSimulation:
    """
    Classe principale pour simuler un job shop.
    Configure les machines, les jobs et les ouvriers, et exécute la simulation.
    """
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

        # Création des ouvriers et leur affectation aux machines
        self.workers = {
            "W1": Worker(nl_interface, "worker_1", profile_0),
            "W2": Worker(nl_interface, "worker_2", profile_1),
            "W3": Worker(nl_interface, "worker_3", profile_2)
        }
        self.machines["M1"].set_operator(self.workers["W1"])
        self.machines["M2"].set_operator(self.workers["W2"])
        self.machines["M3"].set_operator(self.workers["W3"])

        # Création des jobs avec leur séquence d'opérations (routage)
        self.jobs = []
        for j in ["J1", "J2", "J3"]:
            self.jobs.append(Job(nl_interface, j, routing[j]))

        # Démarrage : pour chaque job, récupérer la première opération et l'ajouter à la machine correspondante
        for job in self.jobs:
            op = job.get_next_operation()
            if op:
                self.machines[op.machine_name].add_operation(op)
                # Met à jour la représentation du job vers la machine de départ
                job.update_representation(self.machines[op.machine_name].obj)

    def run(self, total_ticks):
        """
        Exécute la simulation pendant 'total_ticks' ticks.
        À chaque tick, chaque machine traite son opération et, lorsqu'une opération est terminée,
        le job passe à l'opération suivante et son marqueur graphique est mis à jour.
        """
        finished_jobs_count = 0

        for tick in range(total_ticks):
            time.sleep(speed_tik)  # Pause entre les ticks

            # Pour chaque machine, traiter l'opération en cours
            for machine in self.machines.values():
                finished_op = machine.process(tick)
                if finished_op:
                    # Récupérer le job correspondant à l'opération terminée
                    job = self.find_job_by_name(finished_op.job_name)
                    if job:
                        job.advance()
                        if job.finished:
                            finished_jobs_count += 1
                            # Par exemple, déplacer le marqueur en dehors de la zone de production
                            job.update_representation(self.nl_interface)
                        else:
                            next_op = job.get_next_operation()
                            self.machines[next_op.machine_name].add_operation(next_op)
                            # Met à jour le marqueur du job vers la machine cible
                            job.update_representation(self.machines[next_op.machine_name].obj)
            # Arrêt anticipé si tous les jobs sont terminés
            if finished_jobs_count == len(self.jobs):
                print(f"Tous les jobs ({finished_jobs_count}) sont terminés au tick {tick}.")
                break

        print(f"Simulation terminée. Jobs finis : {finished_jobs_count}/{len(self.jobs)}")

    def find_job_by_name(self, job_name):
        """Renvoie le job correspondant au nom donné."""
        for j in self.jobs:
            if j.job_name == job_name:
                return j
        return None

# ------------------------------------------------------------------
# POINT D'ENTRÉE DU SCRIPT
# ------------------------------------------------------------------

if __name__ == "__main__":
    # Lancement de NetLogo via run_netlogo (depuis netlogopy2.netlogopy)
    from netlogopy2.netlogopy import run_netlogo
    nl_interface = run_netlogo("C:/Program Files/NetLogo 6.2.2")

    # Instanciation et exécution de la simulation Job Shop
    sim = JobShopSimulation(nl_interface)
    total_ticks = EOS  # Par exemple, 480 ticks
    sim.run(total_ticks)

    # Fermeture du modèle NetLogo
    nl_interface.close_model()
