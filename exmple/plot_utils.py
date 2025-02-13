"""
plot_utils.py
-------------
Fonctions pour configurer et mettre à jour nos figures (jobs, workers, states).
"""

import matplotlib.pyplot as plt

def init_figure_jobs():
    fig_jobs, ax_jobs = plt.subplots()
    ax_jobs.set_title("Figure 1 : Progression cumulée par Job")
    return fig_jobs, ax_jobs

def init_figure_workers():
    fig_w, ax_w = plt.subplots(1,3, figsize=(12,4))
    fig_w.suptitle("Figure 2 : Fatigue / Exp / Vitesse", fontsize=14)
    return fig_w, ax_w

def init_figure_states():
    fig_s, ax_s = plt.subplots(1,3, figsize=(12,4))
    fig_s.suptitle("Figure 3 : Markov states", fontsize=14)
    return fig_s, ax_s

# etc.
