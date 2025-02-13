"""
job_shop.py
-----------
Définit les classes principales du job shop :
  - Operation, Job
  - Worker (Markov 4 états)
  - Machine
  - Zone
"""

import numpy as np
from netlogopy2.netlogopy import PyTurtle
from math import floor
from exmple.profiles import new_fatigue, new_experience, new_speed

class Operation:
    """Une opération (job_name, machine_name, duration, start_time)."""
    def __init__(self, job_name, machine_name, duration):
        self.job_name = job_name
        self.machine_name = machine_name
        self.duration = duration
        self.start_time = None

class Job:
    """Un job : liste (machine, durée)."""
    def __init__(self, nl_interface, job_name, routing_sequence):
        self.job_name = job_name
        self.routing_sequence = routing_sequence
        self.current_op_index = 0
        self.finished = False
        # Representation dans NetLogo
        self.rep = PyTurtle(nl_interface, x=5, y=5, shape="p_robot00", size_shape=5,
                            color=15, name=job_name, labelcolor=15, fields={})
        self.total_duration = sum(d for (_, d) in routing_sequence)

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
        """Déplace la représentation du job vers la machine ou zone finale."""
        self.rep.move_to(new_target)

class Worker:
    """
    Ouvrier markov 4 états : 0=machine, 1=ZNP1, 2=ZNP2, 3=ZNP3.
    On stocke un 'profile' => f_init, lamF, e_init, lamE, L, punct(4x4)
    """
    def __init__(self, nl_interface, name, profile,
                 znp1_obj, znp2_obj, znp3_obj, machine_obj):
        self.name = name
        self.profile = profile
        self.num_operations = 0
        self.nht = 0
        self.current_state = 0  # Sur la machine
        self.rep = PyTurtle(nl_interface, x=0, y=0, shape="person_0", size_shape=5,
                            color=55, name=name, labelcolor=55, fields={})
        self.rep.move_to(machine_obj)
        self.rep.fd(5)

        # association état -> PyTurtle
        self.zone_by_state = {
            0: machine_obj,
            1: znp1_obj,
            2: znp2_obj,
            3: znp3_obj
        }

    def def_vit(self, t):
        """S(t) = F(t) + E(t)."""
        p = self.profile
        return new_speed(t, p.f_init, p.lamF, p.e_init, p.lamE, p.L)

    def step_markov(self):
        """Transition Markov -> nouvelle zone si changement."""
        matrix = self.profile.punct
        row = matrix[self.current_state]
        new_st = np.random.choice([0,1,2,3], p=row)
        if new_st != self.current_state:
            self.current_state = new_st
            # Déplacement
            self.rep.move_to(self.zone_by_state[new_st])

class Zone:
    """Zone NP ou zone finale."""
    def __init__(self, nl_interface, x, y, shape, size, color, name, labelcolor):
        self.obj = PyTurtle(nl_interface, x=x, y=y, shape=shape, size_shape=size,
                            color=color, name=name, labelcolor=labelcolor,
                            fields={"worker_encour": None, "free": True})
        self.name = name

class Machine:
    """
    Machine, liste d'attente, operator => worker.
    ne traite que si worker.current_state=0
    """
    def __init__(self, nl_interface, name, x, y, shape="machine", size=4, color=15):
        self.name = name
        self.queue = []
        self.operation_in_progress = None
        self.operator = None
        self.obj = PyTurtle(nl_interface, x=x, y=y, shape=shape, size_shape=size,
                            color=color, name=name, labelcolor=color,
                            fields={"busy": False})
        self._update_label_queue()

    def _update_label_queue(self):
        q_size = len(self.queue)
        if self.operation_in_progress:
            label_str = f"Q={q_size+1}"
        else:
            label_str = f"Q={q_size}"
        self.obj.set_label(label_str)

    def set_operator(self, worker):
        self.operator = worker

    def add_operation(self, operation):
        self.queue.append(operation)
        self._update_label_queue()

    def process(self, tick):
        """Renvoie finished_op si terminé, sinon None."""
        if self.operator is None:
            return None
        if self.operator.current_state != 0:
            return None

        tick_time = tick
        if self.operation_in_progress is None and self.queue:
            self.operation_in_progress = self.queue.pop(0)
            self.operation_in_progress.start_time = tick_time
            self.obj.fields["busy"] = True
            self._update_label_queue()

        if self.operation_in_progress:
            w_speed = self.operator.def_vit(tick_time)
            elapsed = (tick_time - self.operation_in_progress.start_time)* w_speed
            if elapsed >= self.operation_in_progress.duration:
                finished_op = self.operation_in_progress
                self.operation_in_progress = None
                self.obj.fields["busy"] = False
                self.operator.num_operations += 1
                self._update_label_queue()
                return finished_op
        return None
