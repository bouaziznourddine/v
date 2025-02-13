import time, os, random

# Importation des paramètres et fonctions de configuration

# Définition d'une classe 'profile' permettant de stocker dynamiquement des attributs
class profile():
    def __init__(self, fields={}):
        # Mise à jour de l'espace de noms de l'objet avec les clés/valeurs du dictionnaire 'fields'
        self.__dict__.update(fields)

        
# --- Simulation de données initiales pour les profils et paramètres généraux ---
if 1 :
    # Création de trois profils différents avec des paramètres de base
    profile_0 = profile(fields={"punct": [[1,0,0,0], [1,0,0,0], [1,0,0,0], [1,0,0,0]],
                                "vitesse": 1, "alf_exp": 0, "alf_ftig": 0, "qualit": 1})
    profile_1 = profile(fields={"punct": [[0.9,0.1,0,0], [0.95,0.05,0,0], [1,0,0,0], [1,0,0,0]],
                                "vitesse": 1, "alf_exp": 0.1, "alf_ftig": 0.1, "qualit": 1})
    profile_2 = profile(fields={"punct": [[0.8,0.2,0,0], [0.6,0.2,0.1,0.1], [0,0.3,0.4,0.3], [0,0.3,0.4,0.3]],
                                "vitesse": 1, "alf_exp": 0.1, "alf_ftig": 0.1, "qualit": 1})

    # Paramètres de la simulation
    pas_tick = 1       # Durée d'un tick
    speed_tik = 0      # Délai entre les ticks (0 pour simulation sans pause)
    EOS = 480           # Fin de la simulation (durée totale en unités de temps)

# --- Définition du modèle de données de production ---
if 1 :
    # Définition des ensembles de base
    M = [1, 2, 3]             # Liste des machines (workstations)
    T_set = [1, 2, 3]         # Types de produits
    J = list(range(1, 10))    # Jobs (numérotés de 1 à 9)

    # Mix de production minimal pour chaque type
    I = {1: 1, 2: 1, 3: 1}

    # Temps de traitement (tau) pour chaque couple (type de produit, machine)
    tau = {
        (1, 1): 3, (1, 2): 3, (1, 3): 2,
        (2, 1): 4, (2, 2): 2, (2, 3): 2,
        (3, 1): 2, (3, 2): 1, (3, 3): 4,
    }

    # Affectation des ouvriers aux machines (W_{k,m})
    W = {
        (1, 1): 1, (1, 2): 0, (1, 3): 0,
        (2, 1): 0, (2, 2): 1, (2, 3): 0,
        (3, 1): 0, (3, 2): 0, (3, 3): 1,
    }

    # Paramètres liés aux ouvriers
    alpha = {1: 8, 2: 5, 3: 5}   # Productivité continue (temps de travail)
    gamma = {1: 1, 2: 2, 3: 1}     # Temps d'arrêt ou coefficient de downtime
    speed = {1: 1, 2: 1, 3: 1}      # Vitesse (uniforme ici)

    # Calcul préliminaire de la capacité U_m et du downtime D_m par machine
    U = {m: sum(alpha[k] * W[(k, m)] for k in alpha.keys()) for m in M}
    D = {m: sum(gamma[k] * W[(k, m)] for k in gamma.keys()) for m in M}
    speedm = {m: sum(speed[k] * W[(k, m)] for k in speed.keys()) for m in M}

    # Ajustement du temps de traitement en fonction de la vitesse de la machine
    adjusted_tau = {(t, m): tau[(t, m)] / speedm[m] for (t, m) in tau}

    H = 25   # Horizon temporel de la simulation (issu de l'image de référence)

# Importation des modules mathématiques et de tracé
from math import exp
import numpy as np
import matplotlib.pyplot as plt

# Couleurs utilisées pour les graphiques
colors = ['red', 'blue', 'green', 'cyan', 'magenta', 'yellow', 'black', 'purple', 'orange', 'brown']

# --- Fonctions de calcul de la vitesse des ouvriers (basées sur expérience et fatigue) ---
def vit_Wkr0(wrk=None, tem=0, numprd=0):
    # Récupère le profil de l'ouvrier et calcule la vitesse en fonction de l'expérience et de la fatigue
    wrprofile = wrk.profile
    v = experience([tem, wrprofile.alf_exp]) + fatigue([tem, wrprofile.alf_ftig])
    return v

def vit_Wkr1(wrk=None, tem=0, numprd=0):
    wrprofile = wrk.profile
    v = experience([tem, wrprofile.alf_exp]) + fatigue([tem, wrprofile.alf_ftig])
    return v

def vit_Wkr2(wrk=None, tem=0, numprd=0):
    wrprofile = wrk.profile
    v = experience([tem, wrprofile.alf_exp]) + fatigue([tem, wrprofile.alf_ftig])
    return v

def vit_Wkr3(wrk=None, tem=0, numprd=0):
    wrprofile = wrk.profile
    v = experience([tem, wrprofile.alf_exp]) + fatigue([tem, wrprofile.alf_ftig])
    return v

def vit_Wkr4(wrk=None, tem=0, numprd=0):
    wrprofile = wrk.profile
    v = experience([tem, wrprofile.alf_exp]) + fatigue([tem, wrprofile.alf_ftig])
    return v

def vit_Wkr5(wrk=None, tem=0, numprd=0):
    wrprofile = wrk.profile
    v = experience([tem, wrprofile.alf_exp]) + fatigue([tem, wrprofile.alf_ftig])
    return v

# --- Fonction de mise à jour de la zone de l'ouvrier ---
def update_wk(wrk, lzone):
    # Si la zone actuelle n'est pas dans la liste des zones, v = 0, sinon on récupère son index + 1
    if wrk.zon_now not in lzone:
        v = 0
    else:
        v = lzone.index(wrk.zon_now) + 1
    # Conversion de la matrice 'punct' en tableau numpy
    M = np.array(wrk.profile.punct)
    # Choix aléatoire de la prochaine zone selon la distribution de probabilités
    nextzon = np.random.choice(np.arange(0, 4), p=M[v])
    pass  # 'pass' inutile ici, il peut être supprimé
    return nextzon

# --- Fonctions de calcul de la fatigue et de l'expérience ---
def fatigue(data):
    t = data[0]  # Temps actuel
    f = data[1]  # Coefficient de fatigue
    # Si le coefficient de fatigue est nul, pas de bruit aléatoire
    if f == 0:
        r = 0
    else:
        # Bruit aléatoire (écart-type 0.01)
        r = np.random.normal(0, 0.01, 1)[0]
    # Calcul de la fatigue : décroissance linéaire avec un bruit aléatoire
    return 1 - (t % 480) * f + r
    # Alternative possible (commentée) : return np.exp(-f * (t % 480)) + r 

def experience(data):
    t = data[0]  # Temps actuel
    e = data[1]  # Coefficient d'expérience
    # L'expérience s'accumule par périodes de 480 unités de temps
    v = np.floor(t / 480) * e 
    return v

# --- Fonctions de tracé pour visualiser l'expérience et la fatigue ---
def plotex(e):
    x = np.arange(0, 100, 1)
    plt.plot(x, experience([x, e]), color='red')
    plt.xlabel('x')
    plt.ylabel('f(x)')
    plt.title('experience ')
    # plt.grid(True)
    plt.show()

def plotexlist(le):
    x = np.arange(0, 100, 1)
    i = -1
    # Parcours de chaque coefficient dans la liste
    for e in le:
        i += 1
        color = colors[i]
        plt.plot(x, experience([x, e]), color=color, label=("ex " + str(e)))
    plt.xlabel('x')
    plt.ylabel('ex(x)')
    plt.title('experience ')
    # plt.grid(True)
    plt.legend()
    plt.show()

def plotft(e):
    x = np.arange(0, 100, 1)
    plt.plot(x, fatigue([x, e]), color='red')
    plt.xlabel('x')
    plt.ylabel('f(x)')
    plt.title('fatigue ')
    # plt.grid(True)
    plt.show()

def plotftlist(le):
    x = np.arange(0, 100, 1)
    i = -1
    for e in le:
        i += 1
        color = colors[i]
        plt.plot(x, fatigue([x, e]), color=color, label=("ex " + str(e)))
    plt.xlabel('x')
    plt.ylabel('ex(x)')
    plt.title('fatigue ')
    # plt.grid(True)
    plt.legend()
    plt.show()

# --- Quelques appels de test pour le tracé (actuellement commentés) ---
l = []
for i in np.arange(0.1, 1, 0.1):
    l.append(i)
# plotexlist(l)

l = []
for i in np.arange(0.1, 1, 0.1):
    l.append(i)
# plotftlist(l)
    
# --- Importation des fonctions et classes de NetLogo pour l'interface graphique ---
from netlogopy2.netlogopy import netlogoshow, resize_world, set_background, NL_Street, PyTurtle

# Efface l'écran (pour Windows)
os.system('cls')


# ========= CLASSES DE BASE POUR LES ENTITÉS =========

# Classe représentant une zone d'intervention dans la simulation
class Zone:
    """
    Représente une zone (point d'intérêt) dans la simulation.
    
    Les attributs dans 'fields' de la pyturtle associée :
      - "worker_encour" : ouvrier assigné à cette zone (None par défaut)
      - "free"          : booléen indiquant si la zone est libre (True par défaut)
    """
    def __init__(self, nl_interface, x, y, shape, size, color, name, labelcolor):
        # Création d'un objet PyTurtle pour représenter la zone
        self.obj = PyTurtle(nl_interface, x=x, y=y, shape=shape, size_shape=size, color=color,
                            name=name, labelcolor=labelcolor,
                            fields={"worker_encour": None, "free": True})
        self.name = name

# Classe représentant un point de stockage
class Stock:
    """
    Représente un point de stockage (pour pièces intermédiaires ou produits finis).
    """
    def __init__(self, nl_interface, x, y, shape, size, color, name):
        # Création d'un objet PyTurtle pour représenter le stock
        self.obj = PyTurtle(nl_interface, x=x, y=y, shape=shape, size_shape=size, color=color,
                            name=name, fields={})
        self.name = name

# Classe représentant une station de travail
class Workstation:
    """
    Représente une station de travail de la chaîne de production.
    
    Les champs dans 'fields' de la pyturtle associée :
      - "pt"            : temps requis pour traiter une pièce à cette station.
      - "prd_encour"    : pièce en cours de traitement (None par défaut).
      - "stock"         : liste des pièces en attente.
      - "stock_tr"      : emplacement de stockage associé (objet Stock).
      - "nextws"        : station suivante (None si dernière station).
      - "worker_encour" : ouvrier assigné à la station (None par défaut).
      - "libre"         : booléen indiquant si la station est disponible.
    """
    def __init__(self, nl_interface, x, y, shape, size, color, name, labelcolor, pt, stock_tr, nextws=None):
        # Création d'un objet PyTurtle pour représenter la station
        self.obj = PyTurtle(nl_interface, x=x, y=y, shape=shape, size_shape=size, color=color,
                            name=name, labelcolor=labelcolor,
                            fields={"pt": pt, "prd_encour": None, "stock": [],
                                    "stock_tr": stock_tr.obj, "nextws": nextws, "worker_encour": None, "libre": True})
        self.name = name

    def set_nextws(self, nextws):
        # Définit la station suivante
        self.obj.fields["nextws"] = nextws

    def add_product(self, product):
        # Ajoute un produit à la file d'attente
        self.obj.fields["stock"].append(product)

    def process(self, current_tick, stockfinal):
        tick_time = current_tick * pas_tick  # Calcul du temps courant en fonction du tick

        # Si aucun produit n'est en cours et que le stock n'est pas vide, on démarre le traitement d'un produit
        if self.obj.fields["prd_encour"] is None and self.obj.fields["stock"]:
            product = random.choice(self.obj.fields["stock"])  # Choix aléatoire d'un produit en attente
            self.obj.fields["stock"].remove(product)            # Suppression du produit du stock
            product.move_to(self.obj)                             # Déplacement visuel vers la station
            product.fields["Sj"] = tick_time                      # Enregistrement du tick de début de traitement
            product.fields["pt"] = tick_time                      # Initialisation de la progression
            self.obj.fields["prd_encour"] = product              # Affectation du produit en cours à la station

        # Si un produit est en cours et qu'un ouvrier est assigné, on traite le produit
        if self.obj.fields["prd_encour"] and self.obj.fields["worker_encour"]:
            worker = self.obj.fields["worker_encour"]
            numprd = worker.numprd
            # Incrémentation de la progression en fonction de la vitesse de l'ouvrier
            inc = pas_tick * worker.def_vit(worker, tick_time, numprd)
            self.obj.fields["prd_encour"].fields["pt"] += inc
            worker.nht += 1  # Incrémentation du nombre de ticks travaillés par l'ouvrier

        # Vérification si le produit a terminé son traitement sur cette station
        if self.obj.fields["prd_encour"] and self.obj.fields["worker_encour"]:
            product = self.obj.fields["prd_encour"]
            if (product.fields["pt"] - product.fields["Sj"]) >= self.obj.fields["pt"]:
                worker = self.obj.fields["worker_encour"]
                worker.numprd += 1  # Incrémentation du nombre de produits traités
                if self.obj.fields["nextws"]:
                    # Si la station suivante existe, le produit y est déplacé
                    next_ws = self.obj.fields["nextws"]
                    product.move_to(next_ws.obj)
                    product.fd(3)
                    next_ws.obj.fields["stock"].append(product)
                    self.obj.fields["prd_encour"] = None
                else:
                    # Sinon, le produit est envoyé vers le stock final
                    product.move_to(stockfinal.obj)
                    product.fd(3)
                    self.obj.fields["prd_encour"] = None
                    return True  # Indique qu'un produit fini a été produit
        return False  # Produit toujours en cours de traitement


# Classe représentant un ouvrier de la chaîne de production
class Worker:
    """
    Représente un ouvrier.
    
    Les champs dans 'fields' de la pyturtle associée :
      - "assignment" : station de travail assignée.
      - "nht"        : nombre de ticks travaillés.
      - "fatigue"    : coefficient de fatigue (initialement 1).
      - "experience" : coefficient d'expérience.
      - "profile"    : profil définissant la vitesse.
      - "zon_now"    : zone actuelle (initialisée à la station d'affectation).
      - "numprd"     : nombre de pièces traitées.
      - "def_vit"    : fonction déterminant la vitesse.
    """
    def __init__(self, nl_interface, x, y, shape, size, color, name, labelcolor, assignment, profile):
        # Création d'un objet PyTurtle pour représenter l'ouvrier
        self.obj = PyTurtle(nl_interface, x=x, y=y, shape=shape, size_shape=size, color=color,
                            name=name, labelcolor=labelcolor,
                            fields={"assignment": assignment.obj, "nht": 0, "fatigue": 1,
                                    "experience": 1, "profile": profile, "zon_now": assignment.obj,
                                    "numprd": 0, "def_vit": None})
        self.assignment = assignment  # Station affectée
        self.profile = profile        # Profil de l'ouvrier
        self.nht = 0                  # Nombre de ticks travaillés
        self.numprd = 0               # Nombre de produits traités

        # Attribution de la fonction de vitesse selon le nom de l'ouvrier
        if name == "person_0":
            self.obj.fields["def_vit"] = lambda wrk, tem, numprd: vit_Wkr0(wrk, tem, numprd)
        elif name == "person_1":
            self.obj.fields["def_vit"] = lambda wrk, tem, numprd: vit_Wkr1(wrk, tem, numprd)
        elif name == "person_2":
            self.obj.fields["def_vit"] = lambda wrk, tem, numprd: vit_Wkr2(wrk, tem, numprd)
        elif name == "person_3":
            self.obj.fields["def_vit"] = lambda wrk, tem, numprd: vit_Wkr3(wrk, tem, numprd)
        elif name == "person_4":
            self.obj.fields["def_vit"] = lambda wrk, tem, numprd: vit_Wkr4(wrk, tem, numprd)
        elif name == "person_5":
            self.obj.fields["def_vit"] = lambda wrk, tem, numprd: vit_Wkr5(wrk, tem, numprd)

    # Méthode de déplacement de l'ouvrier vers une cible donnée
    def move_to(self, target):
        self.obj.move_to(target)
        self.obj.fields["zon_now"] = target  # Mise à jour de la zone actuelle

    @property
    def def_vit(self):
        # Renvoie la fonction de vitesse assignée
        return self.obj.fields["def_vit"]

# Classe représentant une pièce ou un produit dans la chaîne de production
class Product:
    """
    Représente une pièce/produit dans la chaîne de production.
    
    Les champs dans 'fields' de la pyturtle associée :
      - "Sj"      : tick de début de traitement.
      - "pt"      : progression cumulée.
      - "ws_now"  : station actuelle.
      - "ws_last" : station précédente.
      - "ws_next" : station suivante.
      - "active"  : indicateur d'activité.
    """
    def __init__(self, nl_interface, x, y, shape, size, color, labelcolor):
        # Création d'un objet PyTurtle pour représenter le produit
        self.obj = PyTurtle(nl_interface, x=x, y=y, shape=shape, size_shape=size, color=color,
                            name="", labelcolor=labelcolor,
                            fields={"Sj": 0, "pt": 0, "ws_now": None, "ws_last": None,
                                    "ws_next": None, "active": True})

    @property
    def fields(self):
        # Accès simplifié aux champs de l'objet PyTurtle
        return self.obj.fields

    def move_to(self, target):
        # Déplace le produit vers la cible
        self.obj.move_to(target)

    def fd(self, distance):
        # Fait avancer le produit d'une certaine distance (pour l'animation)
        self.obj.fd(distance)


# ========= CLASSE DE SIMULATION =========

# Classe principale qui configure et exécute la simulation
class Simulation:
    """
    Classe principale pour configurer et exécuter la simulation.
    Elle initialise l'environnement NetLogo, crée les stocks, stations, zones, ouvriers et produits,
    puis exécute la simulation pour un nombre de ticks donné.
    """
    def __init__(self):
        # Lancement de NetLogo via l'interface 'run_netlogo'
        from netlogopy2.netlogopy import run_netlogo  # Possibilité d'utiliser une nouvelle interface
        self.n = run_netlogo("C:/Program Files/NetLogo 6.2.2")
        # Redimensionnement du monde et définition de l'image de fond
        resize_world(self.n, 0, 70, 0, 55)
        set_background(self.n, "D:/cphs2024/netlogopy.png")

        # --- Création des points de stockage ---
        self.stock0 = Stock(self.n, 5, 10, "house", 4, 15, "stock0")
        self.stock1 = Stock(self.n, 15, 5, "house", 4, 55, "stock1")
        self.stock2 = Stock(self.n, 25, 5, "house", 4, 55, "stock2")
        self.stock3 = Stock(self.n, 35, 5, "house", 4, 55, "stock3")
        self.stock4 = Stock(self.n, 45, 5, "house", 4, 55, "stock4")
        self.stock5 = Stock(self.n, 55, 5, "house", 4, 55, "stock5")
        self.stockfinal = Stock(self.n, 60, 10, "house", 4, 15, "stockfinal")

        # --- Création des stations de travail ---
        self.Ws5 = Workstation(self.n, 55, 15, "machineinsp", 4, 55, "Ws5", 55, pt=1, stock_tr=self.stock5)
        self.Ws4 = Workstation(self.n, 45, 20, "machineinsp", 4, 55, "Ws4", 55, pt=1, stock_tr=self.stock4, nextws=self.Ws5)
        self.Ws3 = Workstation(self.n, 35, 15, "machine4", 4, 55, "Ws3", 55, pt=4, stock_tr=self.stock3, nextws=self.Ws4)
        self.Ws2 = Workstation(self.n, 25, 20, "machine3", 4, 55, "Ws2", 55, pt=2, stock_tr=self.stock2, nextws=self.Ws3)
        self.Ws1 = Workstation(self.n, 15, 15, "machine2", 4, 55, "Ws1", 55, pt=4, stock_tr=self.stock1, nextws=self.Ws2)
        self.Ws0 = Workstation(self.n, 5, 20, "machine", 4, 15, "Ws0", 15, pt=3, stock_tr=self.stock0, nextws=self.Ws1)
        self.workstations = [self.Ws0, self.Ws1, self.Ws2, self.Ws3, self.Ws4, self.Ws5]

        # --- Création des liaisons visuelles entre les stations ---
        NL_Street(self.n, from_turtle=self.Ws0.obj, to_turtle=self.Ws1.obj, label=" ", labelcolor=35, color=35, shape="aa", thickness=0.5)
        NL_Street(self.n, from_turtle=self.Ws1.obj, to_turtle=self.Ws2.obj, label=" ", labelcolor=35, color=35, shape="aa", thickness=0.5)
        NL_Street(self.n, from_turtle=self.Ws2.obj, to_turtle=self.Ws3.obj, label=" ", labelcolor=35, color=35, shape="aa", thickness=0.5)
        NL_Street(self.n, from_turtle=self.Ws3.obj, to_turtle=self.Ws4.obj, label=" ", labelcolor=35, color=35, shape="aa", thickness=0.5)
        NL_Street(self.n, from_turtle=self.Ws4.obj, to_turtle=self.Ws5.obj, label=" ", labelcolor=35, color=35, shape="aa", thickness=0.5)

        # --- Création des zones d'intervention ---
        self.zones = [
            Zone(self.n, 15, 35, "calling", 4, 15, "Zn1", 15),
            Zone(self.n, 25, 35, "food", 4, 15, "Zn2", 15),
            Zone(self.n, 35, 35, "house", 4, 15, "Zn3", 15)
        ]

        # --- Création des ouvriers et affectation aux stations ---
        self.workers = [
            Worker(self.n, 5, 5, "person_0", 4, 55, "person_0", 55, self.Ws0, profile_0),
            Worker(self.n, 5, 5, "person_1", 4, 55, "person_1", 55, self.Ws1, profile_1),
            Worker(self.n, 5, 5, "person_2", 4, 55, "person_2", 55, self.Ws2, profile_2),
            Worker(self.n, 5, 5, "person_3", 4, 55, "person_3", 55, self.Ws3, profile_0),
            Worker(self.n, 5, 5, "person_4", 4, 55, "person_4", 55, self.Ws4, profile_1),
            Worker(self.n, 5, 5, "person_5", 4, 55, "person_5", 55, self.Ws5, profile_2)
        ]

        # --- Création initiale d'un produit ---
        self.products = []
        init_product = Product(self.n, 5, 8, "p_robot00", 4, 55, 55)
        self.products.append(init_product)
        self.Ws0.add_product(init_product)

    # Méthode principale qui exécute la simulation sur un nombre défini de ticks
    def run(self, simulation_ticks):
        finished_products = 0  # Compteur de produits finis

        # Boucle principale de la simulation
        for tick in range(1, simulation_ticks):
            time.sleep(speed_tik)  # Pause pour simuler le temps réel

            # Traitement de chaque station de travail
            for ws in self.workstations:
                if ws.process(tick, self.stockfinal):
                    finished_products += 1  # Incrémente si un produit a terminé son traitement

            # Si la première station (Ws0) est libre, création d'un nouveau produit
            if self.Ws0.obj.fields["prd_encour"] is None:
                new_product = Product(self.n, 5, 8, "p_robot00", 4, 55, 55)
                self.products.append(new_product)
                self.Ws0.add_product(new_product)

            # Mise à jour du déplacement des ouvriers entre zones via la fonction update_wk
            for worker in self.workers:
                next_zone_index = update_wk(worker.obj, [zone.obj for zone in self.zones])
                if next_zone_index == 0:
                    # Si next_zone_index est 0, l'ouvrier retourne à sa station d'affectation s'il n'y est pas déjà
                    if worker.obj.fields["zon_now"] != worker.obj.fields["assignment"]:
                        worker.move_to(worker.obj.fields["assignment"])
                else:
                    # Sinon, l'ouvrier se déplace vers la zone correspondante (index ajusté)
                    next_zone_index -= 1
                    worker.move_to(self.zones[next_zone_index].obj)

        # Affichage du nombre de produits finis dans l'interface NetLogo et dans la console
        netlogoshow(self.n, "NPF :" + str(finished_products))
        print("Finished Products:", finished_products)
        input("Terminé : O ou N?")
        self.n.close_model()

# ========= Point d'entrée du script =========

if __name__ == "__main__":
    total_ticks = int(EOS / pas_tick)  # Calcul du nombre total de ticks
    sim = Simulation()                 # Instanciation de la simulation
    sim.run(total_ticks)               # Exécution de la simulation
