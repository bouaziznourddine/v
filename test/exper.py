import numpy as np
import matplotlib.pyplot as plt

# 1) Domaine : x = 1 à 175500
x = np.linspace(1, 175500, 1000)

# 2) Choix du point d'inflexion x0 (~ milieu du domaine)
x0 = 87750

# 3) Choix de k pour que y ~ 0 vers x=1 et y ~ 1 vers x=175500
#    On cherche par exemple à avoir y(1) proche de 0.00001 et y(175500) proche de 0.99999
#    Cela nous amène à k ≈ 1.3e-4 (valeur indicative).
k = 4e-5

# Fonction logistique "standard" bornée entre 0 et 1
y = 1 / (1 + np.exp(-k * (x - x0)))

plt.figure(figsize=(8, 5))
plt.plot(x, y, 'r', linewidth=2)

plt.title("Courbe logistique sur x ∈ [1, 175500] et y ∈ [0, 1]")
plt.xlabel("x")
plt.ylabel("y (progression)")
plt.grid(True, linestyle=':', alpha=0.7)

plt.ylim(-0.05, 1.05)     # pour visualiser de 0 à 1
plt.xlim(1, 175500)

plt.show()
