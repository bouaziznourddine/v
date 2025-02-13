"""
main_simulation.py
------------------
Script principal qui lance la simulation du job shop, en affichant 3 figures Matplotlib :
- progression cumulée par job,
- fatigue/exp/vitesse par ouvrier,
- état Markov (0..3) par ouvrier.
"""

import time
import matplotlib.pyplot as plt

# Import NetLogo
from netlogopy2.netlogopy import run_netlogo

# Import du code
from exmple.job_shop import Job, Operation, Worker, Machine, Zone
from exmple.job_shop import new_fatigue, new_experience, new_speed  # si besoin
from exmple.profiles import profile_0, profile_1, profile_2        # ou depuis profiles
# Ou + correct => from profiles import profile_0, profile_1, profile_2, ...
from exmple.job_shop import Job, Operation, Machine, Worker, Zone
from exmple.plot_utils import init_figure_jobs, init_figure_workers, init_figure_states

# + d'autres modules éventuellement

class JobShopSimulation:
    """
    Une simulation orchestrant :
      - Markov 4 états,
      - Avancement des jobs,
      - Mise à jour des figures.
    """
    def __init__(self, nl_interface):
        # ...
        pass

    def run(self, total_ticks):
        pass

if __name__ == "__main__":
    # 1) Lancement NetLogo
    nl_interface = run_netlogo("C:/Program Files/NetLogo 6.2.2")

    # 2) Instanciation de la simulation
    sim = JobShopSimulation(nl_interface)

    # 3) Exécution
    sim.run(50)   # ex. 50 ticks

    # 4) Fermeture NetLogo
    nl_interface.close_model()
