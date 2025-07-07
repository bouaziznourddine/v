import numpy as np
import matplotlib.pyplot as plt

def logistic_function(t, e_min, e_max, k, t0):
    """
    Calcule la valeur d'une fonction logistique de la forme :
        e(t) = e_min + (e_max - e_min) / (1 + exp(-k*(t - t0))).
    
    Paramètres
    ----------
    t : array_like
        Les temps (ou valeurs de la variable indépendante) auxquels on veut calculer e(t).
    e_min : float
        Valeur minimale (asymptote basse).
    e_max : float
        Valeur maximale (asymptote haute).
    k : float
        Pente (taux de croissance).
    t0 : float
        Point de transition (milieu de la croissance).
    
    Retour
    ------
    e : np.ndarray ou float
        Valeurs de la fonction logistique pour chaque point t.
    """
    return e_min + (e_max - e_min) / (1.0 + np.exp(-k * (t - t0)))


# Exemple d'utilisation
if __name__ == "__main__":
    # Paramètres du modèle
    e_min = 2.0   # asymptote inférieure
    e_max = 10.0  # asymptote supérieure
    k = 0.5       # pente
    t0 = 5.0      # point de transition (temps où la fonction est à mi-chemin entre e_min et e_max)

    # Domaine de la variable t
    t_vals = np.linspace(0, 10, 200)

    # Calcul de la fonction pour chaque t
    e_vals = logistic_function(t_vals, e_min, e_max, k, t0)

    # Affichage du résultat
    plt.plot(t_vals, e_vals, label="e(t)")
    plt.xlabel("t")
    plt.ylabel("Valeur de e(t)")
    plt.title("Fonction logistique")
    plt.legend()
    plt.show()
