"""
profiles.py
-----------
Définit la classe `profile` et quelques profils d'ouvriers (Markov 4 états, param. fatigue/exp).
"""

import math
from math import floor

def new_fatigue(t, f_init, lamF, L):
    """
    Fatigue exponentielle :
    F(t) = f_init * exp( -lamF * (t % L) )
    """
    mod_part = t % L
    return f_init * math.exp(- lamF * mod_part)

def new_experience(t, e_init, lamE, L):
    """
    Expérience en paliers :
    E(t) = e_init + lamE * floor( t / L )
    """
    segments = floor(t / L)
    return e_init + lamE * segments

def new_speed(t, f_init, lamF, e_init, lamE, L):
    """
    S(t) = F(t) + E(t)
    """
    f_val = new_fatigue(t, f_init, lamF, L)
    e_val = new_experience(t, e_init, lamE, L)
    return f_val + e_val

class profile:
    """
    Contient les attributs :
      - f_init, lamF, e_init, lamE, L (pour fatigue/exp)
      - punct : matrice de transition Markov 4 états (liste de listes 4x4)
    """
    def __init__(self, fields={}):
        self.__dict__.update(fields)

# Exemples de profils
profile_0 = profile({
    "f_init": 1.0,
    "lamF": 0.0,
    "e_init": 1.0,
    "lamE": 0.0,
    "L": 30,
    "punct": [
        [1,   0,   0,   0],
        [0.5, 0.5, 0,   0],
        [0.4, 0.3, 0.2, 0.1],
        [1,   0,   0,   0]
    ]
})

profile_1 = profile({
    "f_init": 1.0,
    "lamF": 0.1,
    "e_init": 1.0,
    "lamE": 0.1,
    "L": 30,
    "punct": [
        [0.9, 0.1, 0,   0],
        [0.6, 0.2, 0.1, 0.1],
        [0,   0.3, 0.4, 0.3],
        [0,   0.3, 0.4, 0.3]
    ]
})

profile_2 = profile({
    "f_init": 1.0,
    "lamF": 0.05,
    "e_init": 1.0,
    "lamE": 0.2,
    "L": 30,
    "punct": [
        [0.8, 0.2, 0,   0],
        [0.3, 0.3, 0.2, 0.2],
        [0,   0.4, 0.3, 0.3],
        [0,   0.3, 0.4, 0.3]
    ]
})
