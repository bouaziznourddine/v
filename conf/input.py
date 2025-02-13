import time, os, random
from math import floor
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------------------------
# PARAMÈTRES ET CONFIGURATION DE LA SIMULATION
# ------------------------------------------------------------------

# Classe 'profile' permettant de définir dynamiquement des attributs
class profile():
    def __init__(self, fields={}):
        self.__dict__.update(fields)

# --- Données pour les profils d'ouvriers ---
if True:
    profile_0 = profile(fields={
        "punct": [[1, 0, 0, 0]] * 4,  # Vecteur de probabilité pour le déplacement (pour simplifier)
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

# Paramètres temporels de la simulation
pas_tick = 1          # Durée d'un tick
speed_tik = 0.1       # Délai entre les ticks (0.1 secondes pour visualisation)
EOS = 10              # Durée totale de la simulation en ticks (10 ticks => seulement J1 pourra finir)

# --- Données du modèle de production (Job Shop) ---
if True:
    # Liste des machines et jobs
    M = ["M1", "M2", "M3"]
    jobs_names = ["J1", "J2", "J3"]

    # Exemple de routage pour chaque job
    # Ici, J1 a des opérations très courtes pour pouvoir se terminer rapidement,
    # tandis que J2 et J3 ont des opérations plus longues qui ne se termineront pas dans le temps imparti.
    routing = {
        "J1": [("M1", 1), ("M3", 1), ("M2", 1)],  # Total 3 ticks
        "J2": [("M2", 5), ("M1", 5), ("M3", 5)],  # Total 15 ticks
        "J3": [("M3", 5), ("M2", 5), ("M1", 5)]   # Total 15 ticks
    }

    H = 25  # Horizon temporel (pour référence)
