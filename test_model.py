import random
import math
import gurobipy as gp
from gurobipy import GRB
import itertools
import pandas as pd
import plotly.express as px
from input import *
# from input10 import *

# -----------------------------------------------------------------
# 1) Génération de jobs 
# -----------------------------------------------------------------
jobs={
'J1': [{'Ws': 'M1', 'Pt': 1}, {'Ws': 'M2', 'Pt': 8}, {'Ws': 'M3', 'Pt': 4}], 
'J2': [{'Ws': 'M1', 'Pt': 7}, {'Ws': 'M3', 'Pt': 7}, {'Ws': 'M2', 'Pt': 6}], 
'J3': [{'Ws': 'M2', 'Pt': 7}, {'Ws': 'M1', 'Pt': 1}, {'Ws': 'M3', 'Pt': 4}], 
'J4': [{'Ws': 'M2', 'Pt': 3}, {'Ws': 'M3', 'Pt': 8}, {'Ws': 'M1', 'Pt': 2}], 
'J5': [{'Ws': 'M2', 'Pt': 2}, {'Ws': 'M3', 'Pt': 7}, {'Ws': 'M1', 'Pt': 2}], 
'J6': [{'Ws': 'M3', 'Pt': 4}, {'Ws': 'M1', 'Pt': 4}, {'Ws': 'M2', 'Pt': 1}], 
'J7': [{'Ws': 'M1', 'Pt': 1}, {'Ws': 'M3', 'Pt': 2}, {'Ws': 'M2', 'Pt': 1}], 
'J8': [{'Ws': 'M2', 'Pt': 2}, {'Ws': 'M3', 'Pt': 3}, {'Ws': 'M1', 'Pt': 2}], 
'J9': [{'Ws': 'M1', 'Pt': 5}, {'Ws': 'M3', 'Pt': 4}, {'Ws': 'M2', 'Pt': 2}], 
'J10': [{'Ws': 'M3', 'Pt': 2}, {'Ws': 'M2', 'Pt': 5}, {'Ws': 'M1', 'Pt': 2}], 
'J11': [{'Ws': 'M1', 'Pt': 7}, {'Ws': 'M3', 'Pt': 8}, {'Ws': 'M2', 'Pt': 8}], 
'J12': [{'Ws': 'M2', 'Pt': 6}, {'Ws': 'M3', 'Pt': 7}, {'Ws': 'M1', 'Pt': 7}], 
'J13': [{'Ws': 'M3', 'Pt': 7}, {'Ws': 'M1', 'Pt': 4}, {'Ws': 'M2', 'Pt': 5}], 
'J14': [{'Ws': 'M2', 'Pt': 8}, {'Ws': 'M3', 'Pt': 7}, {'Ws': 'M1', 'Pt': 1}], 
'J15': [{'Ws': 'M1', 'Pt': 5}, {'Ws': 'M2', 'Pt': 6}, {'Ws': 'M3', 'Pt': 7}], 
'J16': [{'Ws': 'M2', 'Pt': 2}, {'Ws': 'M1', 'Pt': 5}, {'Ws': 'M3', 'Pt': 1}], 
'J17': [{'Ws': 'M3', 'Pt': 5}, {'Ws': 'M1', 'Pt': 6}, {'Ws': 'M2', 'Pt': 3}], 
'J18': [{'Ws': 'M1', 'Pt': 8}, {'Ws': 'M2', 'Pt': 5}, {'Ws': 'M3', 'Pt': 4}], 
'J19': [{'Ws': 'M2', 'Pt': 7}, {'Ws': 'M1', 'Pt': 3}, {'Ws': 'M3', 'Pt': 2}], 
'J20': [{'Ws': 'M2', 'Pt': 2}, {'Ws': 'M3', 'Pt': 2}, {'Ws': 'M1', 'Pt': 4}], 
'J21': [{'Ws': 'M3', 'Pt': 5}, {'Ws': 'M2', 'Pt': 2}, {'Ws': 'M1', 'Pt': 4}], 
'J22': [{'Ws': 'M3', 'Pt': 5}, {'Ws': 'M1', 'Pt': 5}, {'Ws': 'M2', 'Pt': 8}], 
'J23': [{'Ws': 'M2', 'Pt': 1}, {'Ws': 'M3', 'Pt': 2}, {'Ws': 'M1', 'Pt': 3}], 
'J24': [{'Ws': 'M1', 'Pt': 8}, {'Ws': 'M2', 'Pt': 8}, {'Ws': 'M3', 'Pt': 1}], 
'J25': [{'Ws': 'M1', 'Pt': 2}, {'Ws': 'M3', 'Pt': 2}, {'Ws': 'M2', 'Pt': 6}], 
'J26': [{'Ws': 'M1', 'Pt': 7}, {'Ws': 'M3', 'Pt': 2}, {'Ws': 'M2', 'Pt': 4}], 
'J27': [{'Ws': 'M3', 'Pt': 5}, {'Ws': 'M2', 'Pt': 6}, {'Ws': 'M1', 'Pt': 3}], 
'J28': [{'Ws': 'M3', 'Pt': 3}, {'Ws': 'M2', 'Pt': 1}, {'Ws': 'M1', 'Pt': 7}], 
'J29': [{'Ws': 'M1', 'Pt': 6}, {'Ws': 'M2', 'Pt': 7}, {'Ws': 'M3', 'Pt': 7}], 
'J30': [{'Ws': 'M1', 'Pt': 4}, {'Ws': 'M3', 'Pt': 6}, {'Ws': 'M2', 'Pt': 8}], 
'J31': [{'Ws': 'M1', 'Pt': 1}, {'Ws': 'M3', 'Pt': 1}, {'Ws': 'M2', 'Pt': 4}], 
'J32': [{'Ws': 'M2', 'Pt': 5}, {'Ws': 'M1', 'Pt': 6}, {'Ws': 'M3', 'Pt': 7}], 
'J33': [{'Ws': 'M3', 'Pt': 1}, {'Ws': 'M1', 'Pt': 8}, {'Ws': 'M2', 'Pt': 2}], 
'J34': [{'Ws': 'M1', 'Pt': 1}, {'Ws': 'M2', 'Pt': 1}, {'Ws': 'M3', 'Pt': 5}], 
'J35': [{'Ws': 'M2', 'Pt': 3}, {'Ws': 'M1', 'Pt': 2}, {'Ws': 'M3', 'Pt': 4}], 
'J36': [{'Ws': 'M3', 'Pt': 4}, {'Ws': 'M2', 'Pt': 6}, {'Ws': 'M1', 'Pt': 8}], 
'J37': [{'Ws': 'M3', 'Pt': 2}, {'Ws': 'M2', 'Pt': 6}, {'Ws': 'M1', 'Pt': 7}], 
'J38': [{'Ws': 'M3', 'Pt': 6}, {'Ws': 'M2', 'Pt': 3}, {'Ws': 'M1', 'Pt': 5}], 
'J39': [{'Ws': 'M1', 'Pt': 2}, {'Ws': 'M3', 'Pt': 7}, {'Ws': 'M2', 'Pt': 3}], 
'J40': [{'Ws': 'M3', 'Pt': 8}, {'Ws': 'M2', 'Pt': 7}, {'Ws': 'M1', 'Pt': 1}], 
'J41': [{'Ws': 'M2', 'Pt': 6}, {'Ws': 'M3', 'Pt': 7}, {'Ws': 'M1', 'Pt': 4}], 
'J42': [{'Ws': 'M3', 'Pt': 3}, {'Ws': 'M2', 'Pt': 8}, {'Ws': 'M1', 'Pt': 3}], 
'J43': [{'Ws': 'M2', 'Pt': 5}, {'Ws': 'M3', 'Pt': 6}, {'Ws': 'M1', 'Pt': 5}], 
'J44': [{'Ws': 'M1', 'Pt': 8}, {'Ws': 'M3', 'Pt': 4}, {'Ws': 'M2', 'Pt': 5}], 
'J45': [{'Ws': 'M3', 'Pt': 4}, {'Ws': 'M2', 'Pt': 3}, {'Ws': 'M1', 'Pt': 7}], 
'J46': [{'Ws': 'M2', 'Pt': 7}, {'Ws': 'M3', 'Pt': 3}, {'Ws': 'M1', 'Pt': 6}], 
'J47': [{'Ws': 'M2', 'Pt': 2}, {'Ws': 'M1', 'Pt': 1}, {'Ws': 'M3', 'Pt': 8}], 
'J48': [{'Ws': 'M1', 'Pt': 5}, {'Ws': 'M2', 'Pt': 7}, {'Ws': 'M3', 'Pt': 6}], 
'J49': [{'Ws': 'M3', 'Pt': 6}, {'Ws': 'M1', 'Pt': 3}, {'Ws': 'M2', 'Pt': 6}], 
'J50': [{'Ws': 'M1', 'Pt': 3}, {'Ws': 'M2', 'Pt': 1}, {'Ws': 'M3', 'Pt': 6}], 
'J51': [{'Ws': 'M3', 'Pt': 1}, {'Ws': 'M2', 'Pt': 2}, {'Ws': 'M1', 'Pt': 1}], 
'J52': [{'Ws': 'M1', 'Pt': 6}, {'Ws': 'M3', 'Pt': 7}, {'Ws': 'M2', 'Pt': 8}], 
'J53': [{'Ws': 'M1', 'Pt': 7}, {'Ws': 'M3', 'Pt': 7}, {'Ws': 'M2', 'Pt': 4}], 
'J54': [{'Ws': 'M3', 'Pt': 3}, {'Ws': 'M2', 'Pt': 4}, {'Ws': 'M1', 'Pt': 2}], 
'J55': [{'Ws': 'M3', 'Pt': 6}, {'Ws': 'M1', 'Pt': 8}, {'Ws': 'M2', 'Pt': 5}], 
'J56': [{'Ws': 'M1', 'Pt': 4}, {'Ws': 'M2', 'Pt': 6}, {'Ws': 'M3', 'Pt': 3}], 
'J57': [{'Ws': 'M3', 'Pt': 1}, {'Ws': 'M2', 'Pt': 2}, {'Ws': 'M1', 'Pt': 2}], 
'J58': [{'Ws': 'M1', 'Pt': 2}, {'Ws': 'M3', 'Pt': 8}, {'Ws': 'M2', 'Pt': 8}], 
'J59': [{'Ws': 'M2', 'Pt': 2}, {'Ws': 'M3', 'Pt': 4}, {'Ws': 'M1', 'Pt': 3}], 
'J60': [{'Ws': 'M2', 'Pt': 6}, {'Ws': 'M1', 'Pt': 5}, {'Ws': 'M3', 'Pt': 8}], 
'J61': [{'Ws': 'M3', 'Pt': 5}, {'Ws': 'M1', 'Pt': 7}, {'Ws': 'M2', 'Pt': 5}], 
'J62': [{'Ws': 'M2', 'Pt': 4}, {'Ws': 'M1', 'Pt': 8}, {'Ws': 'M3', 'Pt': 4}], 
'J63': [{'Ws': 'M1', 'Pt': 2}, {'Ws': 'M3', 'Pt': 3}, {'Ws': 'M2', 'Pt': 8}], 
'J64': [{'Ws': 'M3', 'Pt': 3}, {'Ws': 'M2', 'Pt': 5}, {'Ws': 'M1', 'Pt': 4}], 
'J65': [{'Ws': 'M3', 'Pt': 8}, {'Ws': 'M1', 'Pt': 6}, {'Ws': 'M2', 'Pt': 3}], 
'J66': [{'Ws': 'M2', 'Pt': 6}, {'Ws': 'M1', 'Pt': 8}, {'Ws': 'M3', 'Pt': 6}], 
'J67': [{'Ws': 'M3', 'Pt': 5}, {'Ws': 'M2', 'Pt': 8}, {'Ws': 'M1', 'Pt': 2}], 
'J68': [{'Ws': 'M1', 'Pt': 2}, {'Ws': 'M2', 'Pt': 4}, {'Ws': 'M3', 'Pt': 5}], 
'J69': [{'Ws': 'M2', 'Pt': 4}, {'Ws': 'M1', 'Pt': 7}, {'Ws': 'M3', 'Pt': 5}], 
'J70': [{'Ws': 'M1', 'Pt': 2}, {'Ws': 'M3', 'Pt': 4}, {'Ws': 'M2', 'Pt': 6}], 
'J71': [{'Ws': 'M3', 'Pt': 2}, {'Ws': 'M2', 'Pt': 2}, {'Ws': 'M1', 'Pt': 2}], 
'J72': [{'Ws': 'M1', 'Pt': 6}, {'Ws': 'M3', 'Pt': 8}, {'Ws': 'M2', 'Pt': 5}], 
'J73': [{'Ws': 'M3', 'Pt': 2}, {'Ws': 'M1', 'Pt': 5}, {'Ws': 'M2', 'Pt': 5}], 
'J74': [{'Ws': 'M2', 'Pt': 7}, {'Ws': 'M3', 'Pt': 4}, {'Ws': 'M1', 'Pt': 1}], 
'J75': [{'Ws': 'M2', 'Pt': 2}, {'Ws': 'M3', 'Pt': 4}, {'Ws': 'M1', 'Pt': 1}], 
'J76': [{'Ws': 'M2', 'Pt': 7}, {'Ws': 'M1', 'Pt': 2}, {'Ws': 'M3', 'Pt': 3}], 
'J77': [{'Ws': 'M2', 'Pt': 1}, {'Ws': 'M1', 'Pt': 1}, {'Ws': 'M3', 'Pt': 7}], 
'J78': [{'Ws': 'M3', 'Pt': 7}, {'Ws': 'M1', 'Pt': 3}, {'Ws': 'M2', 'Pt': 4}], 
'J79': [{'Ws': 'M1', 'Pt': 7}, {'Ws': 'M3', 'Pt': 6}, {'Ws': 'M2', 'Pt': 1}], 
'J80': [{'Ws': 'M1', 'Pt': 6}, {'Ws': 'M3', 'Pt': 4}, {'Ws': 'M2', 'Pt': 7}], 
'J81': [{'Ws': 'M1', 'Pt': 3}, {'Ws': 'M3', 'Pt': 1}, {'Ws': 'M2', 'Pt': 3}], 
'J82': [{'Ws': 'M2', 'Pt': 1}, {'Ws': 'M1', 'Pt': 8}, {'Ws': 'M3', 'Pt': 8}], 
'J83': [{'Ws': 'M2', 'Pt': 7}, {'Ws': 'M1', 'Pt': 1}, {'Ws': 'M3', 'Pt': 6}], 
'J84': [{'Ws': 'M1', 'Pt': 4}, {'Ws': 'M2', 'Pt': 8}, {'Ws': 'M3', 'Pt': 3}], 
'J85': [{'Ws': 'M2', 'Pt': 6}, {'Ws': 'M1', 'Pt': 5}, {'Ws': 'M3', 'Pt': 8}], 
'J86': [{'Ws': 'M2', 'Pt': 3}, {'Ws': 'M1', 'Pt': 2}, {'Ws': 'M3', 'Pt': 8}], 
'J87': [{'Ws': 'M1', 'Pt': 3}, {'Ws': 'M2', 'Pt': 2}, {'Ws': 'M3', 'Pt': 2}], 
'J88': [{'Ws': 'M2', 'Pt': 2}, {'Ws': 'M1', 'Pt': 6}, {'Ws': 'M3', 'Pt': 7}], 
'J89': [{'Ws': 'M1', 'Pt': 2}, {'Ws': 'M3', 'Pt': 4}, {'Ws': 'M2', 'Pt': 3}], 
'J90': [{'Ws': 'M3', 'Pt': 3}, {'Ws': 'M2', 'Pt': 1}, {'Ws': 'M1', 'Pt': 2}], 
'J91': [{'Ws': 'M2', 'Pt': 6}, {'Ws': 'M1', 'Pt': 3}, {'Ws': 'M3', 'Pt': 4}], 
'J92': [{'Ws': 'M2', 'Pt': 4}, {'Ws': 'M1', 'Pt': 5}, {'Ws': 'M3', 'Pt': 8}], 
'J93': [{'Ws': 'M1', 'Pt': 7}, {'Ws': 'M2', 'Pt': 7}, {'Ws': 'M3', 'Pt': 5}], 
'J94': [{'Ws': 'M2', 'Pt': 6}, {'Ws': 'M1', 'Pt': 8}, {'Ws': 'M3', 'Pt': 3}], 
'J95': [{'Ws': 'M1', 'Pt': 6}, {'Ws': 'M3', 'Pt': 4}, {'Ws': 'M2', 'Pt': 3}], 
'J96': [{'Ws': 'M1', 'Pt': 1}, {'Ws': 'M2', 'Pt': 8}, {'Ws': 'M3', 'Pt': 5}], 
'J97': [{'Ws': 'M1', 'Pt': 3}, {'Ws': 'M2', 'Pt': 8}, {'Ws': 'M3', 'Pt': 4}], 
'J98': [{'Ws': 'M3', 'Pt': 5}, {'Ws': 'M2', 'Pt': 7}, {'Ws': 'M1', 'Pt': 5}], 
'J99': [{'Ws': 'M1', 'Pt': 4}, {'Ws': 'M2', 'Pt': 7}, {'Ws': 'M3', 'Pt': 3}], 
'J100': [{'Ws': 'M2', 'Pt': 2}, {'Ws': 'M3', 'Pt': 4}, {'Ws': 'M1', 'Pt': 2}], 
# 'J101': [{'Ws': 'M2', 'Pt': 1}, {'Ws': 'M3', 'Pt': 3}, {'Ws': 'M1', 'Pt': 8}], 
# 'J102': [{'Ws': 'M1', 'Pt': 8}, {'Ws': 'M2', 'Pt': 5}, {'Ws': 'M3', 'Pt': 7}], 
# 'J103': [{'Ws': 'M2', 'Pt': 4}, {'Ws': 'M1', 'Pt': 3}, {'Ws': 'M3', 'Pt': 8}], 
# 'J104': [{'Ws': 'M2', 'Pt': 2}, {'Ws': 'M3', 'Pt': 6}, {'Ws': 'M1', 'Pt': 6}], 
# 'J105': [{'Ws': 'M3', 'Pt': 3}, {'Ws': 'M1', 'Pt': 6}, {'Ws': 'M2', 'Pt': 3}], 
# 'J106': [{'Ws': 'M2', 'Pt': 1}, {'Ws': 'M1', 'Pt': 3}, {'Ws': 'M3', 'Pt': 7}], 
# 'J107': [{'Ws': 'M2', 'Pt': 6}, {'Ws': 'M3', 'Pt': 4}, {'Ws': 'M1', 'Pt': 5}], 
# 'J108': [{'Ws': 'M1', 'Pt': 8}, {'Ws': 'M2', 'Pt': 7}, {'Ws': 'M3', 'Pt': 6}], 
# 'J109': [{'Ws': 'M3', 'Pt': 1}, {'Ws': 'M2', 'Pt': 1}, {'Ws': 'M1', 'Pt': 7}], 
# 'J110': [{'Ws': 'M1', 'Pt': 7}, {'Ws': 'M3', 'Pt': 5}, {'Ws': 'M2', 'Pt': 7}], 
# 'J111': [{'Ws': 'M3', 'Pt': 6}, {'Ws': 'M2', 'Pt': 8}, {'Ws': 'M1', 'Pt': 6}], 
# 'J112': [{'Ws': 'M1', 'Pt': 2}, {'Ws': 'M3', 'Pt': 1}, {'Ws': 'M2', 'Pt': 2}], 
# 'J113': [{'Ws': 'M1', 'Pt': 3}, {'Ws': 'M3', 'Pt': 7}, {'Ws': 'M2', 'Pt': 3}], 
# 'J114': [{'Ws': 'M3', 'Pt': 4}, {'Ws': 'M2', 'Pt': 1}, {'Ws': 'M1', 'Pt': 3}], 
# 'J115': [{'Ws': 'M2', 'Pt': 4}, {'Ws': 'M1', 'Pt': 4}, {'Ws': 'M3', 'Pt': 2}], 
# 'J116': [{'Ws': 'M1', 'Pt': 7}, {'Ws': 'M3', 'Pt': 8}, {'Ws': 'M2', 'Pt': 3}], 
# 'J117': [{'Ws': 'M3', 'Pt': 1}, {'Ws': 'M2', 'Pt': 4}, {'Ws': 'M1', 'Pt': 3}], 
# 'J118': [{'Ws': 'M2', 'Pt': 7}, {'Ws': 'M3', 'Pt': 2}, {'Ws': 'M1', 'Pt': 5}], 
# 'J119': [{'Ws': 'M2', 'Pt': 2}, {'Ws': 'M3', 'Pt': 3}, {'Ws': 'M1', 'Pt': 4}], 
# 'J120': [{'Ws': 'M1', 'Pt': 2}, {'Ws': 'M2', 'Pt': 3}, {'Ws': 'M3', 'Pt': 8}], 
# 'J121': [{'Ws': 'M1', 'Pt': 6}, {'Ws': 'M2', 'Pt': 4}, {'Ws': 'M3', 'Pt': 5}], 
# 'J122': [{'Ws': 'M2', 'Pt': 5}, {'Ws': 'M1', 'Pt': 2}, {'Ws': 'M3', 'Pt': 1}], 
# 'J123': [{'Ws': 'M2', 'Pt': 3}, {'Ws': 'M1', 'Pt': 3}, {'Ws': 'M3', 'Pt': 8}], 
# 'J124': [{'Ws': 'M2', 'Pt': 2}, {'Ws': 'M1', 'Pt': 6}, {'Ws': 'M3', 'Pt': 6}], 
# 'J125': [{'Ws': 'M3', 'Pt': 2}, {'Ws': 'M2', 'Pt': 4}, {'Ws': 'M1', 'Pt': 1}], 
# 'J126': [{'Ws': 'M3', 'Pt': 1}, {'Ws': 'M2', 'Pt': 3}, {'Ws': 'M1', 'Pt': 5}], 
# 'J127': [{'Ws': 'M3', 'Pt': 5}, {'Ws': 'M2', 'Pt': 2}, {'Ws': 'M1', 'Pt': 7}], 
# 'J128': [{'Ws': 'M3', 'Pt': 4}, {'Ws': 'M1', 'Pt': 1}, {'Ws': 'M2', 'Pt': 5}], 
# 'J129': [{'Ws': 'M1', 'Pt': 3}, {'Ws': 'M2', 'Pt': 2}, {'Ws': 'M3', 'Pt': 4}], 
# 'J130': [{'Ws': 'M1', 'Pt': 7}, {'Ws': 'M2', 'Pt': 8}, {'Ws': 'M3', 'Pt': 6}], 
# 'J131': [{'Ws': 'M3', 'Pt': 3}, {'Ws': 'M2', 'Pt': 8}, {'Ws': 'M1', 'Pt': 8}], 
# 'J132': [{'Ws': 'M3', 'Pt': 4}, {'Ws': 'M2', 'Pt': 6}, {'Ws': 'M1', 'Pt': 8}], 
# 'J133': [{'Ws': 'M3', 'Pt': 3}, {'Ws': 'M1', 'Pt': 8}, {'Ws': 'M2', 'Pt': 5}], 
# 'J134': [{'Ws': 'M2', 'Pt': 7}, {'Ws': 'M3', 'Pt': 4}, {'Ws': 'M1', 'Pt': 3}], 
# 'J135': [{'Ws': 'M3', 'Pt': 1}, {'Ws': 'M2', 'Pt': 7}, {'Ws': 'M1', 'Pt': 2}], 
# 'J136': [{'Ws': 'M3', 'Pt': 7}, {'Ws': 'M2', 'Pt': 5}, {'Ws': 'M1', 'Pt': 1}], 
# 'J137': [{'Ws': 'M1', 'Pt': 4}, {'Ws': 'M3', 'Pt': 6}, {'Ws': 'M2', 'Pt': 7}], 
# 'J138': [{'Ws': 'M2', 'Pt': 5}, {'Ws': 'M1', 'Pt': 4}, {'Ws': 'M3', 'Pt': 4}], 
# 'J139': [{'Ws': 'M1', 'Pt': 3}, {'Ws': 'M3', 'Pt': 4}, {'Ws': 'M2', 'Pt': 2}], 
# 'J140': [{'Ws': 'M1', 'Pt': 3}, {'Ws': 'M3', 'Pt': 5}, {'Ws': 'M2', 'Pt': 2}], 
# 'J141': [{'Ws': 'M2', 'Pt': 6}, {'Ws': 'M3', 'Pt': 8}, {'Ws': 'M1', 'Pt': 8}], 
# 'J142': [{'Ws': 'M1', 'Pt': 2}, {'Ws': 'M3', 'Pt': 2}, {'Ws': 'M2', 'Pt': 4}], 
# 'J143': [{'Ws': 'M2', 'Pt': 3}, {'Ws': 'M1', 'Pt': 8}, {'Ws': 'M3', 'Pt': 7}], 
# 'J144': [{'Ws': 'M2', 'Pt': 6}, {'Ws': 'M1', 'Pt': 5}, {'Ws': 'M3', 'Pt': 3}], 
# 'J145': [{'Ws': 'M2', 'Pt': 3}, {'Ws': 'M3', 'Pt': 2}, {'Ws': 'M1', 'Pt': 4}], 
# 'J146': [{'Ws': 'M1', 'Pt': 1}, {'Ws': 'M3', 'Pt': 2}, {'Ws': 'M2', 'Pt': 1}], 
# 'J147': [{'Ws': 'M3', 'Pt': 2}, {'Ws': 'M1', 'Pt': 7}, {'Ws': 'M2', 'Pt': 2}], 
# 'J148': [{'Ws': 'M2', 'Pt': 1}, {'Ws': 'M1', 'Pt': 4}, {'Ws': 'M3', 'Pt': 1}], 
# 'J149': [{'Ws': 'M2', 'Pt': 7}, {'Ws': 'M1', 'Pt': 3}, {'Ws': 'M3', 'Pt': 2}], 
# 'J150': [{'Ws': 'M2', 'Pt': 1}, {'Ws': 'M1', 'Pt': 7}, {'Ws': 'M3', 'Pt': 6}], 
# 'J151': [{'Ws': 'M3', 'Pt': 6}, {'Ws': 'M1', 'Pt': 8}, {'Ws': 'M2', 'Pt': 5}], 
# 'J152': [{'Ws': 'M1', 'Pt': 8}, {'Ws': 'M2', 'Pt': 8}, {'Ws': 'M3', 'Pt': 8}], 
# 'J153': [{'Ws': 'M2', 'Pt': 8}, {'Ws': 'M1', 'Pt': 7}, {'Ws': 'M3', 'Pt': 1}], 
# 'J154': [{'Ws': 'M2', 'Pt': 4}, {'Ws': 'M3', 'Pt': 7}, {'Ws': 'M1', 'Pt': 7}], 
# 'J155': [{'Ws': 'M2', 'Pt': 2}, {'Ws': 'M3', 'Pt': 1}, {'Ws': 'M1', 'Pt': 5}], 
# 'J156': [{'Ws': 'M3', 'Pt': 8}, {'Ws': 'M1', 'Pt': 7}, {'Ws': 'M2', 'Pt': 2}], 
# 'J157': [{'Ws': 'M1', 'Pt': 3}, {'Ws': 'M3', 'Pt': 2}, {'Ws': 'M2', 'Pt': 8}], 
# 'J158': [{'Ws': 'M1', 'Pt': 1}, {'Ws': 'M2', 'Pt': 6}, {'Ws': 'M3', 'Pt': 4}], 
# 'J159': [{'Ws': 'M2', 'Pt': 4}, {'Ws': 'M1', 'Pt': 8}, {'Ws': 'M3', 'Pt': 7}], 
# 'J160': [{'Ws': 'M3', 'Pt': 5}, {'Ws': 'M1', 'Pt': 4}, {'Ws': 'M2', 'Pt': 7}], 
# 'J161': [{'Ws': 'M1', 'Pt': 4}, {'Ws': 'M3', 'Pt': 6}, {'Ws': 'M2', 'Pt': 1}], 
# 'J162': [{'Ws': 'M2', 'Pt': 6}, {'Ws': 'M3', 'Pt': 7}, {'Ws': 'M1', 'Pt': 3}], 
# 'J163': [{'Ws': 'M2', 'Pt': 7}, {'Ws': 'M3', 'Pt': 3}, {'Ws': 'M1', 'Pt': 2}], 
# 'J164': [{'Ws': 'M1', 'Pt': 2}, {'Ws': 'M3', 'Pt': 4}, {'Ws': 'M2', 'Pt': 4}], 
# 'J165': [{'Ws': 'M2', 'Pt': 6}, {'Ws': 'M3', 'Pt': 3}, {'Ws': 'M1', 'Pt': 1}], 
# 'J166': [{'Ws': 'M2', 'Pt': 3}, {'Ws': 'M1', 'Pt': 4}, {'Ws': 'M3', 'Pt': 4}], 
# 'J167': [{'Ws': 'M3', 'Pt': 1}, {'Ws': 'M2', 'Pt': 2}, {'Ws': 'M1', 'Pt': 3}], 
# 'J168': [{'Ws': 'M1', 'Pt': 7}, {'Ws': 'M2', 'Pt': 4}, {'Ws': 'M3', 'Pt': 5}], 
# 'J169': [{'Ws': 'M3', 'Pt': 1}, {'Ws': 'M2', 'Pt': 4}, {'Ws': 'M1', 'Pt': 6}], 
# 'J170': [{'Ws': 'M1', 'Pt': 7}, {'Ws': 'M3', 'Pt': 5}, {'Ws': 'M2', 'Pt': 2}], 
# 'J171': [{'Ws': 'M1', 'Pt': 7}, {'Ws': 'M2', 'Pt': 7}, {'Ws': 'M3', 'Pt': 6}], 
# 'J172': [{'Ws': 'M2', 'Pt': 2}, {'Ws': 'M3', 'Pt': 4}, {'Ws': 'M1', 'Pt': 1}], 
# 'J173': [{'Ws': 'M3', 'Pt': 2}, {'Ws': 'M1', 'Pt': 4}, {'Ws': 'M2', 'Pt': 5}], 
# 'J174': [{'Ws': 'M2', 'Pt': 5}, {'Ws': 'M1', 'Pt': 2}, {'Ws': 'M3', 'Pt': 2}], 
# 'J175': [{'Ws': 'M1', 'Pt': 8}, {'Ws': 'M2', 'Pt': 1}, {'Ws': 'M3', 'Pt': 8}], 
# 'J176': [{'Ws': 'M1', 'Pt': 2}, {'Ws': 'M2', 'Pt': 8}, {'Ws': 'M3', 'Pt': 6}], 
# 'J177': [{'Ws': 'M2', 'Pt': 8}, {'Ws': 'M1', 'Pt': 7}, {'Ws': 'M3', 'Pt': 1}], 
# 'J178': [{'Ws': 'M2', 'Pt': 6}, {'Ws': 'M3', 'Pt': 8}, {'Ws': 'M1', 'Pt': 1}], 
# 'J179': [{'Ws': 'M2', 'Pt': 7}, {'Ws': 'M1', 'Pt': 8}, {'Ws': 'M3', 'Pt': 6}], 
# 'J180': [{'Ws': 'M1', 'Pt': 7}, {'Ws': 'M3', 'Pt': 2}, {'Ws': 'M2', 'Pt': 2}], 
# 'J181': [{'Ws': 'M1', 'Pt': 8}, {'Ws': 'M2', 'Pt': 5}, {'Ws': 'M3', 'Pt': 4}], 
# 'J182': [{'Ws': 'M1', 'Pt': 4}, {'Ws': 'M3', 'Pt': 1}, {'Ws': 'M2', 'Pt': 7}], 
# 'J183': [{'Ws': 'M2', 'Pt': 4}, {'Ws': 'M3', 'Pt': 7}, {'Ws': 'M1', 'Pt': 7}], 
# 'J184': [{'Ws': 'M1', 'Pt': 1}, {'Ws': 'M3', 'Pt': 6}, {'Ws': 'M2', 'Pt': 3}], 
# 'J185': [{'Ws': 'M2', 'Pt': 2}, {'Ws': 'M3', 'Pt': 4}, {'Ws': 'M1', 'Pt': 4}], 
# 'J186': [{'Ws': 'M3', 'Pt': 7}, {'Ws': 'M1', 'Pt': 5}, {'Ws': 'M2', 'Pt': 4}], 
# 'J187': [{'Ws': 'M3', 'Pt': 7}, {'Ws': 'M2', 'Pt': 1}, {'Ws': 'M1', 'Pt': 3}], 
# 'J188': [{'Ws': 'M2', 'Pt': 4}, {'Ws': 'M1', 'Pt': 7}, {'Ws': 'M3', 'Pt': 6}], 
# 'J189': [{'Ws': 'M2', 'Pt': 5}, {'Ws': 'M1', 'Pt': 3}, {'Ws': 'M3', 'Pt': 5}], 
# 'J190': [{'Ws': 'M2', 'Pt': 6}, {'Ws': 'M1', 'Pt': 2}, {'Ws': 'M3', 'Pt': 4}], 
# 'J191': [{'Ws': 'M1', 'Pt': 8}, {'Ws': 'M3', 'Pt': 8}, {'Ws': 'M2', 'Pt': 5}], 
# 'J192': [{'Ws': 'M3', 'Pt': 6}, {'Ws': 'M1', 'Pt': 3}, {'Ws': 'M2', 'Pt': 6}], 
# 'J193': [{'Ws': 'M3', 'Pt': 4}, {'Ws': 'M2', 'Pt': 6}, {'Ws': 'M1', 'Pt': 3}], 
# 'J194': [{'Ws': 'M1', 'Pt': 5}, {'Ws': 'M3', 'Pt': 5}, {'Ws': 'M2', 'Pt': 2}], 
# 'J195': [{'Ws': 'M3', 'Pt': 4}, {'Ws': 'M2', 'Pt': 2}, {'Ws': 'M1', 'Pt': 7}], 
# 'J196': [{'Ws': 'M1', 'Pt': 8}, {'Ws': 'M2', 'Pt': 5}, {'Ws': 'M3', 'Pt': 2}], 
# 'J197': [{'Ws': 'M1', 'Pt': 7}, {'Ws': 'M2', 'Pt': 1}, {'Ws': 'M3', 'Pt': 5}], 
# 'J198': [{'Ws': 'M2', 'Pt': 7}, {'Ws': 'M3', 'Pt': 8}, {'Ws': 'M1', 'Pt': 7}], 
# 'J199': [{'Ws': 'M2', 'Pt': 3}, {'Ws': 'M1', 'Pt': 1}, {'Ws': 'M3', 'Pt': 4}], 
# 'J200': [{'Ws': 'M2', 'Pt': 2}, {'Ws': 'M1', 'Pt': 2}, {'Ws': 'M3', 'Pt': 4}]
}
machines = ['M1', 'M2', 'M3']
num_jobs = 100  # Reduced for testing

print("Jobs générés:")
for job_id, tasks in jobs.items():
    print(f"{job_id}: {tasks}")
print(jobs)
print("\n--- Fin de la génération des jobs ---\n")
 
# -----------------------------------------------------------------
# 2) Paramètres du problème
# -----------------------------------------------------------------
operators = ['K1', 'K2', 'K3']
T =  400  # Adjusted time horizon
speed = {
    'K1': {'M1': 1.2, 'M2': 1.0, 'M3': 0.8},
    'K2': {'M1': 1.0, 'M2': 1.5, 'M3': 1.0},
    'K3': {'M1': 0.9, 'M2': 0.9, 'M3': 1.2}
}
 
# -----------------------------------------------------------------
# 3) Pré-calcul du temps effectif
# -----------------------------------------------------------------
myProcTime = {}
for j in jobs:
    for o, op_data in enumerate(jobs[j]):
        machine = op_data['Ws']
        pt = op_data['Pt']
        for k in operators:
            myProcTime[(j, o, k)] = math.ceil(pt / speed[k][machine])
 
# -----------------------------------------------------------------
# 4) Création du modèle Gurobi
# -----------------------------------------------------------------
model = gp.Model("JobShopScheduling")
# model.setParam('MIPGap', 0.07)
# model.setParam("Accelerator", "GPU")

# -----------------------------------------------------------------
# 5) Variables de décision
# -----------------------------------------------------------------
S = model.addVars([(j, o) for j in jobs for o in range(len(jobs[j]))], vtype=GRB.CONTINUOUS, name="S")
C = model.addVars([(j, o) for j in jobs for o in range(len(jobs[j]))], vtype=GRB.CONTINUOUS, name="C")
x = model.addVars(operators, machines, vtype=GRB.BINARY, name="x")
y = model.addVars(jobs.keys(), vtype=GRB.BINARY, name="y")
BigM = T * 2
 
# -----------------------------------------------------------------
# 6) Contraintes (corrected)
# -----------------------------------------------------------------
# 6.1 Affectation opérateurs -> machines
model.addConstrs((x.sum('*', m) == 1 for m in machines), "MachineOperator")
model.addConstrs((x.sum(k, '*') <= 1 for k in operators), "OperatorLimit")
 
# 6.2 Lien entre S, C et temps effectif (contrainte modifiée)
for j in jobs:
    for o in range(len(jobs[j])):
        machine = jobs[j][o]['Ws']
        expr_time = gp.quicksum(myProcTime[(j, o, k)] * x[k, machine] for k in operators)
        # Contrainte modifiée : 
        # Si y[j] = 1, on a C[j, o] >= S[j, o] + expr_time.
        # Si y[j] = 0, le terme -BigM*(1-y[j]) = -BigM "désactive" la contrainte 
        # (BigM étant choisi suffisamment grand pour rendre la contrainte non contraignante).
        model.addConstr(
            C[j, o] >= S[j, o] + expr_time - BigM*(1 - y[j]),
            f"process_{j}_{o}"
        )
 
# 6.3 Activation du job
for j in jobs:
    for o in range(len(jobs[j])):
        model.addConstr(S[j, o] <= T * y[j], f"start_act_{j}_{o}")
        model.addConstr(C[j, o] <= T * y[j], f"comp_act_{j}_{o}")
 
# 6.4 Précédence des opérations
for j in jobs:
    for o in range(len(jobs[j]) - 1):
        model.addConstr(S[j, o+1] >= C[j, o] - BigM * (1 - y[j]), f"precedence_{j}_{o}")
 
# 6.5 Contraintes disjonctives
machine_ops = {m: [] for m in machines}
for j in jobs:
    for o in range(len(jobs[j])):
        machine_ops[jobs[j][o]['Ws']].append((j, o))
 
for m in machines:
    ops = machine_ops[m]
    for (j1, o1), (j2, o2) in itertools.combinations(ops, 2):
        z = model.addVar(vtype=GRB.BINARY, name=f"z_{j1}_{o1}_{j2}_{o2}")
        model.addConstr(S[j1, o1] >= C[j2, o2] - BigM*(1 - z) - BigM*(2 - y[j1] - y[j2]))
        model.addConstr(S[j2, o2] >= C[j1, o1] - BigM*z - BigM*(2 - y[j1] - y[j2]))
 
# 6.6 Délai final
for j in jobs:
    last_op = len(jobs[j]) - 1
    model.addConstr(C[j, last_op] <= T, f"deadline_{j}")
 

 
# -----------------------------------------------------------------
# 7) Fonction Objectif
# -----------------------------------------------------------------
model.setObjective( gp.quicksum(y[j] for j in jobs) , GRB.MAXIMIZE)
 
# -----------------------------------------------------------------
# 8) Résolution
# -----------------------------------------------------------------
import time
start_time = time.time()
model.optimize()
end_time = time.time()
exec_time = end_time - start_time
# -----------------------------------------------------------------
# 9) Extraction du planning
# -----------------------------------------------------------------
gantt_data = []
if model.status == GRB.OPTIMAL:
    for m in machines:
        assigned_op = next((k for k in operators if x[k, m].X > 0.5), None)
        machine_label = f"{m} ({assigned_op})" if assigned_op else m
        for (j, o) in machine_ops[m]:
            if y[j].X > 0.5:
                start_t = S[j, o].X
                end_t = C[j, o].X
                if end_t > start_t:
                    gantt_data.append({
                        'Job': j,
                        'Operation': f"Op{o}",
                        'Ws': machine_label,
                        'Start': start_t,
                        'Finish': end_t
                    })
 
# -----------------------------------------------------------------
# 10) Diagramme de Gantt corrigé
# -----------------------------------------------------------------
if gantt_data:
       
       # Converting to individual task variables
       Tâches    = [item['Job'] for item in gantt_data]         # Task names taken from 'Job'
       d         = [item['Start'] for item in gantt_data]         # Starting times
       f         = [item['Finish'] for item in gantt_data]        # Finishing times
       Ressource = [item['Ws'] for item in gantt_data]            # Resources (workstations)
       pt        = [item['Finish'] - item['Start'] for item in gantt_data]  # Duration for each task
       title     = "Test Bar Timeline"
 
       # Build the list of dictionaries
       data_list = []
       for t, start, end, res, time in zip(Tâches, d, f, Ressource, pt):
              data_list.append({
                     "Tâches": t,
                     "Début": start,
                     "Fin": end,
                     "Ressource": res,
                     "Aj": start,  # Using the start as the base position for the bar
                     "Pt": time,
                     "Cj": end,    # This could be used for further customization if needed
                     "Time": time
              })
 
       # Create DataFrame
       df = pd.DataFrame(data_list)
 
       # Create a horizontal bar chart
       fig = px.bar(
       df,
       base="Aj",        # Base start value for each bar
       x="Time",         # Width of the bar
       y="Ressource",    # Categories on the y-axis
       text="Tâches",    # Task names displayed on the bars
       color="Tâches",   # Color bars based on tasks
       orientation='h',  # Horizontal orientation
       title=title
       )
 
       # Reverse the y-axis to have the first task at the top
       fig.update_yaxes(autorange="reversed")
       fig.show()
       # Convert the Plotly figure to an HTML string (without full HTML wrapper)
       plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
 
       # Create an HTML document with a larger, centered refresh button
       html_content = f"""
       <html>
       <head>
       <title>{title}</title>
       <meta charset="UTF-8">
       <style>
              .refresh-button {{
              display: block;
              margin: 20px auto;
              padding: 15px 30px;
              font-size: 20px;
              cursor: pointer;
              }}
       </style>
       </head>
       <body>
       <!-- Refresh button to reload the page -->
       <button class="refresh-button" onclick="window.location.reload();">
              Refresh Page
       </button>
       {plot_html}
       </body>
       </html>
       """
 
       # Write the HTML content to a file
       with open("gantt_chart.html", "w", encoding="utf-8") as file:
              file.write(html_content)
 
       print("HTML file 'gantt_chart.html' has been created.")
 
else:
    print("No operations to plot.")
 
# -----------------------------------------------------------------
# 11) Résultats
# -----------------------------------------------------------------
if model.status == GRB.OPTIMAL:
    print(f"\nJobs réalisés: {sum(y[j].X for j in jobs)}/{num_jobs}")
    print("\nAssignations opérateurs-machines:")
    for m in machines:
        for k in operators:
            if x[k, m].X > 0.5:
                print(f"{m} → {k}")
    print("exec_time : ",exec_time)
else:
    print("No optimal solution found")